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

from obtain_sentinnel_product import ObtainProduct_sentinel
from shape2geojson import shapetogeojson 
from yieldpotential_algorithm import YieldPotential, PartialFactorProductivity, NUEAdj
from write_geotiff import GdalWrite


#################################Main program Begins 
os.chdir('/home/abhishes/Desktop/Abhi/Varimax_FB') # This is the directory where you have Input boundaries data from all producers
UsrName='abhilam' # this is for Sentinnel username and password
Password='' # Create sentinnel account and use password.
# Sentinnel API
api = SentinelAPI(user=UsrName, password=Password,api_url='https://scihub.copernicus.eu/dhus')

################################## Step One ########################################################
# Go to producers folder containing shape file
# convert them to geojson and put it to new folder
# Comment below section once you do first run. 
#####################################################################################################


# Initializing variable, input and path
producers='josh_lloyd' # Name of the producers folder
"""
Specify your input
"""
Input={
        'BoundryNme':  ['Braden'],
        'StartDate':   ['20170301'],
        'EndDate':     ['20170707'],
        'GrowthStage': [4]
        }

pathofInputfolder          ='/home/abhishes/Desktop/Abhi/Varimax_FB/' # Path where your allproducers folder located
PathofBoundries            ='/home/abhishes/Desktop/Abhi/Varimax_FB/'+producers+'/boundaries' # path within producers where your shapefiles are located
pathofSen2cor              ='/home/abhishes/anaconda2/envs/TEST/bin/'
pathofgdal                 ='/home/abhishes/anaconda2/bin/'

os.chdir(PathofBoundries) # work under boundary folder

########################################################################################################
# Rename all files by replacing space to hyphen 
# this process can be removed if our all shapefile names doesnt contain any spaces in between
#######################################################################################################

filenames = os.listdir(PathofBoundries)
for filename in filenames:
    try:os.rename(os.path.join(PathofBoundries, filename), os.path.join(PathofBoundries, filename.replace(' ', '-')))
    except:pass

# Now convert all shapefile to geojson as it is one of the requirement to use sentinnel package to download
ListofShapefile=glob.glob('*.shp')
for files in ListofShapefile:
    shapetogeojson(files)
    

################################## Step 2 ########################################################

#For each geojson, collect growth stage and date information
# Download sentinnel data for each geojson
# Create separate folder for each boundary
# unzip each one and move to new folder created above

#####################################################################################################

