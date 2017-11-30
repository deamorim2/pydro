# PYDRO - Python code for Hydrography Terrain Analysis Using Digital Elevation Models
Python code for Hydrography Terrain Analysis Using Digital Elevation Models

## STATUS

## Branches

The master branch has the latest minor release. (1.0)

The develop branch has the next minor release. (1.1-dev)

## INTRODUCTION

Pydro project presents python code for Hydrography Terrain Analysis Using Digital Elevation Models to provide drainage network analysis functionality to support decision making in Water Resources.

## LIST OF CODES

1 - pydro_flowpath.py

## REQUIREMENTS

Python 2.4+

GDAL/OGR 2.1.2+

## INSTALLATION (v.1.0)

Download the python files and copy the content to the workspace directory containing the dem files

## USAGE

1 - pydro_flow_path.py:

In the terminal: c:\workspace>python pydro_flowpath.py -d C:/workspace/ -s source.shp -i flowdirection.tif -o flowpath.tif -f t

Where:

workspace: C:/workspace/
shapefile drainage source point: source.shp
input flow direction raster: flowdirection.tif
output flow path raster: flowpath.tif
type of flow direction: t-> taudem flow direction model a-> arcgis/terrahidro flow direction model

## SETUP

## SYSTEM ENVIRONMENTAL SETUP (WINDOWS)

PATH=C:\Program Files\QGIS Brighton\bin

PYTHONPATH=C:\Program Files\QGIS x.x\apps\Python27\Lib

PYTHONHOME=C:\Program Files\QGIS x.x\apps\Python27

GDAL_DATA=C:\Program Files\QGIS x.x\share\gdal

GDAL_DRIVER_PATH=C:\Program Files\QGIS x.x\bin\gdalplugins  

## Notes

IMPORTANT : the changes are made in the current project, and will be saved only if you save the project.

## Authors

Gustavo Souto Molleri, Alexandre de Amorim Teixeira

## Licence

Pydro is Open Source, available under the GPLv2 license and is supported by a growing community of individuals, companies and organizations with an interest in management and decision making in water resources.
