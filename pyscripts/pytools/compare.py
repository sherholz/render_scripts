'''
Created on 20.11.2015

@author: sherholz
'''


import os
import numpy
import fnmatch
import sys

from exrtools import *

def compareMSE(refR, refG, refB, compR, compG, compB, scale):
    refN = refR.shape[0]
    compN = compR.shape[0]

    r = (refR - compR) * scale
    g = (refG - compG) * scale
    b = (refB - compB) * scale

    v = r * r + g * g + b * b

    return v

def compareL2(refR, refG, refB, compR, compG, compB, scale):
    refN = refR.shape[0]
    compN = compR.shape[0]

    r = (refR - compR) * scale
    g = (refG - compG) * scale
    b = (refB - compB) * scale

    v = numpy.sqrt(r * r + g * g + b * b)

    return v

def compareMSA(refR, refG, refB, compR, compG, compB, scale):
    refN = refR.shape[0]
    compN = compR.shape[0]

    r = numpy.abs(refR - compR) * scale
    g = numpy.abs(refG - compG) * scale
    b = numpy.abs(refB - compB) * scale

    v = r + g + b

    return v


def compareRelMSE(refR, refG, refB, compR, compG, compB, scale):
    refN = refR.shape[0]
    compN = compR.shape[0]

    relR = refR.copy()
    relR *= scale
    relR[relR == 0] = 1.0

    relG = refG.copy()
    relG *= scale
    relG[relG == 0] = 1.0

    relB = refB.copy()
    relB *= scale
    relB[relB == 0] = 1.0

    diffR = numpy.abs(refR - compR) * scale
    diffG = numpy.abs(refG - compG) * scale
    diffB = numpy.abs(refB - compB) * scale

    r = diffR / relR
    g = diffG / relG
    b = diffB / relB

    v = r * r + g * g + b * b

    return v


# We suppose that pixels are indexed from 1
def compare(referenceFileName, compFileName, metricType="MSE", discardPercentage=0.0, scale=1.0):
    refFilePath = os.path.abspath(referenceFileName)
    compFilePath = os.path.abspath(compFileName)

    if not (os.path.isfile(refFilePath) and fnmatch.fnmatch(refFilePath, "*.exr")):
        print("[ERROR] Cannot find reference file file {}".format(refFilePath))
        exit(-1)

    if not (os.path.isfile(compFilePath) and fnmatch.fnmatch(compFilePath, "*.exr")):
        print("[ERROR] Cannot find reference file file {}".format(compFilePath))
        exit(-1)

    [refR, refG, refB, refSize] = loadEXRImage(refFilePath)
    [compR, compG, compB, compSize] = loadEXRImage(compFilePath)


    #print refSize
    print "scale: ", scale, "\tdiscardPercentage: ", discardPercentage, "\tmetricType: ", metricType

    v = []

    if metricType == "MSE":
        v = compareMSE(refR, refG, refB, compR, compG, compB, scale)
    elif metricType == "MSA":
        v = compareMSA(refR, refG, refB, compR, compG, compB, scale)
    elif metricType == "relMSE":
        v = compareRelMSE(refR, refG, refB, compR, compG, compB, scale)
    elif metricType == "L2":
        v = compareL2(refR, refG, refB, compR, compG, compB, scale)
    else:
        print "[ERROR]: unknown metric type: " + metricType
        exit(-1)

    N = v.shape[0]
    pN = int(N * (1.0 - discardPercentage / 100.0))
    sv = numpy.sort(v)

    pv = sv[0:pN]

    print numpy.sum(pv) / float(pv.shape[0]), " "
    return numpy.sum(pv) / float(pv.shape[0])


if __name__ == '__main__':
    # createInset( "reference.exr", "inset", 0, 0, 1023, 575 )
    # exit()
    if len(sys.argv) < 6:
        print sys.argv
        print "Usage: <filename1> <filename2> <\"MSE\"|\"MSA\"|\"RMSE\"> <discard percentage [0-100]> <scale value> [ignore infs(0 = do not ignore, 1 = ignore)]"
        # print("\t\twhere x, y are coordinates of the upper left corner while x1, y1 of the lower right corner")
        # print("\t\tand ev is an optional exposure value of the tone-mapped (sRGB) .png inset.")

    else:
        # calcMSE( sys.argv[1], sys.argv[2], )
        #calcMSE("../example/CoronaBenchmark_ref.exr", "../example/CoronaBenchmark_our.exr", 0, 1.0, "MSE")
        #print sys.argv
        compare(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]))
    #compare("../example/CoronaBenchmark_ref.exr", "../example/CoronaBenchmark_our.exr", 1.0, 10.0, "RMSE")
