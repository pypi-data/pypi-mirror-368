"""varseek sim and specific helper functions."""

import logging
import os
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

import varseek
from varseek.varseek_build import accepted_build_file_types

from .constants import supported_databases_and_corresponding_reference_sequence_type
from .utils import (
    check_file_path_is_string_with_valid_extension,
    fasta_to_fastq,
    introduce_sequencing_errors,
    is_valid_int,
    make_function_parameter_to_value_dict,
    merge_synthetic_read_info_into_variants_metadata_df,
    get_varseek_dry_run,
    report_time_elapsed,
    reverse_complement,
    save_params_to_config_file,
    save_run_info,
    set_up_logger,
    splitext_custom,
    set_varseek_logging_level_and_filehandler
)

tqdm.pandas()
logger = logging.getLogger(__name__)
logger = set_up_logger(logger, logging_level="INFO", save_logs=False, log_dir=None)


def assign_strands(read_start_indices_mutant, strand, seed=None):
    if strand in ("f", "r"):
        return [(idx, strand) for idx in read_start_indices_mutant]
    elif strand == "random":
        if seed:
            random.seed(seed)
        return [(idx, random.choice(["f", "r"])) for idx in read_start_indices_mutant]
    elif strand == "both":
        half = len(read_start_indices_mutant) // 2
        return [(idx, "f") for idx in read_start_indices_mutant[:half]] + [(idx, "r") for idx in read_start_indices_mutant[half:]]
    else:
        raise ValueError("strand must be 'f', 'r', 'random', or 'both'")


def validate_input_sim(params_dict):
    variants = params_dict["variants"]
    sequences = params_dict["sequences"]

    if isinstance(variants, (str, Path)):
        if variants in supported_databases_and_corresponding_reference_sequence_type:
            if sequences not in supported_databases_and_corresponding_reference_sequence_type[variants]["sequence_download_commands"]:
                raise ValueError(f"sequences {sequences} not internally supported.\nTo see a list of supported variant databases and reference genomes, please use the 'list_internally_supported_indices' flag/argument.")
            elif os.path.isfile(variants) and variants.endswith(accepted_build_file_types):  # a path to a variant database with a valid extension
                pass
            else:
                raise ValueError(f"variants must be a df, a path to a variant database, or a string specifying a variant database supported by varseek. Got {type(variants)}.\nTo see a list of supported variant databases and reference genomes, please use the 'list_internally_supported_indices' flag/argument.")
    elif isinstance(variants, pd.DataFrame):
        pass
    else:
        raise ValueError(f"variants must be a df, a path to a variant database, or a string specifying a variant database supported by varseek. Got {type(variants)}.\nTo see a list of supported variant databases and reference genomes, please use the 'list_internally_supported_indices' flag/argument.")

    # integers - optional just means that it's in kwargs
    for param_name, min_value, optional_value in [
        ("w", 1, False),
        ("k", 1, False),
        ("number_of_variants_to_sample", 1, False),
        ("seed", 0, True),
    ]:
        param_value = params_dict.get(param_name)
        if not is_valid_int(param_value, ">=", min_value, optional=optional_value):
            raise ValueError(f"{param_name} must be an integer >= {min_value}. Got {params_dict.get(param_name)}.")

    number_of_reads_per_variant_alt = params_dict["number_of_reads_per_variant_alt"]
    if not (is_valid_int(number_of_reads_per_variant_alt, ">=", 0) or number_of_reads_per_variant_alt == "all"):
        raise ValueError(f"number_of_reads_per_variant_alt must be an integer >= 0 or 'all'. Got {number_of_reads_per_variant_alt}.")

    number_of_reads_per_variant_ref = params_dict["number_of_reads_per_variant_ref"]
    if not (is_valid_int(number_of_reads_per_variant_ref, ">=", 0) or number_of_reads_per_variant_ref == "all"):
        raise ValueError(f"number_of_reads_per_variant_ref must be an integer >= 0 or 'all'. Got {number_of_reads_per_variant_ref}.")

    if number_of_reads_per_variant_alt == 0 and number_of_reads_per_variant_ref == 0:
        raise ValueError("number_of_reads_per_variant_alt and number_of_reads_per_variant_ref cannot both be 0.")

    if params_dict["sample_ref_and_alt_reads_from_same_locations"] is True:
        if number_of_reads_per_variant_alt != number_of_reads_per_variant_ref:
            raise ValueError("When sample_ref_and_alt_reads_from_same_locations is True, number_of_reads_per_variant_alt must be equal to number_of_reads_per_variant_ref")

    if params_dict["strand"] not in ["f", "r", "both", "random", None]:
        raise ValueError("strand must be 'f', 'r', 'both', 'random', or None.")

    if not (0 <= params_dict["error_rate"] <= 1):
        raise ValueError("error_rate must be between 0 and 1.")

    # check if the values in error_distribution sum to 1 and are each non-negative
    if not (sum(params_dict["error_distribution"]) == 1):
        raise ValueError("error_distribution must sum to 1.")
    for value in params_dict["error_distribution"]:
        if value < 0:
            raise ValueError("error_distribution must be non-negative.")

    # check if max_errors is a positive integer or float
    if not (is_valid_int(params_dict["max_errors"], ">=", 0) or isinstance(params_dict["max_errors"], float)):
        raise ValueError("max_errors must be a positive integer or float.")

    for param_name, file_type in {"reads_fastq_parent": "fastq", "reads_csv_parent": "csv", "variants_updated_csv_out": ["csv", "tsv"], "reads_fastq_out": "fastq", "reads_csv_out": "csv", "wt_vcrs_fasta_out": "fasta", "wt_vcrs_t2g_out": "t2g", "removed_variants_text_out": "txt", "gtf": "gtf"}.items():
        check_file_path_is_string_with_valid_extension(params_dict.get(param_name), param_name, file_type)

    # Boolean
    for param_name in [
        "sample_ref_and_alt_reads_from_same_locations",
        "with_replacement",
        "add_noise_sequencing_error",
        "add_noise_base_quality",
        "save_reads_csv",
        "save_variants_updated_csv",
        "gzip_reads_fastq_out",
        "dry_run",
    ]:
        if not isinstance(params_dict.get(param_name), bool):
            raise ValueError(f"{param_name} must be a boolean. Got {param_name} of type {type(params_dict.get(param_name))}.")

