#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 09:52:55 2017

###########################################
# Author: Abhishes lamsal
# Email: abhilam@ksu.edu
# Year : @2018
# Kansas State University, Department Of Agronomy
# contact: abhilam@ksu.edu
# Purpose: Download Sentinnel Scene using boundry information (shapefile) 
# Do the radiometric correction using Sen2cor
# Clip the image based on the boundary(using geojson) and use N recommendation 
# algorithm to create Nrec raster.

##############################################
"""
import numpy as np
import shapefile
from json import dumps
import shutil
from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt #get_coordinates
import zipfile
import os
import glob
import urllib
from json import dumps
import gdal
import matplotlib.pyplot as plt
from cStringIO import StringIO
from PIL import Image
import sys

# This module convert shapefile to Geojson which is needed later to clip images
def shapetogeojson(Inshp):
    # Inshp= name of shapefile in string "name"
    shapeinput   = str(Inshp)
    reader       = shapefile.Reader(shapeinput)
    fields       = reader.fields[1:]
    field_names  = [field[0] for field in fields]
    buffer       = []
    for sr in reader.shapeRecords():
        atr      = dict(zip(field_names, sr.record))
        geom     = sr.shape.__geo_interface__
        buffer.append(dict(type="Featureimport gdal", \
                    geometry = geom, properties=atr)) 
   # write the GeoJSON file
    geojson      = open(Inshp[:-4]+".geojson", "w")
    geojson.write(dumps({"type": "FeatureCollection",\
                        "features": buffer}, indent=2) + "\n")
    geojson.close()
    return
    
