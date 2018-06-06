import OpenEXR as oe
import Imath

import numpy
import fnmatch

from PIL import Image

def loadEXRImage(inputFilePath):
    img = oe.InputFile(inputFilePath)
    dw = img.header()['dataWindow']

    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    (rc, gc, bc) = img.channels("RGB", Imath.PixelType(Imath.PixelType.FLOAT))
    channelType = numpy.float32

    r = numpy.fromstring(rc, dtype=channelType)
    g = numpy.fromstring(gc, dtype=channelType)
    b = numpy.fromstring(bc, dtype=channelType)

    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    return [r, g, b, size]

def saveEXRImage(outputFilePath, r, g, b, size):
    print "TODO"
    dataR = r.tostring()
    dataG = g.tostring()
    dataB = b.tostring()

    outputFileName = outputFilePath
    if not fnmatch.fnmatch(outputFilePath, "*.exr"):
        outputFileName = outputFilePath + ".exr"

    tmpHeader = oe.Header(size[0], size[1])
    outputHeader = tmpHeader

    outExr = oe.OutputFile(outputFileName, outputHeader)
    outExr.writePixels({'R': dataR, 'G': dataG, 'B': dataB})

def savePNGImage(outputFilePath, r, g, b, size):
    print "TODO"
    dataR = r.tostring()
    dataG = g.tostring()
    dataB = b.tostring()

    outputFileName = outputFilePath
    if not fnmatch.fnmatch(outputFilePath, "*.png"):
        outputFileName = outputFilePath + ".png"

    w = size[0]
    h = size[1]

    im = Image.new("RGB", (w, h))
    pix = im.load()

    for i in range(0, w):
        for j in range(0, h):
            idx = j*w+i
            c = (r[idx], g[idx], b[idx])
            #c = tuple(map(lambda c: min(255, int(round(toSRGB(c, ev) * 255))), c))
            rgbR = int(round(min(255, r[idx] * 255)))
            rgbG = int(round(min(255, g[idx] * 255)))
            rgbB = int(round(min(255, b[idx] * 255)))

            pix[i, j] = ((rgbR,rgbG,rgbB))

    im = im.resize((w, h), Image.NEAREST)

    try:
        im.save(outputFileName)
    except IOError:
        print("[WARN] Cannot create the image '{}'".format(outputFileName))

    print("[INFO] Tone-mapped version was written to file %s" % outputFileName)


def mergeRGB(inputFilePathR, inputFilePathG, inputFilePathB, outputFilePathRGB):
	[rR, rG, rB, sizeR] = loadEXRImage(inputFilePathR)
	[gR, gG, gG, sizeG] = loadEXRImage(inputFilePathG)
	[bR, bG, bB, sizeB] = loadEXRImage(inputFilePathB)

	saveEXRImage(outputFilePathRGB, rR, gG, bB, sizeR)
	


def getMitsubaLog(inputFilePath):
    img = oe.InputFile(inputFilePath)
    imgHeader = img.header()
    return imgHeader["log"]


def getAnnotations(inputFilePath, annotations):
    img = oe.InputFile(inputFilePath)
    imgHeader = img.header()

    for key in annotations.keys():
    	if imgHeader.has_key(key):
		annotations[key] = imgHeader[key]
    return annotations

