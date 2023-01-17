# refrepath

Repathing of references in Maya scenes.

The current system of repathing used a "common denominator" logic, where
a user-provided path entity name is provided to split the source reference
path and replace the left-most part with the new desired root path.

Example :

```python
>>> source_reference_path = "Z:/projects/demo/assetA.ma"
>>> common_denominator = "demo"
>>> new_root_path = "X:/work/pro"
# we split source_reference_path at "demo" and prefix it with new_root_path:
"X:/work/pro/demo/assetA.ma"
```

This is useful if only the left-most part of the path have to be updated. If there
is a change of hierarchy on the "right side", **this tool can't work**.

# Requirements

_refrepath_ needs Python >= 3.7 to work. Compatible Maya version are:
- Maya 2023 (3.9.7)
- Maya 2022 (3.7.7)

# How to use.

## Individual files

You only need to repath reference in one scene and would like to do it via
a convenient interface.

- must be executed from a Maya session.
- find all references in given scene and repath them with the given parameters

### Installation

- Copy and paste the `refrepath` directory (the one with the python files inside) to one
of the user preferences scripts directory of Maya.

> **Help**: the uers-prefs directory to install python tools are :
> 1. `C:\Users\{USER}\Documents\maya\scripts`
> 2. `C:\Users\{USER}\Documents\maya\{VERSION}\scripts`
>
> Don't install in both, pick one depending on what you want. Option 1. make it
> accessible for all versions of Maya.

- Start/restart Maya.
- In the script editor execute
    ```python
    import refrepath.gui
    refrepath.gui.gui()
    ```
  (You can put this code in a shelf button for easier access)

### Usage

- Make sure you are on an empty scene before you start the repathing.
- Give the path to the maya file with reference.
- Give the path to the new root directory for the left-most part of references.
- Start the repathing.

## Batch process a directory

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
python -m refrepath "/z/projects/demo"
```

This will find all maya files (`.ma` and `.mb`) **recursively** in the directory,
and for each of them, create a subprocess to open Maya and repath the reference.

A `.log` file is created at the root of the directory provided AND next to each
maya file and allow you to check progress and if any error was raised.

You notice that only one argument is provided. The script will assume the directory
we want to find maya file in, will also be used as new root for reference repathing.

If you want to specify both individually , you can use `--new_root_dir` :

```shell
# linux shell
cd path/to/refrepath/directory/
export MAYA_BATCH_PATH="/c/Program Files/Autodesk/Maya2023/bin/mayabatch.exe"
python -m refrepath "/z/projects/demo/assets/env" --new_root_dir "/z/projects/demo"
```