# Welcome to varseek's contributing guide

Thank you for investing your time in contributing to our project! Any contribution you make will be reflected on the [varseek repo](https://github.com/pachterlab/varseek). ✨

Read our [Code of Conduct](./code_of_conduct.md) to keep our community approachable and respectable.

In this guide you will get an overview of the contribution workflow from opening an issue or creating a pull request (PR) to reviewing and merging a PR.

## Issues

### Create a new issue

If you spot a problem with varseek or you have an idea for a new feature, [check if an issue already exists](https://github.com/pachterlab/varseek/issues). If a related issue doesn't exist, you can open a new issue using the relevant [issue form](https://github.com/pachterlab/varseek/issues/new/choose).

### Solve an issue

Scan through our [existing issues](https://github.com/pachterlab/varseek/issues) to find one that interests you. You can narrow down the search using `labels` as filters. If you find an issue to work on, you are welcome to open a PR with a fix.

## Contribute through pull requests

### Getting started

1. Fork the repository.
- Using GitHub Desktop:
  - [Getting started with GitHub Desktop](https://docs.github.com/en/desktop/installing-and-configuring-github-desktop/getting-started-with-github-desktop) will guide you through setting up Desktop.
  - Once Desktop is set up, you can use it to [fork the repo](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/cloning-and-forking-repositories-from-github-desktop)!

- Using the command line:
  - [Fork the repo](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#fork-an-example-repository) so that you can make your changes without affecting the original project until you're ready to merge them.

2. Create a working branch and start with your changes!

### Commit your update

Commit the changes once you are happy with them.

### ‼️ Self-review the following before creating a Pull Request ‼️

1. Review the content for technical accuracy.
2. Copy-edit the changes/comments for grammar, spelling, and adherence to the general style of existing varseek code.
3. Format your code using [black](https://black.readthedocs.io/en/stable/getting_started.html).
4. Make sure the unit tests pass:
    - Developer dependencies can be installed with `pip install -r dev-requirements.txt`
    - Run existing unit tests from the varseek repository root with `coverage run -m pytest -ra -v tests && coverage report --omit=main.py,tests*`
5. Add new unit tests if applicable:
    - Arguments and expected results are stored in json files in ./tests/fixtures/
    - Unit tests can be added to ./tests/test_*.py and will be automatically detected
6. Make sure the edits are compatible with both the Python and the command line interface
    - The command line interface and arguments are defined in ./varseek/main.py
8. Add new modules/arguments to the documentation if applicable:
    - The manual for each module can be edited/added as ./docs/src/*.md

If you have any questions, feel free to start a [discussion](https://github.com/pachterlab/varseek/discussions) or create an issue as described above.

### Pull Request

When you're finished with the changes, [create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request), also known as a PR.

‼️ Please make all PRs against the `dev` branch of the varseek repository. 

- Don't forget to [link PR to issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) if you are solving one.
- Enable the checkbox to [allow maintainer edits](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/allowing-changes-to-a-pull-request-branch-created-from-a-fork) so the branch can be updated for a merge.
- If you run into any merge issues, checkout this [git tutorial](https://github.com/skills/resolve-merge-conflicts) to help you resolve merge conflicts and other issues.

Once you submit your PR, a varseek team member will review your proposal. We may ask questions or request additional information.

### Your PR is merged!

Congratulations! 🎉	 The varseek team thanks you. ✨

Once your PR is merged, your contributions will be publicly visible on the [varseek repo](https://github.com/pachterlab/varseek).
