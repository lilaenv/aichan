# Developer Documentation

This documentation is intended for developers and contributors who work on improving the AIchan source code. When developing or contributing to the source code, please follow the rules below.

## Development Environment

This guide assumes macOS users setting up the AIchan development environment.

### Editor Setup

**VSCode** or **Cursor** is recommended. Any editor that can provide a similar environment is acceptable.

Below are recommended extensions for VSCode. These are also compatible with Cursor.

- Required Extensions
    - [Mypy Type Checker](https://github.com/microsoft/vscode-mypy)
    - [Python](https://github.com/Microsoft/vscode-python)
    - [Ruff](https://github.com/astral-sh/ruff-vscode)
    - [SQLite Viewer](https://github.com/qwtel/sqlite-viewer-vscode)

- Optional Extensions
    - [Github Actions](https://github.com/github/vscode-github-actions)
    - [Github Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
    - [IntelliCode](https://marketplace.visualstudio.com/items?itemName=VisualStudioExptTeam.vscodeintellicode)
    - [Jupyter](https://github.com/Microsoft/vscode-jupyter)
    - [YAML](https://github.com/redhat-developer/vscode-yaml)

For basic VSCode and cursor settings, please refer to [settings.json](https://github.com/lilaenv/aichan/blob/main/.vscode/settings.json). Those who use a cursor should also refer to [.cursor](https://github.com/lilaenv/aichan/blob/main/.cursor)

### Python Setup

We use **uv** for Python package management. It can handle both Python installation and package management in one place. For installation details and more information, please refer to the [official website](https://docs.astral.sh/uv/).

Below is a list of basic uv commands:

<table>
    <tr>
        <th>Command</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>uv python install 3.x.x</td>
        <td>Install Python with specified version</td>
    </tr>
    <tr>
        <td>uv sync</td>
        <td>Synchronize dependencies</td>
    </tr>
    <tr>
        <td>uv add [package]</td>
        <td>Add a dependency</td>
    </tr>
    <tr>
        <td>uv remove [package]</td>
        <td>Remove a dependency</td>
    </tr>
    <tr>
        <td>uv --version</td>
        <td>Check uv version</td>
    </tr>
    <tr>
        <td>uv self update</td>
        <td>Update uv to the latest version</td>
    </tr>
</table>

## Cloning and Dependencies

Navigate to your desired directory and clone the repository. Then, you can synchronize dependencies using uv commands. If the specified Python version is not installed, please install it before synchronizing dependencies.

```
# ----- clone repo -----
git clone https://github.com/lilaenv/aichan.git
cd aichan/

# ----- install python (if necessary) -----
uv python install 3.11.11

# ----- sync dependencies -----
uv sync
```

## Coding Standards

We generally follow [PEP8](https://pep8-ja.readthedocs.io/ja/latest/). Additionally, we use mypy and ruff to improve code quality and prevent bugs.

Basically, if there are no mypy or ruff warnings, you are following the coding standards. However, the following are AIchan-specific rules that **will not trigger warnings**, so please be careful:

- Use `# type: ignore` when dealing with complex Union types or when mypy cannot correctly recognize types for any reason. However, you must explain the reason immediately before the line, as shown below:
    ```python
    # Explain the reason here
    warned_variable # type: ignore
    ```

- When you need to ignore ruff rules for a valid reason, use `# noqa: <rule>`. As with mypy, you must explain the reason immediately before the line.

- In specific contexts, wildcard imports are allowed (ignore F403). However, when using wildcard imports or functions defined by them, you must explain the reason immediately before the import.

    Example:
    ```python
    # Explain the reason here
    from module import *

    # Explain the reason here
    from_wildcard_import() # type: ignore # noqa: F405
    ```

    The following exceptions do not require explanation:

    - `from path.to.utils.decorators import *`
    - Imports of `commands` and `events` in `__main__.py`

**Note**

If you encounter any issues with wildcard imports, please report them in an Issue.

## Branch Structure

We follow the [A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/), but we use `main` instead of `master`.

![Branch Overview](https://github.com/lilaenv/aichan/blob/main/.github/assets/branch.png)

Here's a detailed explanation of each branch:

<table>
    <tr>
        <th>Branch Name</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>main</td>
        <td>Generally no direct work is done here</td>
    </tr>
    <tr>
        <td>hotfix</td>
        <td>For urgent fixes after release<br>Create as hotfix/[id] from main<br>After completion, create PR to merge into main and develop</td>
    </tr>
    <tr>
        <td>release</td>
        <td>For pre-release testing<br>No new features are added to this branch<br>After completion, create PR to merge into main & tag<br>If bugs are fixed or changes are committed, also create PR to merge into develop</td>
    </tr>
    <tr>
        <td>develop</td>
        <td>Base branch for development<br>Derived from main</td>
    </tr>
    <tr>
        <td>fix</td>
        <td>For non-urgent bug fixes<br>Create as fix/[id] from develop<br>After completion, create PR to merge into develop</td>
    </tr>
    <tr>
        <td>feature</td>
        <td>For new feature development<br>Create as feature/[id] from develop<br>After completion, create PR to merge into develop</td>
    </tr>
</table>

## Issues

Feel free to create Issues for source code improvements, bug reports, or new feature proposals. You can create Issues [here](https://github.com/lilaenv/aichan/issues).

## Commit Rules

We refer to the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

Commit messages should follow the [template](https://github.com/lilaenv/aichan/blob/main/.github/.gitmessage). You can display the template during commit by using the following command. If you use this, do not use the `-m` option:
```
git config commit.template /path/to/.gitmessage
```