@report_time_elapsed
def sim(
    variants,
    number_of_variants_to_sample=1500,
    number_of_reads_per_variant_alt="all",
    number_of_reads_per_variant_ref="all",
    sample_ref_and_alt_reads_from_same_locations=False,
    with_replacement=False,
    strand=None,
    read_length=150,
    filters=None,
    add_noise_sequencing_error=False,
    add_noise_base_quality=False,
    error_rate=0.0001,
    error_distribution=(0.85, 0.1, 0.05),  # sub, del, ins
    max_errors=float("inf"),
    variant_sequence_read_parent_column="mutant_sequence_read_parent",
    ref_sequence_read_parent_column="wt_sequence_read_parent",
    variant_sequence_read_parent_rc_column="mutant_sequence_read_parent_rc",
    ref_sequence_read_parent_rc_column="wt_sequence_read_parent_rc",
    reads_fastq_parent=None,
    reads_csv_parent=None,
    out=".",
    reads_fastq_out=None,
    variants_updated_csv_out=None,
    reads_csv_out=None,
    save_variants_updated_csv=True,
    save_reads_csv=True,
    vk_build_out_dir=None,
    sequences=None,
    seq_id_column="seq_ID",
    var_column="mutation",
    var_id_column="header",
    variant_type_column = "vcrs_variant_type",
    k=59,
    w=54,
    sequences_cdna=None,
    seq_id_column_cdna="seq_ID",
    var_column_cdna="mutation",
    sequences_genome=None,
    seq_id_column_genome="chromosome",
    var_column_genome="mutation_genome",
    seed=None,
    gzip_reads_fastq_out=False,
    dry_run=False,
    logging_level=None,
    save_logs=False,
    log_out_dir=None,
    **kwargs,
):
    """
    Create synthetic RNA-seq dataset with variant-containing reads.

    # Required input arguments:
    - variants                         (str or pd.DataFrame) Path to the csv file or a dataframe object containing variant information.
        Valid input files include the variants_updated_csv_out file from vk build (save_variants_updated_csv=True) with merge_identical=False, or the variants_updated_exploded_vk_info_csv_out output of vk info (save_variants_updated_exploded_vk_info_csv=True).
        Expects the following columns:
            header: variant header/ID
            variant_sequence_read_parent_column: the parent variant-containing sequence from which to draw the read - should correspond to roughly twice the read length (so that the variant can occur in any position in the read) - required if and only if number_of_reads_per_variant_alt > 0
            ref_sequence_read_parent_column: the parent non-variant containing sequence from which to draw the read - should correspond to roughly twice the read length (so that the position where the variant normally appears can occur in any position in the read) - required if and only if number_of_reads_per_variant_ref > 0
            variant_sequence_read_parent_rc_column: the reverse complement of the parent variant-containing sequence from which to draw the read - optional (generated if not present)
            ref_sequence_read_parent_rc_column: the reverse complement of the parent non-variant containing sequence from which to draw the read - optional (generated if not present)

    # Optional input arguments:
    - number_of_variants_to_sample     (int) Number of variants to sample from `variants`, or 'all' for all variants. Default: 1500
    - number_of_reads_per_variant_alt    (int or str) Number of variant-containing reads to simulate per variant. Either accepts an integer greater than 0 or "all" to simulate all possible reads per variant. Default: "all"
    - number_of_reads_per_variant_ref    (int or str) Number of non-variant-containing reads to simulate per variant. Either accepts an integer greater than 0 or "all" to simulate all possible reads per variant. Default: "all"
    - sample_ref_and_alt_reads_from_same_locations (bool) Whether to sample variant-containing and non-variant-containing reads from the same locations. Requires number_of_reads_per_variant_alt and number_of_reads_per_variant_ref to be the same. Default: False
    - with_replacement                  (bool) Whether to sample with replacement. Default: False
    - strand                            (str) Strand to simulate reads from. Possible values: 'f' (forward strand), 'r' (reverse complement strand), 'both' (both strands equally), 'random' (select a strand at random for each read), or None (select a strand at random for all reads derived from each variant). Default: None
    - read_length                       (int) Length of the reads to simulate. Default: 150
    - filters                           (list) List of filters to apply to the variant metadata dataframe. Default: None
    - add_noise_sequencing_error        (bool) Whether to add noise to the reads. Default: False
    - add_noise_base_quality            (bool) Whether to add noise to the base quality scores. Default: False
    - error_rate                        (float) Error rate for sequencing errors. Only applies if add_noise_sequencing_error=True. Default: 0.0001
    - error_distribution                (tuple) Distribution of errors. Default: (0.85, 0.1, 0.05) (sub, del, ins)
    - max_errors                        (int or float) Maximum number of errors to introduce. Default: float("inf") (no cap)
    - variant_sequence_read_parent_column (str) Name of the column containing the parent variant-containing sequence from which to draw the read. Default: "mutant_sequence_read_parent"
    - ref_sequence_read_parent_column    (str) Name of the column containing the parent non-variant containing sequence from which to draw the read. Default: "wt_sequence_read_parent"
    - variant_sequence_read_parent_rc_column (str) Name of the column containing the reverse complement of the parent variant-containing sequence from which to draw the read. Default: "mutant_sequence_read_parent_rc"
    - ref_sequence_read_parent_rc_column (str) Name of the column containing the reverse complement of the parent non-variant containing sequence from which to draw the read. Default: "wt_sequence_read_parent_rc"
    - reads_fastq_parent                (str) Path to the parent fastq on which the output will be concatenated. Good when chaining multiple runs. Default: None
    - reads_csv_parent                  (str) Path to the parent csv on which the output will be concatenated. Good when chaining multiple runs. Default: None
    - out                               (str) Path to the output directory. Default: "."
    - reads_fastq_out                   (str) Path to the output fastq file containing the simulated reads. Default: `out`/synthetic_reads.fq
    - variants_updated_csv_out         (str) Path to the output csv file containing the updated variant metadata dataframe (one row per variant). Default: `out`/variants_updated_synthetic_reads.csv
    - reads_csv_out                     (str) Path to the output csv file containing the simulated reads (one row per read). Default: `out`/synthetic_reads_df.csv
    - save_variants_updated_csv        (bool) Whether to save the updated variant metadata dataframe to a csv file. Default: True
    - save_reads_csv                     (bool) Whether to save the simulated reads to a csv file. Default: True
    - vk_build_out_dir                  (str) Only applies if variants does not exist or have the expected columns. Path to the output directory for the vk_build files. Default: `out`/vk_build.
    - sequences                         (str) Only applies if variants does not exist or have the expected columns. Path to the fasta file containing the sequences. Default: None
    - seq_id_column                     (str) Only applies if variants does not exist or have the expected columns. Name of the column containing the sequence IDs. Default: "seq_ID"
    - var_column                        (str) Only applies if variants does not exist or have the expected columns. Name of the column containing the variants. Default: "mutation"
    - var_id_column                     (str) Only applies if variants does not exist or have the expected columns. Name of the column containing the variant header. Default: "header"
    - variant_type_column               (str) Only applies if variants does not exist or have the expected columns. Name of the column containing the variant type. Default: "vcrs_variant_type"
    - k                                 (int) Only applies if variants does not exist or have the expected columns. Length of the k-mer to use for filtering. Default: 59
    - w                                 (int) Only applies if variants does not exist or have the expected columns. Length of the k-mer to use for filtering. Default: 54
    - sequences_cdna                    (str) Only applies if variants does not exist or have the expected columns. Path to the fasta file containing the cDNA sequences. Default: None
    - seq_id_column_cdna                (str) Only applies if variants does not exist or have the expected columns. Name of the column containing the sequence IDs for cDNA sequences. Default: "seq_ID"
    - var_column_cdna                   (str) Only applies if variants does not exist or have the expected columns. Name of the column containing the variants for cDNA sequences. Default: "mutation"
    - sequences_genome                  (str) Only applies if variants does not exist or have the expected columns. Path to the fasta file containing the genome sequences. Default: None
    - seq_id_column_genome              (str) Only applies if variants does not exist or have the expected columns. Name of the column containing the sequence IDs for genome sequences. Default: "chromosome"
    - var_column_genome                 (str) Only applies if variants does not exist or have the expected columns. Name of the column containing the variants for genome sequences. Default: "mutation_genome"
    - seed                              (int) Seed for random number generation. Default: None
    - gzip_reads_fastq_out              (bool) Whether to gzip the output fastq file. Default: False
    - dry_run                           (bool) Whether to run in dry-run mode. Default: False
    - logging_level                     (str) Logging level. Can also be set with the environment variable VARSEEK_LOGGING_LEVEL. Default: INFO.
    - save_logs                         (True/False) Whether to save logs to a file. Default: False.
    - log_out_dir                       (str) Directory to save logs. Default: None (do not save logs).

    # Hidden arguments
    - make_internal_copies              (bool) Whether to make internal copies of the input dataframes. Default: True
    - filter_null_rows_from_important_cols  (bool) Whether to filter out rows with null values in important columns. Default: True
    - make_dataframes                   (bool) Whether to make dataframes. Turn off when only wanting to make the fastq file (saves a lot of memory). Default: True
    All kwargs get passed into vk build
    """
    # * 1. logger
    if save_logs and not log_out_dir:
        log_out_dir = os.path.join(out, "logs")
    set_varseek_logging_level_and_filehandler(logging_level=logging_level, save_logs=save_logs, log_dir=log_out_dir)


    # * 2. Type-checking
    params_dict = make_function_parameter_to_value_dict(1)
    validate_input_sim(params_dict)

    if number_of_reads_per_variant_alt == 0:
        sample_type = "w"
    elif number_of_reads_per_variant_ref == 0:
        sample_type = "m"
    else:
        sample_type = "all"

    # * 3. Dry-run
    if dry_run:
        print(get_varseek_dry_run(params_dict, function_name="sim"))
        return None

    # * 4. Save params to config file and run info file
    config_file = os.path.join(out, "config", "vk_sim_config.json")
    save_params_to_config_file(params_dict, config_file)

    run_info_file = os.path.join(out, "config", "vk_sim_run_info.txt")
    save_run_info(run_info_file, params_dict=params_dict, function_name="sim")

    # * 5. input stuff
    # no need

    # * 6. Set up default folder/file output paths, and make sure they don't exist unless overwrite=True
    if not reads_fastq_out:
        reads_fastq_out = os.path.join(out, "synthetic_reads.fq")
    if save_variants_updated_csv and not variants_updated_csv_out:
        variants_updated_csv_out = os.path.join(out, "variants_updated_synthetic_reads.csv")
    if save_reads_csv and not reads_csv_out:
        reads_csv_out = os.path.join(out, "synthetic_reads_df.csv")

    os.makedirs(out, exist_ok=True)

    # * 7. Define kwargs defaults
    make_internal_copies = kwargs.get("make_internal_copies", True)
    filter_null_rows_from_important_cols = kwargs.get("filter_null_rows_from_important_cols", True)
    make_dataframes = kwargs.get("make_dataframes", True)

    # * 7.5 make sure ints are ints
    read_length, k, w = int(read_length), int(k), int(w)
    # don't account for number_of_reads_per_variant_alt (can be all), number_of_reads_per_variant_ref (can be all), error_rate (float), max_errors (can be float("inf"))

    # * 8. Start the function
    if isinstance(variants, (str, Path)):
        variants = str(variants)
        if not os.path.exists(variants):
            raise ValueError(f"variants path {variants} does not exist.")
        if ".tsv" in variants:
            variants = pd.read_csv(variants, sep="\t")
        elif ".csv" in variants:
            variants = pd.read_csv(variants)
        else:
            raise ValueError("variants must be a csv path, tsv path, or dataframe")
    elif isinstance(variants, pd.DataFrame):
        if make_internal_copies:
            variants = variants.copy()
    else:
        raise ValueError("variants must be a csv path, tsv path, or dataframe")

    header_column = var_id_column
        
    if header_column not in variants.columns:
        try:
            variants[header_column] = variants[seq_id_column] + ":" + variants[var_column]  #!!! might not work for my genome-cdna combo pipeline
            logger.info(f"adding {header_column} column to variants dataframe as <seq_id_column>:<var_column>")
        except Exception as e:
            raise KeyError(f"variants must contain a 'header' column provided by {header_column}, or that can be created with <seq_id_column>:<var_column>.")

    if (isinstance(variants, str) and not os.path.exists(variants)) or (variant_sequence_read_parent_column not in variants.columns and sample_type != "w") or (ref_sequence_read_parent_column not in variants.columns and sample_type != "m"):
        logger.info("cannot find mutant sequence read parent")
        if not vk_build_out_dir:
            vk_build_out_dir = os.path.join(out, "vk_build")
        
        update_df_out = f"{vk_build_out_dir}/sim_data_df.csv"

        if k and w:
            if k <= w:
                raise ValueError("k must be greater than w")
            read_w = read_length - (k - w)
        else:
            read_w = read_length - 1
        
        read_k = read_w + 1

        if sequences_cdna is not None and sequences_genome is not None:
            update_df_out_cdna = update_df_out.replace(".csv", "_cdna.csv")
            if not os.path.exists(update_df_out_cdna):
                varseek.build(sequences=sequences_cdna, variants=variants, out=vk_build_out_dir, w=read_w, k=read_k, remove_seqs_with_wt_kmers=False, optimize_flanking_regions=False, required_insertion_overlap_length=None, max_ambiguous=None, merge_identical=False, min_seq_len=read_length, save_variants_updated_csv=True, variants_updated_csv_out=update_df_out_cdna, seq_id_column=seq_id_column_cdna, var_column=var_column_cdna, overwrite=True, **kwargs)

            update_df_out_genome = update_df_out.replace(".csv", "_genome.csv")
            if not os.path.exists(update_df_out_genome):
                varseek.build(sequences=sequences_genome, variants=variants, out=vk_build_out_dir, w=read_w, k=read_k, remove_seqs_with_wt_kmers=False, optimize_flanking_regions=False, required_insertion_overlap_length=None, max_ambiguous=None, merge_identical=False, min_seq_len=read_length, save_variants_updated_csv=True, variants_updated_csv_out=update_df_out_genome, seq_id_column=seq_id_column_genome, var_column=var_column_genome, overwrite=True, **kwargs)

            # Load the CSV files
            df_cdna = pd.read_csv(update_df_out_cdna)
            df_genome = pd.read_csv(update_df_out_genome)

            # Concatenate vertically (appending rows)
            sim_data_df = pd.concat([df_cdna, df_genome], axis=0)

            sim_data_df_columns_original = []  # because I did the concatenation, I will want to save it regardless
        else:
            if not os.path.exists(update_df_out):
                logger.info("running varseek build")
                varseek.build(sequences=sequences, variants=variants, out=vk_build_out_dir, w=read_w, k=read_k, remove_seqs_with_wt_kmers=False, optimize_flanking_regions=False, required_insertion_overlap_length=None, max_ambiguous=None, merge_identical=False, min_seq_len=read_length, save_variants_updated_csv=True, variants_updated_csv_out=update_df_out, seq_id_column=seq_id_column, var_column=var_column, var_id_column=var_id_column, overwrite=True, **kwargs)

            sim_data_df = pd.read_csv(update_df_out)
        
            sim_data_df_columns_original = list(sim_data_df.columns)
        
        for old_column, new_column in [("vcrs_header", header_column), ("vcrs_sequence", variant_sequence_read_parent_column), ("wt_sequence", ref_sequence_read_parent_column)]:
            if old_column in sim_data_df.columns and new_column not in sim_data_df.columns:
                sim_data_df.rename(columns={old_column: new_column}, inplace=True)

        if variant_sequence_read_parent_rc_column not in sim_data_df.columns:
            sim_data_df[variant_sequence_read_parent_rc_column] = sim_data_df[variant_sequence_read_parent_column].apply(reverse_complement)
        if ref_sequence_read_parent_rc_column not in sim_data_df.columns:
            sim_data_df[ref_sequence_read_parent_rc_column] = sim_data_df[ref_sequence_read_parent_column].apply(reverse_complement)
        
        if "mutant_sequence_read_parent_length" not in sim_data_df.columns:
            sim_data_df["mutant_sequence_read_parent_length"] = sim_data_df[variant_sequence_read_parent_column].str.len()
        if "wt_sequence_read_parent_length" not in sim_data_df.columns:
            sim_data_df["wt_sequence_read_parent_length"] = sim_data_df[ref_sequence_read_parent_column].str.len()

        if "vcrs_id" not in sim_data_df.columns:
            sim_data_df["vcrs_id"] = varseek.utils.generate_unique_ids(len(sim_data_df))

        if list(sim_data_df.columns) != sim_data_df_columns_original:  # save if any columns were added
            sim_data_df.to_csv(update_df_out, index=False)

        variants = pd.merge(
            variants,
            sim_data_df[
                [
                    header_column,
                    variant_sequence_read_parent_column,
                    variant_sequence_read_parent_rc_column,
                    "mutant_sequence_read_parent_length",
                    ref_sequence_read_parent_column,
                    ref_sequence_read_parent_rc_column,
                    "wt_sequence_read_parent_length",
                    "vcrs_id"
                ]
            ],
            on=header_column,
            how="left",
            suffixes=("", "_read_parent"),
        )
    else:
        if variant_sequence_read_parent_rc_column not in variants.columns and sample_type != "w":
            variants[variant_sequence_read_parent_rc_column] = variants[variant_sequence_read_parent_column].apply(reverse_complement)
        if "mutant_sequence_read_parent_length" not in variants.columns and sample_type != "w":
            variants["mutant_sequence_read_parent_length"] = variants[variant_sequence_read_parent_column].str.len()

        if ref_sequence_read_parent_rc_column not in variants.columns and sample_type != "m":
            variants[ref_sequence_read_parent_rc_column] = variants[ref_sequence_read_parent_column].apply(reverse_complement)
        if "wt_sequence_read_parent_length" not in variants.columns and sample_type != "m":
            variants["wt_sequence_read_parent_length"] = variants[ref_sequence_read_parent_column].str.len()

        if "vcrs_id" not in variants.columns:
            variants["vcrs_id"] = varseek.utils.generate_unique_ids(len(variants))

    if not filters:
        filters = []
    if filter_null_rows_from_important_cols:
        filters.extend([f"{variant_sequence_read_parent_column}:is_not_null", f"{ref_sequence_read_parent_column}:is_not_null"])
    if sample_type != "m":
        filters.extend([f"wt_sequence_read_parent_length:greater_or_equal={read_length}"])
    if sample_type != "w":  # should be handled by vk build's min_seq_len, but good to have in case this was not derived from vk build
        filters.extend([f"mutant_sequence_read_parent_length:greater_or_equal={read_length}"])

    filters = list(dict.fromkeys(filters))  # equivalent to `list(set(filters))`, but maintains order of filters

    if filters:
        filtered_df = varseek.filter(
            input_dir=".",
            variants_updated_vk_info_csv=variants,
            filters=filters,
            out=out,
            return_variants_updated_filtered_csv_df=True,
            save_vcrs_filtered_fasta_and_t2g=False,
            vcrs_id_column=header_column,
            overwrite=True,
            make_internal_copies=False,
            called_from_vk_sim=True
        )  # filter to include only rows not already in variant and whatever condition I would like
    else:
        filtered_df = variants

    fastq_output_path_base, fastq_output_path_ext = splitext_custom(reads_fastq_out)
    fasta_output_path_temp = fastq_output_path_base + "_temp.fa"

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    column_and_default_value_list_of_tuples = [
        ("included_in_synthetic_reads", False),
        ("included_in_synthetic_reads_wt", False),
        ("included_in_synthetic_reads_mutant", False),
        ("list_of_read_starting_indices_wt", None),
        ("list_of_read_starting_indices_mutant", None),
        ("number_of_reads_wt", 0),
        ("number_of_reads_mutant", 0),
        ("any_noisy_reads_wt", False),
        ("noisy_read_indices_wt", None),
        ("any_noisy_reads_mutant", False),
        ("noisy_read_indices_mutant", None),
    ]

    for column, default_value in column_and_default_value_list_of_tuples:
        if column not in variants.columns:
            variants[column] = default_value

    len_filtered_df = len(filtered_df)
    if number_of_variants_to_sample == "all" or number_of_variants_to_sample > len_filtered_df:
        if number_of_variants_to_sample != "all":
            logger.info(f"number_of_variants_to_sample is greater than the number of variants in the filtered dataframe ({len_filtered_df}). Setting number_of_variants_to_sample to {len_filtered_df}.")
        sampled_reference_df = filtered_df
    else:
        # Randomly select number_of_variants_to_sample rows
        number_of_variants_to_sample = min(number_of_variants_to_sample, len_filtered_df)
        sampled_reference_df = filtered_df.sample(n=number_of_variants_to_sample, random_state=None)

    if sampled_reference_df.empty:
        logger.warning("No variants to sample")
        # return dict with empty values
        return {
            "read_df": pd.DataFrame(),
            "variants": pd.DataFrame(),
        }

    mutant_list_of_dicts = []
    wt_list_of_dicts = []

    if sample_type == "m":
        sampled_reference_df["included_in_synthetic_reads_mutant"] = True
        new_column_names = [
            "number_of_reads_mutant",
            "list_of_read_starting_indices_mutant",
            "any_noisy_reads_mutant",
            "noisy_read_indices_mutant",
        ]
    elif sample_type == "w":
        sampled_reference_df["included_in_synthetic_reads_wt"] = True
        new_column_names = [
            "number_of_reads_wt",
            "list_of_read_starting_indices_wt",
            "any_noisy_reads_wt",
            "noisy_read_indices_wt",
        ]
    else:
        sampled_reference_df["included_in_synthetic_reads_mutant"] = True
        sampled_reference_df["included_in_synthetic_reads_wt"] = True
        new_column_names = [
            "number_of_reads_mutant",
            "list_of_read_starting_indices_mutant",
            "number_of_reads_wt",
            "list_of_read_starting_indices_wt",
            "any_noisy_reads_mutant",
            "noisy_read_indices_mutant",
            "any_noisy_reads_wt",
            "noisy_read_indices_wt",
        ]

    new_column_dict = {key: [] for key in new_column_names}
    noisy_read_indices_mutant = []
    noisy_read_indices_wt = []

    with_replacement_original = with_replacement

    if not variant_type_column:
        variant_type_column = ""
    if variant_type_column not in sampled_reference_df:
        logger.warning(f"variant_type_column {variant_type_column} not in dataframe")
    
    approximate_symbol = "~"
    len_sampled_reference_df = len(sampled_reference_df)
    if isinstance(number_of_reads_per_variant_ref, int) and isinstance(number_of_reads_per_variant_alt, int):
        total_reads = len_sampled_reference_df * (number_of_reads_per_variant_ref + number_of_reads_per_variant_alt)
        approximate_symbol = ""
    elif isinstance(number_of_reads_per_variant_ref, int) and not isinstance(number_of_reads_per_variant_alt, int):
        total_reads = len_sampled_reference_df * (number_of_reads_per_variant_ref + read_length)  # read_length gives an upper bound
    elif not isinstance(number_of_reads_per_variant_ref, int) and isinstance(number_of_reads_per_variant_alt, int):
        total_reads = len_sampled_reference_df * (number_of_reads_per_variant_alt + read_length)
    else:
        total_reads = len_sampled_reference_df * (read_length + read_length)
    
    logger.info(f"Simulating {approximate_symbol}{total_reads} reads - {len_sampled_reference_df} variants, with {number_of_reads_per_variant_ref} ref reads per variant and {number_of_reads_per_variant_alt} alt reads per variant")

    # Write to a FASTA file
    total_fragments = 0
    skipped = 0
    
    with open(fasta_output_path_temp, "w", encoding="utf-8") as fa_file:
        # TODO: replace itertuples with iterating through columns as iterators/lists for speedup
        for row in tqdm(sampled_reference_df.itertuples(index=False), total=len_sampled_reference_df, desc="Looping through variants to simulate reads", unit="variants"):
            # try:
            header = getattr(row, header_column, None)
            vcrs_id = getattr(row, "vcrs_id", None)
            vcrs_header = getattr(row, "vcrs_header", None)
            vcrs_variant_type = getattr(row, variant_type_column, None)
            mutant_sequence = getattr(row, variant_sequence_read_parent_column)
            mutant_sequence_rc = getattr(row, variant_sequence_read_parent_rc_column)
            mutant_sequence_length = row.mutant_sequence_read_parent_length
            wt_sequence = getattr(row, ref_sequence_read_parent_column)
            wt_sequence_rc = getattr(row, ref_sequence_read_parent_rc_column)
            wt_sequence_length = row.wt_sequence_read_parent_length

            if not vcrs_id:
                vcrs_id = header
            if not vcrs_header:
                vcrs_header = header

            valid_starting_index_max_mutant = int(mutant_sequence_length - read_length + 1)
            valid_starting_index_max_wt = int(wt_sequence_length - read_length + 1)

            if not sample_ref_and_alt_reads_from_same_locations:
                if number_of_reads_per_variant_alt == "all":
                    read_start_indices_mutant = list(range(valid_starting_index_max_mutant))
                    number_of_reads_mutant = len(read_start_indices_mutant)
                else:
                    number_of_reads_per_variant_alt = int(number_of_reads_per_variant_alt)
                    number_of_reads_mutant = number_of_reads_per_variant_alt

                    if number_of_reads_per_variant_alt > valid_starting_index_max_mutant:
                        # logger.info("Setting with_replacement = True for this round")
                        with_replacement = True

                    if with_replacement:
                        read_start_indices_mutant = random.choices(range(valid_starting_index_max_mutant), k=number_of_reads_per_variant_alt)
                    else:
                        read_start_indices_mutant = random.sample(range(valid_starting_index_max_mutant), number_of_reads_per_variant_alt)

                    with_replacement = with_replacement_original

                # repeat but for wt
                if number_of_reads_per_variant_ref == "all":
                    read_start_indices_wt = list(range(valid_starting_index_max_wt))
                    number_of_reads_wt = len(read_start_indices_wt)
                else:
                    number_of_reads_per_variant_ref = int(number_of_reads_per_variant_ref)
                    number_of_reads_wt = number_of_reads_per_variant_ref

                    if number_of_reads_per_variant_ref > valid_starting_index_max_wt:
                        # logger.info("Setting with_replacement = True for this round")
                        with_replacement = True

                    if with_replacement:
                        read_start_indices_wt = random.choices(range(valid_starting_index_max_wt), k=number_of_reads_per_variant_ref)
                    else:
                        read_start_indices_wt = random.sample(range(valid_starting_index_max_wt), number_of_reads_per_variant_ref)

                    with_replacement = with_replacement_original
            else:
                if number_of_reads_per_variant_alt == "all" and number_of_reads_per_variant_ref == "all":  # I asserted earlier that these must be equal in this condition
                    read_start_indices_mutant = list(range(valid_starting_index_max_mutant))
                    read_start_indices_wt = list(range(valid_starting_index_max_wt))

                    number_of_reads_mutant = len(read_start_indices_mutant)
                    number_of_reads_wt = len(read_start_indices_wt)
                else:
                    valid_starting_index_max = min(valid_starting_index_max_mutant, valid_starting_index_max_wt)
                    number_of_reads_per_variant = int(number_of_reads_per_variant_alt)  # which I asserted to be the same as number_of_reads_per_variant_ref

                    if number_of_reads_per_variant > valid_starting_index_max:
                        # logger.info("Setting with_replacement = True for this round")
                        with_replacement = True

                    if with_replacement:
                        read_start_indices_mutant = random.choices(
                            range(valid_starting_index_max),
                            k=number_of_reads_per_variant,
                        )

                    else:
                        read_start_indices_mutant = random.sample(
                            range(valid_starting_index_max),
                            number_of_reads_per_variant,
                        )

                    read_start_indices_wt = read_start_indices_mutant

                    with_replacement = with_replacement_original

                    number_of_reads_mutant = number_of_reads_per_variant
                    number_of_reads_wt = number_of_reads_per_variant

            if sample_ref_and_alt_reads_from_same_locations and strand == "random":
                assign_strands_seed = random.randint(1, 100)  # makes sure that the same seed is used for both mutant and wt reads
            else:
                assign_strands_seed = None

            if strand is None:
                strand_value_for_function = random.choice(["f", "r"])
            else:
                strand_value_for_function = strand

            read_start_indices_and_strand_mutant = assign_strands(read_start_indices_mutant, strand_value_for_function, seed=assign_strands_seed)  # list of two-tuples - [(index, strand), ...]
            read_start_indices_and_strand_wt = assign_strands(read_start_indices_wt, strand_value_for_function, seed=assign_strands_seed)

            # Loop through each 150mer of the sequence
            if sample_type != "w":
                for i, selected_strand in read_start_indices_and_strand_mutant:
                    selected_sequence = mutant_sequence if selected_strand == "f" else mutant_sequence_rc  # if selected_strand == "r"
                    sequence_chunk = selected_sequence[i : i + read_length]
                    noise_str = ""
                    if add_noise_sequencing_error:
                        sequence_chunk_old = sequence_chunk
                        sequence_chunk = introduce_sequencing_errors(
                            sequence_chunk,
                            error_rate=error_rate,
                            error_distribution=error_distribution,
                            max_errors=max_errors,
                        )  # no need to pass seed here since it's already set
                        if sequence_chunk != sequence_chunk_old:
                            noise_str = "n"
                            noisy_read_indices_mutant.append(i)

                    read_id = f"{vcrs_id}_{i}{selected_strand}M{noise_str}_{total_fragments}"
                    read_header = f"{header}_{i}{selected_strand}M{noise_str}_{total_fragments}"
                    fa_file.write(f">{read_id}\n{sequence_chunk}\n")  # not worth adding a buffer, as the rate-limiting step is itertuples
                    if make_dataframes:
                        mutant_dict = {
                            "read_id": read_id,
                            "read_header": read_header,
                            "read_sequence": sequence_chunk,
                            "read_index": i,
                            "read_strand": selected_strand,
                            "reference_header": header,
                            "vcrs_id": vcrs_id,
                            "vcrs_header": vcrs_header,
                            "vcrs_variant_type": vcrs_variant_type,
                            "mutant_read": True,
                            "wt_read": False,
                            "region_included_in_vcrs_reference": True,
                            "noise_added": bool(noise_str),
                        }
                        mutant_list_of_dicts.append(mutant_dict)
                    total_fragments += 1

                if make_dataframes:
                    new_column_dict["number_of_reads_mutant"].append(number_of_reads_mutant)
                    new_column_dict["list_of_read_starting_indices_mutant"].append(read_start_indices_mutant)
                    new_column_dict["any_noisy_reads_mutant"].append(bool(noisy_read_indices_mutant))
                    new_column_dict["noisy_read_indices_mutant"].append(noisy_read_indices_mutant)
                noisy_read_indices_mutant = []

            if sample_type != "m":
                for i, selected_strand in read_start_indices_and_strand_wt:
                    selected_sequence = wt_sequence if selected_strand == "f" else wt_sequence_rc  # if selected_strand == "r"
                    sequence_chunk = selected_sequence[i : i + read_length]
                    noise_str = ""
                    if add_noise_sequencing_error:
                        sequence_chunk_old = sequence_chunk
                        sequence_chunk = introduce_sequencing_errors(
                            sequence_chunk,
                            error_rate=error_rate,
                            error_distribution=error_distribution,
                            max_errors=max_errors,
                        )  # no need to pass seed here since it's already set
                        if sequence_chunk != sequence_chunk_old:
                            noise_str = "n"
                            noisy_read_indices_wt.append(i)

                    read_id = f"{vcrs_id}_{i}{selected_strand}W{noise_str}_{total_fragments}"
                    read_header = f"{header}_{i}{selected_strand}W{noise_str}_{total_fragments}"
                    fa_file.write(f">{read_id}\n{sequence_chunk}\n")
                    if make_dataframes:
                        wt_dict = {
                            "read_id": read_id,
                            "read_header": read_header,
                            "read_sequence": sequence_chunk,
                            "read_index": i,
                            "read_strand": selected_strand,
                            "reference_header": header,
                            "vcrs_id": vcrs_id,
                            "vcrs_header": vcrs_header,
                            "vcrs_variant_type": vcrs_variant_type,
                            "mutant_read": False,
                            "wt_read": True,
                            "region_included_in_vcrs_reference": True,
                            "noise_added": bool(noise_str),
                        }
                        wt_list_of_dicts.append(wt_dict)
                    total_fragments += 1

                if make_dataframes:
                    new_column_dict["number_of_reads_wt"].append(number_of_reads_wt)
                    new_column_dict["list_of_read_starting_indices_wt"].append(read_start_indices_wt)
                    new_column_dict["noisy_read_indices_wt"].append(noisy_read_indices_wt)
                    new_column_dict["any_noisy_reads_wt"].append(bool(noisy_read_indices_wt))
                noisy_read_indices_wt = []
            # except Exception as e:
            #     skipped += 1

    if skipped > 0:
        logger.warning(f"Skipped {skipped} variants due to errors")

    fasta_to_fastq(fasta_output_path_temp, reads_fastq_out, add_noise=add_noise_base_quality, gzip_output=gzip_reads_fastq_out)
    os.remove(fasta_output_path_temp)
    logger.info(f"Wrote {total_fragments} variants to {reads_fastq_out}")
    if not make_dataframes:
        simulated_df_dict = {
            "read_df": None,
            "variants": None,
        }
        return simulated_df_dict

    for key in new_column_dict:
        sampled_reference_df[key] = new_column_dict[key]

    if mutant_list_of_dicts and wt_list_of_dicts:
        read_df_mut = pd.DataFrame(mutant_list_of_dicts)
        read_df_wt = pd.DataFrame(wt_list_of_dicts)
        read_df = pd.concat([read_df_mut, read_df_wt], ignore_index=True)
    elif mutant_list_of_dicts:
        read_df = pd.DataFrame(mutant_list_of_dicts)
    elif wt_list_of_dicts:
        read_df = pd.DataFrame(wt_list_of_dicts)

    # Read the contents of the files first
    if reads_fastq_parent:
        if not os.path.exists(reads_fastq_parent) or os.path.getsize(reads_fastq_parent) == 0:
            # write to a new file
            write_mode = "w"
        else:
            write_mode = "a"
        with open(reads_fastq_out, "r", encoding="utf-8") as new_file:
            file_content_new = new_file.read()

        # Now write both contents to read_fa_path
        with open(reads_fastq_parent, write_mode, encoding="utf-8") as parent_file:
            parent_file.write(file_content_new)

    if reads_csv_parent is not None:
        if isinstance(reads_csv_parent, str):
            reads_csv_parent = pd.read_csv(reads_csv_parent)
        elif isinstance(reads_csv_parent, pd.DataFrame) and make_internal_copies:
            reads_csv_parent = reads_csv_parent.copy()
        read_df = pd.concat([reads_csv_parent, read_df], ignore_index=True)

    variants = merge_synthetic_read_info_into_variants_metadata_df(variants, sampled_reference_df, sample_type=sample_type, header_column=header_column)

    variants["tumor_purity"] = variants["number_of_reads_mutant"] / (variants["number_of_reads_wt"] + variants["number_of_reads_mutant"])

    variants["tumor_purity"] = np.where(
        np.isnan(variants["tumor_purity"]),
        np.nan,  # Keep NaN as NaN
        variants["tumor_purity"],  # Keep the result for valid divisions
    )

    simulated_df_dict = {
        "read_df": read_df,
        "variants": variants,
    }

    if reads_csv_out is not None:
        read_df.to_csv(reads_csv_out, index=False)

    if variants_updated_csv_out is not None:
        variants.to_csv(variants_updated_csv_out, index=False)

    return simulated_df_dict
