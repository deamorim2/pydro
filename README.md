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

input: start drainage point(vector) and Flow Direction(raster)

output: flow path (raster)  - raster with values equal to one showing the sintetic drainage traced from source to outlet.

2 - pydro_agreedem.py (using numpy)

input: vector coverage (vector) and digital elevation model (raster)

output: agree dem* (raster) surface reconditioning models that adjusts the surface elevation of the DEM to be consistent with a vector coverage. The vector coverage can be a stream or ridge line coverage. 

3 - pydro_agreedem_gdal (using gdal, faster)

input: vector coverage (vector) and digital elevation model (raster)

output: agree dem* (raster) surface reconditioning models that adjusts the surface elevation of the DEM to be consistent with a vector coverage. The vector coverage can be a stream or ridge line coverage.

*http://www.ce.utexas.edu/prof/maidment/gishydro/ferdi/research/agree/agree.html

## REQUIREMENTS

Python 2.4+

GDAL/OGR 2.1.2+

## INSTALLATION (v.1.0)

Download the python files and copy the content to the workspace directory containing the dem files

## USAGE

**1 - pydro_flow_path.py:**

>Type in the terminal:

    c:\workspace>python pydro_flowpath.py -w c:/workspace/ -s source.shp -i flowdirection.tif -o flowpath.tif -f t

optional arguments:

  -h, --help            show this help message and exit

  Workspace Directory
  
  -w DIR_NAME, --directory workspace DIR_NAME
  
  Source Points Shapefile Name
                        
  -s SHP_NAME, --source_points SHP_NAME
  
  Flow Direction File Name
                          
  -i INFILE_NAME, --input_flow_direction INFILE_NAME
  
  Flow Path Output File Name
                        
  -o OUTFILE_NAME, --output_flow_path_file OUTFILE_NAME
  
  Type of Flow Direction: Taudem=t ArcGIS/TerraHydro=a
                        
  -f TYPE_FLOW_DIRECTION, --flow TYPE_FLOW_DIRECTION
  

**2 - pydro_agreedem.py:**

>Type in the terminal:

    c:\workspace>python pydro_agreedem.py -w c:/workspace/ -hy c:/workspace/tdr.shp -i c:/workspace/img02.tif -o agreedem -bf 2 -sm 5 -sh 100

optional arguments:

  -h, --help            show this help message and exit
  
  Workspace Directory
  
  -w DIR_NAME, --directory workspace DIR_NAME
  
  Hydrography Shapefile Name Directory
                        
  -hy SHP_NAME, --hydrography SHP_NAME
  
  DEM File Name Directory
                         
  -i INFILE_NAME, --input_dem_file INFILE_NAME
  
  Output AgreeDEM File Name
                         
  -o OUTFILE_NAME, --output_agreedem_file_name OUTFILE_NAME
  
  Buffer distance in Pixel
                          
  -bf BUFFER_VALUE, --buffer BUFFER_VALUE
  
  Smooth modified elevation
                       
  -sm SMOOTH_VALUE, --smooth SMOOTH_VALUE
  
  Sharp drop/raise grid
                       
  -sh SHARP_VALUE, --sharp SHARP_VALUE
                        
                        
**3 - pydro_agreedem_gdal.py:**

>Type in the terminal:

    c:\workspace>python pydro_agreedem_gdal.py -w c:/workspace/ -hy c:/workspace/tdr.shp -i c:/workspace/img02.tif -bf 2 -sm 5 -sh 100 -gd "c:/Program Files/QGIS 2.14/bin" -od "c:/Program Files/QGIS 2.14/bin"

optional arguments:

  -h, --help            show this help message and exit
  
  Workspace Directory
  
  -w DIR_NAME, --directory workspace DIR_NAME
  
  Hydrography Shapefile Name Directory
                          
  -hy SHP_NAME, --hydrography SHP_NAME
  
  DEM File Name Directory
 
  -i INFILE_NAME, --input_dem_file INFILE_NAME
  
  Buffer distance in Pixel
 
  -bf BUFFER_VALUE, --buffer BUFFER_VALUE
  
  Smooth modified elevation
 
  -sm SMOOTH_VALUE, --smooth SMOOTH_VALUE
  
  Sharp drop/raise grid
  
  -sh SHARP_VALUE, --sharp SHARP_VALUE
  
  Gdal Directory Name
    
  -gd GDAL_DIRECTORY, --gdal_directory GDAL_DIRECTORY
  
  OSGEO Directory Name
   
  -od OSGEO_DIRECTORY, --osgeo_directory OSGEO_DIRECTORY
 

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
