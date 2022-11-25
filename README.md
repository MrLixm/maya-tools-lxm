![header:maya logo](./img/header.jpg)

Collection of scripting stuff I wrote for Autodesk's Maya software.

## Utilisation

Everything should be written in the top docstring of each script.
Else a README.md should be supplied.

## What's Inside

- [`cmds_interface_demo`](./src/cmds_interface_demo)

    A script to demonstrate how you can use `cmds` to create a quick interface in Maya.

- [`mash2pointcloud`](./src/mash2pointcloud)

    Export a Mash Network to an Alembic point-cloud.

- [`selectSimilarPolyCount`](./src/selectSimilarPolyCount)

    From a selected object , find in the whole scene which geometric objects has the
same vertex number and select them.

- [`polyTransferUVs`](./src/polyTransferUVs)

    Transfer UVs from one object to multiple objects.

- [`shapeNameConform`](./src/shapeNameConform)

    Make the shapes of a dag object have the same name as the transform ( for when
they are different).

- [`securityVirusCleaner`](./src/securityVirusCleaner)

    A utility aimed at removing the `vaccine.py` virus from the currently openened
maya scene and from your system.

- [`resetWindowPosition`](./src/resetWindowPosition)

    Useful to reset a maya window that might have gone off-screeen and is not
visible anymore.

- [`referenceExporter`](./src/referenceExporter)

  Scripts to help exporting references nodes from a scene.


## Licensing

License should be specified in each directory or in the top of each file else
the terms specified in the root's [LICENSE.md](./LICENSE.md) file will apply.


## Contact

[monsieurlixm@gmail.com](mailto:monsieurlixm@gmail.com)
