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

from PIL import Image

import numpy as np

def arg_median(a):
    if len(a) % 2 == 1:
        return np.where( a == np.median(a) )[0][0]
    else:
        l,r = len(a)/2 -1, len(a)/2
        left = np.partition(a, l)[l]
        right = np.partition(a, r)[r]
        return [np.where(a == left)[0][0], np.where(a==right)[0][0]]

def toSRGB( val, ev ):
    res = val * pow( 2, ev )
    if res <= 0.0031308:
        res = res * 12.92
    else:
        a = 0.055
        res = (1 + a) * pow( res, 1/2.4 ) - a
    return res
 

def isReal( v ):
    v = float(v)
    return v == v and v != float('+inf') and v != float('-inf')


#We suppose that pixels are indexed from 1
def removeFireFlies( inputFilePath, outputFilePath, w, threshold, ev):

    
    ffimg_r = None
    ffimg_g = None
    ffimg_b = None
    
    
    if not (os.path.isfile(inputFilePath) and fnmatch.fnmatch(inputFilePath, "*.exr")):
        print("[ERROR] Cannot create inset from file {}".format( inputFilePath ))
        exit( -1 )
            
    print('[INFO] Inset from file "%s"' % inputFilePath)
        
    img = oe.InputFile( inputFilePath )
    #(r, g, b) = img.channels("RGB", Imath.PixelType(Imath.PixelType.FLOAT))
    #pt = Imath.PixelType(Imath.PixelType.HALF)
    #print(img.header())
    dw = img.header()[ 'dataWindow' ]   
    
    
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    #(rc, gc, bc) = img.channels("RGB", pt)
    #(rc, gc, bc) = img.channels("RGB")
    (rc, gc, bc) = img.channels("RGB", Imath.PixelType(Imath.PixelType.FLOAT))
    channelType = numpy.float32
    
    r = numpy.fromstring(rc, dtype = channelType)
    g = numpy.fromstring(gc, dtype = channelType)
    b = numpy.fromstring(bc, dtype = channelType)
    
    #print r.shape     
    
    lum = (r+g+b)/3.0;    
    
    
    r.shape = (size[1], size[0]) # Numpy arrays are (row, col)
    g.shape = (size[1], size[0]) # Numpy arrays are (row, col)
    b.shape = (size[1], size[0]) # Numpy arrays are (row, col)
    
    lum.shape = (size[1], size[0])    
    
    #ffimg_r = numpy.array([0]*w*h, dtype = numpy.float32)
    

    ffimg_r = numpy.array([0]*size[1]*size[0], dtype = numpy.float32)
    ffimg_g = numpy.array([0]*size[1]*size[0], dtype = numpy.float32)
    ffimg_b = numpy.array([0]*size[1]*size[0], dtype = numpy.float32)
    ffimg_r.shape = (size[1], size[0]) # Numpy arrays are (row, col)
    ffimg_g.shape = (size[1], size[0]) # Numpy arrays are (row, col)
    ffimg_b.shape = (size[1], size[0]) # Numpy arrays are (row, col)   
        
        
        
    """ Check the image """
    """    
    for j in range(0, size[1]):
        for i in range(0, size[0]):        
            if not isReal( r[j, i] ) or not isReal( g[j, i] ) or not isReal( b[j, i] ):            
                print("[WARN] pixel at [%d, %d] = (%f, %f, %f) is nor real" % (i, j, r[j, i], g[j, i], b[j, i]))                            
            #resimg_r[y, x] = resimg_r[y, x] + inv_gamma(r[y, x])
            #resimg_g[y, x] = resimg_g[y, x] + inv_gamma(g[y, x])
            #resimg_b[y, x] = resimg_b[y, x] + inv_gamma(b[y, x])
            
    """
    """ Add the image to the result image""" 
    for y in range(0, size[1]):
        for x in range(0, size[0]):
            minY = max(0,y-w)
            maxY = min(size[1]-1,y+w)
            
            minX = max(0,x-w)
            maxX = min(size[0]-1,x+w)
            
            pw = maxX-minX
            ph = maxY-minY
            
            
            plum = lum[minY:maxY,minX:maxX]
            plum = numpy.reshape(plum,(pw*ph,1))            
            
            mplum = numpy.mean(plum)
            vplum = numpy.sqrt(numpy.var(plum))            
            
            pimg_r = r[minY:maxY,minX:maxX]            
            pimg_g = g[minY:maxY,minX:maxX] 
            pimg_b = b[minY:maxY,minX:maxX]             
            
            #print pimg_r.shape            
            #print pw
            #print ph
            pimg_r = numpy.reshape(pimg_r,(pw*ph))
            pimg_g = numpy.reshape(pimg_g,(pw*ph))
            pimg_b = numpy.reshape(pimg_b,(pw*ph))
            
            
            if(abs(mplum-lum[y,x])>(threshold*vplum)):
 
                ffimg_r[y,x] = numpy.median(pimg_r)
                ffimg_g[y,x] = numpy.median(pimg_g)
                ffimg_b[y,x] = numpy.median(pimg_b)
            else:
                ffimg_r[y,x] = r[y,x]
                ffimg_g[y,x] = g[y,x]
                ffimg_b[y,x] = b[y,x]



   
    dataR = ffimg_r.ravel().tostring()
    dataG = ffimg_g.ravel().tostring()
    dataB = ffimg_b.ravel().tostring()
    
    outputFileName = outputFilePath
    if not fnmatch.fnmatch(outputFilePath, "*.exr"):
        outputFileName = outputFilePath + ".exr"
    
    outputHeader = img.header()
    tmpHeader = oe.Header( size[0], size[1] )
    #outputHeader[ 'displayWindow' ] = tmpHeader[ 'displayWindow' ]
    #outputHeader[ 'dataWindow' ] = tmpHeader[ 'dataWindow' ]
    outputHeader = tmpHeader
    
    outExr = oe.OutputFile( outputFileName, outputHeader )
    outExr.writePixels({'R' : dataR, 'G' : dataG, 'B' : dataB})
    
    print("[INFO] Inset was written to file %s" % outputFileName)
    
    
    
    """ Create its tone-mapped .png version """
    prefix, dummy = os.path.splitext( outputFileName )
    outputFileName = prefix + ".png"
    
    im = Image.new( "RGB", (size[0], size[1]) )
    pix = im.load()
    for i in range( 0, size[0] ):
        for j in range( 0, size[1] ):            
            c = ( ffimg_r[ j, i ], ffimg_g[ j, i ], ffimg_b[ j, i ] )
            c = tuple( map( lambda c: min( 255, int( round( toSRGB(c,ev) * 255 ) ) ), c ) )  
            pix[ i, j ] = ( c )
    

    try:
        im.save(outputFileName)
    except IOError:
        print("[WARN] Cannot create the image '{}'".format( outputFileName ))
    
    print("[INFO] Tone-mapped version was written to file %s" % outputFileName)
    
    
    
if __name__ == '__main__':
    #createInset( "reference.exr", "inset", 0, 0, 1023, 575 )
    #exit()    
    if len(sys.argv) < 5:
        print("Usage: <inputFile> <outputFile> <x> <y> <x1> <y1> [ev]")
        print("\t\twhere x, y are coordinates of the upper left corner while x1, y1 of the lower right corner")
        print("\t\tand ev is an optional exposure value of the tone-mapped (sRGB) .png inset.")
    
    if ( len( sys.argv > 4 ) ):
        ev = float( sys.argv[5] )
    else:
        ev = 0.0
        
    removeFireFlies( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], ev )