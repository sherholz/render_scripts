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
def createInset( inputFilePath, outputFilePath, x, y, x1, y1, ev, scale ):
    #inputFilePath = r"d:\Jirka\projects\importance_gitrepo\results\final\pt\CoronaBenchmark\CoronaBenchmark_guided_adrrs_nosplit.exr"
    #outputFilePath = r"d:\Jirka\projects\importance_gitrepo\results\final\pt\CoronaBenchmark\insent_test.exr"

    copyImage = False
    print "x: " ,x, "  y: ", y
    print "x1: " ,x1, "  y1: ", y1
    if x1 ==-1 and y1 ==-1:
        copyImage = True

    #We suppose that pixels are indexed from 1 but internally from 0    
    x  = x - 1
    x1 = x1 - 1
    y  = y - 1
    y1 = y1 - 1

    w = x1 - x + 1
    h = y1 - y + 1
    w = x1 - x
    h = y1 - y
    print "w: " ,w, "  h: ", h

    print "copyImage:" , copyImage
    print "Scale: ", scale

    if not copyImage and (w <= 0 or h <= 0):
        print("[ERROR] Cannot create the specified inset. Invalid input range.")
        exit(-1)
    
    resimg_r = None
    resimg_g = None
    resimg_b = None
    
    
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

    if copyImage:
        h = size[0]
        w = size[1]

    r = numpy.fromstring(rc, dtype = channelType)
    g = numpy.fromstring(gc, dtype = channelType)
    b = numpy.fromstring(bc, dtype = channelType)
    
    r.shape = (size[1], size[0]) # Numpy arrays are (row, col)
    g.shape = (size[1], size[0]) # Numpy arrays are (row, col)
    b.shape = (size[1], size[0]) # Numpy arrays are (row, col)

    """ Create the output image according to size of an first observed image """    
    if resimg_r == None and not copyImage:
        resimg_r = numpy.array([0]*w*h, dtype = numpy.float32)
        resimg_g = numpy.array([0]*w*h, dtype = numpy.float32)
        resimg_b = numpy.array([0]*w*h, dtype = numpy.float32)
        resimg_r.shape = (h, w) # Numpy arrays are (row, col)
        resimg_g.shape = (h, w) # Numpy arrays are (row, col)
        resimg_b.shape = (h, w) # Numpy arrays are (row, col)   
        
    """ Check the image """
    for j in range(0, size[1]):
        for i in range(0, size[0]):        
            if not isReal( r[j, i] ) or not isReal( g[j, i] ) or not isReal( b[j, i] ):            
                print("[WARN] pixel at [%d, %d] = (%f, %f, %f) is nor real" % (i, j, r[j, i], g[j, i], b[j, i]))                            
            #resimg_r[y, x] = resimg_r[y, x] + inv_gamma(r[y, x])
            #resimg_g[y, x] = resimg_g[y, x] + inv_gamma(g[y, x])
            #resimg_b[y, x] = resimg_b[y, x] + inv_gamma(b[y, x])

    """ Add the image to the result image"""  

    print "WW: ", w, "HH: ",h          
    if not copyImage:
        #resimg_r = r[y:y+h,x:x+w]
        #resimg_g = g[y:y+h,x:x+w]
        #resimg_b = b[y:y+h,x:x+w]
	resimg_r = r[y:y+h,x:x+w]
        resimg_g = g[y:y+h,x:x+w]
        resimg_b = b[y:y+h,x:x+w]
    else:
        resimg_r = r
        resimg_g = g
        resimg_b = b

    dataR = resimg_r.ravel().tostring()
    dataG = resimg_g.ravel().tostring()
    dataB = resimg_b.ravel().tostring()
    
    outputFileName = outputFilePath
    if not fnmatch.fnmatch(outputFilePath, "*.exr"):
        outputFileName = outputFilePath + ".exr"
    
    outputHeader = img.header()
    if not copyImage:
        tmpHeader = oe.Header( w, h )
        #outputHeader[ 'displayWindow' ] = tmpHeader[ 'displayWindow' ]
        #outputHeader[ 'dataWindow' ] = tmpHeader[ 'dataWindow' ]
        outputHeader = tmpHeader

    outExr = oe.OutputFile( outputFileName, outputHeader )
    outExr.writePixels({'R' : dataR, 'G' : dataG, 'B' : dataB})
    
    print("[INFO] Inset was written to file %s" % outputFileName)
    
    
    
    """ Create its tone-mapped .png version """
    prefix, dummy = os.path.splitext( outputFileName )
    outputFileName = prefix + ".png"
    print "resimg_r: ", numpy.shape(resimg_r), "\t w: ", w, "\t h: ",h
    
    if copyImage:   
 	    im = Image.new( "RGB", (h, w) )
	    pix = im.load()
	    for i in range( 0, w ):
		for j in range( 0, h ):
		                 
		    c = ( resimg_r[i,j ], resimg_g[i,j], resimg_b[i,j ] )
		  
		    c = tuple( map( lambda c: min( 255, int( round( toSRGB(c,ev) * 255 ) ) ), c ) )  
		    pix[j, i ] = ( c )
	    
	    im = im.resize((h*scale,w*scale),Image.NEAREST)

	    try:
		im.save(outputFileName)
	    except IOError:
		print("[WARN] Cannot create the image '{}'".format( outputFileName ))
	    
	    print("[INFO] Tone-mapped version was written to file %s" % outputFileName)
    else:
	    im = Image.new( "RGB", (w, h) )
	    pix = im.load()
	    for i in range( 0, w ):
		for j in range( 0, h ):

		    c = ( resimg_r[j,i ], resimg_g[j,i], resimg_b[j,i ] )
		    c = tuple( map( lambda c: min( 255, int( round( toSRGB(c,ev) * 255 ) ) ), c ) )  
		    pix[i, j ] = ( c )
	    
	    im = im.resize((w*scale,h*scale),Image.NEAREST)

	    try:
		im.save(outputFileName)
	    except IOError:
		print("[WARN] Cannot create the image '{}'".format( outputFileName ))
	    
	    print("[INFO] Tone-mapped version was written to file %s" % outputFileName)
    
    
if __name__ == '__main__':
    #createInset( "reference.exr", "inset", 0, 0, 1023, 575 )
    #exit()    
    if len(sys.argv) < 7:
        print("Usage: <inputFile> <outputFile> <x> <y> <x1> <y1> [ev]")
        print("\t\twhere x, y are coordinates of the upper left corner while x1, y1 of the lower right corner")
        print("\t\tand ev is an optional exposure value of the tone-mapped (sRGB) .png inset.")
    
    if ( len( sys.argv > 7 ) ):
        ev = float( sys.argv[7] )
    else:
        ev = 0.0
        
    createInset( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], ev )
