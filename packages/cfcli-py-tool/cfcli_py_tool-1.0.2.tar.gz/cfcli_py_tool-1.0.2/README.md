# CFCli
A cli tool for codeforces

## Installation

Head to [the pypi page](https://pypi.org/project/cfcli-py-tool/) and copy the command at the top.

In our case it will be `pip install cfcli-py-tool`.

Open your terminal (or command line if you're using windows) and paste the following:

```bash
pip install cfcli-py-tool
```

If this gives an error, please try:

```bash
pip3 install cfcli-py-tool
```

This will install CFCli from the PyPi package manager.

In order to test your installation, please run:

```bash
cf-cli
```

## Requirements

Since the project is a pip (python package manager) package, you are required to have the following in order for it to work.
- Python 3.8+
- Latest Pip version

## Setup

The setup for cf-cli is very minimal. Since there are parts of the [Codeforces API](https://codeforces.com/apiHelp) that require authentication, it is the only environment variable that is needed.

# For the rest of the documenation, please visit the [official site](https://compprogtools.github.io/CFCli/)