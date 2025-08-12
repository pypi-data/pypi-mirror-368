![PyPI - Version](https://img.shields.io/pypi/v/bfjira)


# bfjira - Branch Management with JIRA Integration

bfjira (branch from Jira) is a command-line utility that simplifies the process of creating Git branches based on JIRA ticket information. It ensures that branch names are consistent and informative by incorporating the issue type and summary from the JIRA ticket.

## Installation

The recommended way to install bfjira is via `pip` from PyPI:

```bash
pip install bfjira
```

Make sure you have `pip` installed and are using a virtual environment if necessary.

## Usage

To use bfjira, you must have the following environment variables set:

- `JIRA_SERVER`: Your JIRA server URL.
- `JIRA_EMAIL`: The email address associated with your JIRA account.
- `JIRA_API_TOKEN`: Your JIRA API token.

Instructions for creating a Jira API token can be found [here](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)

Optionally, you can set the `JIRA_TICKET_PREFIX` environment variable to use a default prefix other than "SRE" for ticket IDs that are entered without a prefix.

### Basic Commands

- Show version:

  ```bash
  bfjira --version
  ```

- Show help message:

  ```bash
  bfjira --help
  ```

- Create a branch for a JIRA ticket:

  ```bash
  bfjira --ticket SRE-1234
  ```

  If you only have the ticket number, bfjira will use the default prefix ("SRE" or whatever is set in `JIRA_TICKET_PREFIX`):

  ```bash
  bfjira -t 1234
  ```

### Advanced Options

- Set a custom issue type for the branch:

  ```bash
  bfjira -t 1234 --issue-type hotfix
  ```

- Create a branch without setting the upstream:

  ```bash
  bfjira -t 1234 --no-upstream
  ```

- Increase output verbosity (useful for debugging):

  ```bash
  bfjira -t 1234 --verbose
  ```

- Optionally prevent transitioning the ticket to 'In Progress':

  By default, the script transitions the specified JIRA ticket to 'In Progress'. If you wish to create a branch for the ticket without changing its status, use the `--no-progress` flag. This is useful when you need to perform operations on the ticket without indicating that work has started.

  ```bash
  bfjira -t 1234 --no-progress
  ```

- Handle uncommitted changes:

  If `bfjira` detects uncommitted changes (including untracked files) in your repository, it will prompt you before proceeding. You can choose to have the script automatically stash these changes. The stash will be automatically popped after the branch is successfully created and the JIRA ticket is transitioned. If you choose not to stash, the script will exit.

## Versioning

bfjira follows [Semantic Versioning](https://semver.org/) (SemVer) for its releases:

- **MAJOR** version (X.0.0) - Incompatible API changes
- **MINOR** version (0.X.0) - New features in a backward-compatible manner
- **PATCH** version (0.0.X) - Backward-compatible bug fixes

The versioning is automated through GitHub Actions, which:
1. Detects the type of change (feature, fix, etc.) from commit messages
2. Automatically increments the appropriate version number
3. Creates a new release and publishes to PyPI

## Troubleshooting

### Common Issues

1. **JIRA Authentication Errors**
   - Ensure your `JIRA_API_TOKEN` is valid and not expired
   - Verify your `JIRA_EMAIL` matches the account associated with the API token
   - Check that your JIRA account has the necessary permissions

2. **Branch Creation Issues**
   - Make sure you're in a Git repository
   - Verify you have write permissions to the repository
   - Check that the branch name doesn't already exist

3. **Version Mismatches**
   - If you encounter version-related issues, try updating to the latest version:
     ```bash
     pip install --upgrade bfjira
     ```

### Getting Help

If you encounter issues not covered here:
1. Check the [GitHub Issues](https://github.com/nwhobart/bfjira/issues) for similar problems
2. Enable verbose output with `--verbose` flag for more detailed error messages
3. Open a new issue with detailed information about your problem

## Development

### Setup

bfjira uses [Poetry](https://python-poetry.org/) for dependency management and packaging. To set up the development environment:

1. Install Poetry:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/nwhobart/bfjira.git
   cd bfjira
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Activate the virtual environment:
   ```bash
   poetry shell
   ```

### Running Tests

Run the test suite with:
```bash
poetry run pytest
```

### Contributing

Contributions to bfjira are welcome! Please read the contributing guidelines before submitting pull requests.

## License

bfjira is released under the GNU General Public License. See the [LICENSE](LICENSE) file for more details.
