# ![Python](https://img.shields.io/badge/type-Python-yellow) Mash To PointCloud

Export a Mash Network to an Alembic point-cloud.

![demo](./demo.gif)

## Use

1. Copy/paste in script editor
2. Select the Mash Network you want to export.
3. Run script.
4. A file dialog open : Select the path + filename for the alembic export.

### Modifying what is exported

_(wip)_

You can use the `scene_config` dictionnary.
The `build.particleSystems` keys allow you to create a new attribute to export
(you must also add it in `export.alembic.attributes`). This attribute can be
linked to an attribute on the mash node by specifying it in the `mashAttr` key.

## Licensing

See [LICENSE.md](./LICENSE.md).

## Credits

Credit to Onouris on Discord for showing me the initial nParticle setup.