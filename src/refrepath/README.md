# refrepath

Batch repathing of references in Maya scenes.

The current system of repathing used a "search and replace" logic.

Example :

```python
>>> source_reference_path = "Z:/projects/demo/assetA.ma"
>>> search = "*projects"
>>> new_root_path = "X:/work/pro"
"X:/work/pro/demo/assetA.ma"
```

This is useful if only the left-most part of the path have to be updated. If there
is a change of hierarchy on the "right side", **this tool can't work**.

# Requirements

_refrepath_ needs Python >= 3.7 to work. Compatible Maya version are:
- Maya 2023 (3.9.7)
- Maya 2022 (3.7.7)

# How to use.

You need to process an unknown number of file all at once in a given directory.

This can be achieved using the CLI.
- must be executed from command line **with a python interpreter installed**.
- will parse the given directory for maya files and open a subprocess for each of
them to repath references.
- create logs files for every maya file repathed

### Instructions

```shell
cd path/to/refrepath/directory/
python -m refrepath --help
```
> open the help of the CLI to check all options available

You can set the path to the `mayabatch.exe` using the `MAYA_BATCH_PATH` environment variable.

```shell
# linux shell
cd path/to/refrepath/directory/
export MAYA_BATCH_PATH="/c/Program Files/Autodesk/Maya2023/bin/mayabatch.exe"
python -m refrepath --help
```
```shell
# windows batch
CD path/to/refrepath/directory/
SET "MAYA_BATCH_PATH=C:\Program Files\Autodesk\Maya2023\bin\mayabatch.exe"
python -m refrepath --help
```

Example of executing repathing on a directory

```shell
# linux shell
cd path/to/refrepath/directory/
export MAYA_BATCH_PATH="/c/Program Files/Autodesk/Maya2023/bin/mayabatch.exe"
python -m refrepath "/z/projects/demo" "*projects/demo" "::use_maya_file_dir"
```

This will find all maya files (`.ma` and `.mb`) **recursively** in the directory,
and for each of them, create a subprocess to open Maya and repath the reference.

A `.log` file is created at the root of the directory provided AND next to each
maya file and allow you to check progress and if any error was raised.

You only need 3 argument minimum to start the process : 
- `maya_file_dir` : directory to parse recursively for maya files
- `search` : Part of the reference's path to replace. A [fnmatch](https://docs.python.org/3/library/fnmatch.html)-compatible pattern.
- `replace` : Partial path to swap with the result of the search. You can use `"::use_maya_file_dir"` if it is the same as the maya_file_dir.

Check the `--help` command for additional arguments.
