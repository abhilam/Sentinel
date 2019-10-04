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
# Purpose: Obtain Sentinnel Product
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



# search by polygon, time, and SciHub query keywords

def ObtainProduct_sentinel(JsonFile,Sdate,Edate,Cldmin,Cldmax):
    # This will extract the sentinnel product and stored in Dictionary as SceneID and Date when Image collected
    # JsonFile = Name of the geojson file of Area of Interest
    # Sdate    = Start date (eg. 20150101 YYYYMMDD)
    # Edate    = End Date (eg. 20160101 YYYYMMDD)
    CldCoverrange      = '['+str(Cldmin) + ' TO '+ str(Cldmax)+']' 
    footprints         = geojson_to_wkt(read_geojson(JsonFile))
    #print footprints
    products           = api.query(footprints, (Sdate,Edate), platformname = 'Sentinel-2', cloudcoverpercentage = CldCoverrange)
    a                  = api.to_geodataframe(products)
    #print a
    # Collect all the data available and its date and product ID
    Result             = {'Pr_Id':[],'Datetime':[],'Geometry':[],'Identifier':[]}
    if len(products)==0:
        print 'No scene available in given condition'
    else:
        print 'Found '+ str(len(products)) + ' Scene\n',"Here is your list of Dates available and its product id"
    counter            = 0
    for i in xrange(len(a)):# in products:
        Result['Pr_Id'].append(a['uuid'][i])
        Result['Datetime'].append(a['beginposition'][i])
        Result['Geometry'].append(a['geometry'][i])
        Result['Identifier'].append(a['identifier'][i])
        print counter,' ==> ',a['beginposition'][i],' ==> ',a['uuid'][i],' ==> ',a['cloudcoverpercentage'][i]
        counter+=1
    return Result
