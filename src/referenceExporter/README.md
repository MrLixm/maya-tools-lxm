# referenceExporter

Scripts to help exporting references nodes from a scene.

# `referenceBakedExport.py`

Export the selected reference dag object to a new `.ma` file.
The reference exported is "unloaded" (baked to static geometry) then its namespace is being removed.

The export path is queried via a file dialog window.

## Usage

- Select a single reference location to export
- Run script