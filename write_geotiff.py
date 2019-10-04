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
# Purpose: write geotiff from Ndarray 

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


# Function to write Geotiff with adding prjection and geotransformation
def GdalWrite(NRecArray,InputFileTiff,DistFileTiff):
    # NRecArray= Array of N recommendation to be written
    # InputFileTiff= Tiff File name whose projection and geotransformation will be taken to write 
    # DistFileTiff=  Destination file name to be written
    x_pixel,y_pixel=gdal.Open(InputFileTiff).ReadAsArray().shape
    #print x_pixel,y_pixel
    trans=gdal.Open(InputFileTiff).GetGeoTransform()
    proj=gdal.Open(InputFileTiff).GetProjection()
    #print trans,proj
    driver                      = gdal.GetDriverByName('GTiff')
    Outdata                     = driver.Create(str(DistFileTiff),x_pixel, y_pixel, 1,gdal.GDT_Float64)
    Outdata.SetGeoTransform(trans)
    Outdata.SetProjection(proj)
    Outdata.GetRasterBand(1).WriteArray(NRecArray.astype(float))
    Outdata                     = None
    return DistFIle
