# Minkar
Minkar is a Python CLI toolkit built with Typer to improve development workflow. It helps with common developer tasks from merging source files to managing frequently used shell commands.

## Installation

```bash
pip install minkar
```

or from source:

```bash
git clone https://github.com/Waland2/Minkar.git
cd minkar
pip install .
```
## Features
* **`minkar get code`** - merge project source files into a single text, with extension filters, exclusion rules, and statistics.
* **`minkar get dir`** - shows the project folder tree in either indented form or using bars (`├──`, `└──`).
* **`minkar get file`** - create a `.zip` archive of a directory with include/exclude rules.
* **`minkar cmd`** - save, edit, delete, and run custom shell commands with argument placeholders.

## Usage examples

Merge all Python and JavaScript files in a project and copy to clipboard:

```bash
minkar get code --langs py,js --recursive
```

Print directory tree with files:

```bash
minkar get dir --include-files --bars
```

Create a zip archive with only `.py` files:

```bash
minkar get file --match "\.py" --output code.zip
```

Save and run a shell command:

```bash
minkar cmd save "git status" --name gst
minkar cmd run gst
```

## CLI Structure

* `minkar get` - project information utilities:
  * `code` - merge source files
  * `dir` - print directory tree
  * `file` - create zip archives
* `minkar cmd` - shell command manager:
  * `save` - save a command
  * `run` - execute a command
  * `edit` - update a command
  * `delete` - remove a command
  * `delete-all` - remove all commands
  * `list` - list all saved commands

## License

This project is licensed under the [MIT License](LICENSE.md).
