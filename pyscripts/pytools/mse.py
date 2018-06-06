'''
Created on 20.11.2015

@author: Jirka
'''

import OpenEXR as oe
import Imath
import os
import numpy
import fnmatch
import sys


import math
import subprocess
import time
import shutil

from PIL import Image


#We suppose that pixels are indexed from 1
def calcMSE( referenceFileName, fileName, scale,discardPercentage,metricType):
    
    #metricType = "MSE"
    #discardPercentage = "1.0"
    scriptDir, scriptName = os.path.split( os.path.realpath(__file__) )
    print( "[INFO] Processing file '{}'... ".format( os.path.abspath( fileName ) ) )
    mse, error = subprocess.Popen([scriptDir + os.path.sep + "bin" + os.path.sep + "mse.exe",os.path.abspath( referenceFileName ), os.path.abspath( fileName ),  metricType, discardPercentage, str(scale)],stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
    print error
    print "test"
    #ofile = open( outputDir + os.path.sep + resultType + "_errors.txt", 'w' )
    print mse
    print( "MSE:  %f" %float( mse ))
    print( "RMSE: %f" % math.sqrt( float( mse ) )  )
    
    #print("[INFO] Tone-mapped version was written to file %s" % outputFileName)
    
    return mse
    
if __name__ == '__main__':
    #createInset( "reference.exr", "inset", 0, 0, 1023, 575 )
    #exit()    
    if len(sys.argv) < 2:
        print("Usage: <inputFile> <outputFile> <x> <y> <x1> <y1> [ev]")
        print("\t\twhere x, y are coordinates of the upper left corner while x1, y1 of the lower right corner")
        print("\t\tand ev is an optional exposure value of the tone-mapped (sRGB) .png inset.")
    
        
    calcMSE( sys.argv[1], sys.argv[2])