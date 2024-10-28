# ![Python](https://img.shields.io/badge/type-Python-yellow) Mash To PointCloud

Export a Mash Network to an Alembic point-cloud.

![demo](./demo.gif)

> [!WARNING] It seems the script fully work only when using a MASH _Instancer_.
> When using a _repro_mesh_ only the basic translate/rotate/scale attrbiutes
> seems to work.

## Use

1. Copy/paste in script editor
2. Select the Mash Network you want to export.
3. Run script.
4. A file dialog open : Select the path + filename for the alembic export.

### Modifying what is exported

_(wip)_

You can use the `scene_config` dictionnary:

The `build.particleSystems` keys allow you to create a new attribute on the 
particleSystem for export (you must also add it in `export.alembic.attributes`
). This attribute can be then connected to an attribute on the `Mash Node` by
specifying it in the `mashAttr` key.

The `mashAttr` key except the path of the attribute on the `Mash Node` that
must be connected to the newly created p.s. attribute. Make sure these two
attributes are of the same type. 

### Export a randomColor attribute

This is an enough special case to be explained here. If you are using Mash
Instances you might now that the `color` mash node can't be used. But here is 
a workaround as [explained here](https://redshift.maxon.net/topic/24542/maya-making-mash-color-node-working-with-instances-probability-node).

The issue is that the `point color` attribute must be gathered on the mash
`Python` node. To avoid rewriting all the script while actually not needed,
the solution is simply to create a new attribute on the Mash Node called like
`colorPP`, and connect the `Python.colorOutPP` attribute to it. Then in 
the script you just have to modify the `scene_config` dict as usual :
```python
scene_config = {
    "build": {
        "particleSystem": {
            "MyColorRandom": {
                "dataType": "vectorArray",
                "mashAttr": "colorPP"
            }
        },
    },
    "export": {
        "alembic": {
            "attributes": ["MyColorRandom"]
        }
    }   
}
```

## Current Issues

- Doesn't seem to support animated attribute export except from P.

## Licensing

See [LICENSE.md](./LICENSE.md).

## Credits

Huge thanks to Onouris on Discord for showing me the initial nParticle setup 
that saved my ass when I needed it.