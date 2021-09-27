
This package allows converting and exporting a MASH network as a pointcloud 
(using the Alembic file format).

You have to handle the instance source export yourself thought.


# About

- **Author**: Liam Collod.

- **Credits**:
  
  - Onouris for showing me the maya setup.
    
Tested on Maya 2022.

# How to run

## Option 01

_On the fly import (dirty)._

Copy the path to the `mash2pointcloud` directory (the one that have this .md file)
In the script editor run the bottom snippet.
Before think to replace `$PACKPATH` with the above path.

```python

import sys

m2p_path = "$PACKPATH"
if m2p_path not in sys.path:
    sys.path.append(m2p_path)

import mash2pointcloud as m2p

m2p.start()

```

## Option 02

_Maya package registering_

Copy the `mash2pointcloud` directory (the one that have this .md file) inside
location registered by Maya: