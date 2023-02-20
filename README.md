# Software Design course project - Group SWD <!-- omit in toc -->
A desktop application built with Python and PyQt6. Under development.

- [Installation](#installation)
- [Development](#development)
  - [Installing dependencies with `poetry`](#installing-dependencies-with-poetry)
    - [Setting up `poetry`](#setting-up-poetry)
    - [Using `poetry`](#using-poetry)
  - [User interface development](#user-interface-development)
  - [Testing](#testing)
  - [Linting and formatting](#linting-and-formatting)

## Installation
1. Make sure you have installed [Python](https://www.python.org/downloads/). 
2. Install `poetry` and project dependencies according to [Setting up `poetry`](#setting-up-poetry)
3. Run `poetry run python3 app.py` in the project root folder.

NOTE! If for some reasons you do not want to install `poetry`, you can install the dependencies listed in the `[tool.poetry.dependencies]`
section inside the `pyproject.toml` file. Run `python3 app.py` to start the app. But we __really__ recommend you using `poetry`.

## Development

### Installing dependencies with `poetry`
This project uses [poetry](https://python-poetry.org/) to manage Python dependencies. This means you do not have to install Python packages individually or manage them yourself - just install Poetry and it will do it for you. Poetry creates a virtual environment that contains the dependencies, therefore does not pollute your local machine. 

#### Setting up `poetry`
1. Install `poetry` according to the [installation guide](https://python-poetry.org/docs/#installation)
2. Install project dependencies by running `poetry install`.

#### Using `poetry`
All `poetry` commands are listed [here](https://python-poetry.org/docs/cli/). For example, `poetry add <package-name>` installs a new package, while `poetry remove <package-name>` uninstalls the package. 

### User interface development
This project use PyQt6 as the UI Platform. The UI is designed using QtDesigner (download Qt [here](https://www.qt.io/download-qt-installer) if you want to design the UI).

The UI file from QtDesigner has the extension `.ui`. All `.ui` files are stored in `ui/`. In order for PyQt to use these files, they have to be compiled into `.py` files whenever they are modified. This should be done for every modified .ui file for it to take effect:
1. Run `poetry run pyuic6 -o <output-py-file-path> <input-ui-file-path>`. For example `poetry run pyuic6 -o ui/Ui_main_window.py ui/main_window.ui`.


### Testing
Run tests using *pytest*: `poetry run pytest .`

All tests are in folder `tests` in the root directory. 

### Linting and formatting
If you are using VSCode, linting and formatting is automatically done whenever a Python file is saved. This configuration can be seen in `.vscode/settings.json`

Otherwise, you can running the linter and formatter in the Terminal with the commands below .
1. Linting all python files using *flake8*: `poetry run flake8 .`
2. Formatting all python files using *black*: `poetry run black .`

The linter and formatter can also be configured for other IDEs/editors, however the details depend on the editors themselves.

### Feature notes

- The import/export user options is done by clicking on the top bar File -> Import/Export, or keyboard shortcuts Cmd/Ctrl + I/E
- There are 3 bonus features we implemented: saving plots, different plotting options and fetching data on separate thread to avoid blocking the UI. Saving plots can be done in all tabs, while plotting options can be chosen in the STATFI tab (bar chart or line graph).