print 'My work beguin'
for i in xrange(len(Input['BoundryNme'])):
    NRecOutput_geotif          =Input['BoundryNme'][i] +'_Final_Clipped_NRec_Geotiff.tif' # name to save final Nrecommendation geotiff
    NRecOutput_No_geotif       =Input['BoundryNme'][i] +'_Final_Clipped_NRec_No_Geotiff.tif' # name to save final Nrecommendation without Geotiff
    MinCld         = 03
    MaxCld         = 100
    Sdate          = Input['StartDate'][i]
    Edate          = Input['EndDate'][i]
    JsonFileName   = Input['BoundryNme'][i]+'.geojson'
    ProductID      = ObtainProduct_sentinel(JsonFileName,Sdate,Edate,MinCld,MaxCld)
        
    # Now Download the Single data that is necessasry:
    Kind=raw_input('if you just want to download Single File, Type S \nOR\
                    \nif you want to download ALl, type A\
                    \nif youwant to download multiple type M\nType now using CAPS LOCK On :  ')
    CurntPath=os.getcwd()
    Path_to_Download=os.path.join(CurntPath,'Sentinnel_Downloaded_Files')
    if os.path.exists(Path_to_Download)==False:
        os.mkdir(Path_to_Download)
    Kind            = str(Kind)
    Decision        = 'N'
    if Kind=='S':
        while Decision=='N':
          print 'You are downloading single file'
          ID           =raw_input('Now type which Scene ID you want to download: ')
          QuickView    ="https://scihub.copernicus.eu/dhus/odata/v1/Products('"+ProductID['Pr_Id'][int(ID)]+"')/Products('Quicklook')/$value"
          fil          =StringIO(urllib.urlopen(QuickView).read())
          Img          =Image.open(fil);#Img.show()
          Img.save('abc.tif')
          Geom= ProductID['Geometry'][int(ID)]
          abc=str( Geom)
          Lon=[];Lat=[];
          for item in abc.split('(')[-1].split(')')[0].split(','):
                abcd=item.split(' ')
                try: 
                    abcd.remove('')
                except:
                     print 'Do nothing'
                Lat.append(abcd[1])
                Lon.append(abcd[0])
          Boundingbox=[min(Lon),max(Lat),min(Lon),min(Lat)]
    
          gdal.Translate('aRaster_ABC.tif', 'abc.tif',outputSRS='epsg:4326',outputBounds=list(Geom.bounds))
          DataFile='abc.tif'
          InputFile='aRaster_ABC.tif'
          DistFIle='aRaster_ABC_Final.tif'
          #GdalWrite(DataFile,InputFile,DistFIle)
          ShapefileName1                = JsonFileName.split('.')[0]+'.shp'
          gdal.Warp('aRaster_ABC_cliped.tif','aRaster_ABC.tif', cutlineDSName=ShapefileName1, dstAlpha=True)

          plt.imshow(gdal.Open('aRaster_ABC_cliped.tif').ReadAsArray()[0])
          plt.show()
          plt.imshow(gdal.Open('aRaster_ABC.tif').ReadAsArray()[0])
          plt.show()
          Identifier=ProductID['Identifier'][int(ID)]
          Decision     =raw_input('Do you think this is correct [Y or N]: ')
        os.remove('abc.tif');os.remove('aRaster_ABC.tif');os.remove('aRaster_ABC_cliped.tif')
        api.download(ProductID['Pr_Id'][int(ID)],Path_to_Download)
     
    elif Kind=='A':
        print 'You all Data is being downloading\n'
        for item in ProductID['Pr_Id']:
          api.download(item,Path_to_Download)
    elif Kind=='M':
        print 'You are downloading Multipel Scene ID'
        ID              = raw_input('Type Multipel Scene ID number separated by , eg: 1,2,5\nTypeNow: ')
        ID              = ID.split(',')
        for i in ID:
            i           = int(i)
            api.download(ProductID['Pr_Id'][i],Path_to_Download)
    
    #Now Unzip the files when downloading single file
    os.chdir(os.path.join(os.getcwd(), 'Sentinnel_Downloaded_Files'))
    abc                  = sorted(glob.glob(Identifier+'.zip'),key=os.path.getatime)
    zip_ref              = zipfile.ZipFile('./'+abc[-1], 'r');zip_ref.extractall('./');zip_ref.close()
    zipfiles             = glob.glob('*.zip')
    
    # Remove zip file
    #for zips in zipfiles:os.remove(zips)

    ############################################ STEP 3 #####################################################
    #Do the Sen2Cor correction for each safe file
    # Go to each boundary folder create above (e.g Braden_SAFE)
    # DO the Sen2cor correction
    # COpy R10 Folder and rename based on Previous FOlder    print gdal.Open(InputFileTiff).ReadAsArray()[0].shape
    #and Copy to new Final Folder
    #############################################################################################################
    print Identifier
    pathofDownloadScene       = PathofBoundries+'/Sentinnel_Downloaded_Files' # This is where downloaded sentinel scene located
    os.chdir(pathofDownloadScene)    
    SafeFoldr                 = glob.glob(Identifier+'.SAFE')
    # make sure you install sen2cor in your system https://github.com/umwilm/SEN2COR 
    # This process take quite a long time, approx 30 min.
    #from sen2cor import L2A_Process
	
    command                   = 'cd '+pathofDownloadScene+'; '+pathofSen2cor+'L2A_Process '+ SafeFoldr[0] +' --resolution 10'
    print command#dst_filename
    os.system(command)
    # Now delete L1C
    L1Cfolder                 = glob.glob('*L1*.SAFE')
    #for fold in L1Cfolder:      shutil.rmtree(fold) # uncomment this if you want to delete uncalibrated folder
    # Now go to R10 folder of L2A(calibrated) and convert .jp2 file to geotiff
    Calibrated_Safe_FileNme=Identifier.replace('L1C','L2A')
    
    try:
          foldPath                  = os.getcwd()+'/'+glob.glob(Calibrated_Safe_FileNme+'.SAFE/*/*/*/*R10*')[0]
    except:
          print 'There is not Calibrated folder or something mismatch with calibrated folder name'
          sys.exit()
    # Go to R10m folder for working directory
    os.chdir(foldPath)
    Bands                      = ['*B04*.jp2','*B08*.jp2']
    Jp2Files                   = [glob.glob(bnds)[0] for bnds in Bands] # Just converting Band 4 and 8
    #Jp2Files=glob.glob('*.jp2') if you wanted to convert all bands jp2 files
    for jp2file in Jp2Files:
        # make sure gdal >2.2 is in your system.NIR  Get your directory of gdal_translate by searching which gdal_translate in terminal
        gdal.Translate(jp2file.split('.')[0]+'.tif',jp2file,format='GTiff')
        #os.system(pathofgdal+'gdal_translate -of GTiff -co TILED=YES '+ jp2file+' '+ jp2file.split('.')[0]+'.tif')
    
    NIR                         = glob.glob('*_B08*.tif')
    RED                         = glob.glob('*_B04*.tif')   
    NIRData                     = gdal.Open(NIR[0])   
    N                           = NIRData.GetRasterBand(1).ReadAsArray()
    REDData                     = gdal.Open(RED[0])
    R                           = REDData.GetRasterBand(1).ReadAsArray()
    # Calculate NDVIjosh_lloyd
    NDVI                        = (N.astype(np.float64)-R.astype(np.float64))/(N.astype(np.float64)+R.astype(np.float64))
    NREC                        = YieldPotential(GrStage=4, NDVIRaster=NDVI)*(PartialFactorProductivity()/NUEAdj())
    dst_filename='NRec_EntireRaster.tif'
    GdalWrite(NRecArray=NREC,InputFileTiff=NIR[0],DistFileTiff=dst_filename)
    
    # Now copy shapefile to R10m folder and clip 
    shapefiles                  =glob.glob(PathofBoundries+'/'+JsonFileName.split('.')[0]+'*')
    for i in xrange(len(shapefiles)):
        try:                     shutil.copy(shapefiles[i],'./')
        except:                  pass
        
    ShapefileName                = JsonFileName.split('.')[0]+'.shp'
    
    # Now clip the ENtireNrec Raster based on boundary (shape file)
    gdal.Warp(NRecOutput_geotif,dst_filename, cutlineDSName=ShapefileName,cropToCutline=True)
    #command                      = pathofgdal+"gdalwarp -cutline "+ ShapefileName + " -crop_to_cutline "+dst_filename+' '+NRecOutput_geotif+' -overwrite'
    #os.system(command)
    
    plt.imshow(gdal.Open(NRecOutput_geotif).ReadAsArray(),cmap=plt.cm.RdYlGn);plt.colorbar()
    plt.savefig(NRecOutput_No_geotif)
    plt.show()
    # currently your images in R10m folder. if you need to move to your desired location then follow following steps.
    """
    shutil.move(NRecOutput_geotif,'pathof the folder where you want this image to be')
    shutil.move(NRecOutput_No_geotif,'pathof the folder where you want this image to be')
    # Once you copied needed map, we can delete the entire L2C folder.
    """
    
