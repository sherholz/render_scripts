'''
Created on 20.11.2015

@author: sherholz
'''

import os
import numpy
import fnmatch
import sys

from exrtools import *


def diffPosNeg(refR, refG, refB, compR, compG, compB):

    N = refR.shape[0]

    diffR = compR - refR
    diffG = compG - refG
    diffB = compB - refB

    pn = diffR+diffG+diffB
    dist = numpy.sqrt(diffR*diffR+diffG*diffG+diffB*diffB)

    pnR = numpy.zeros([N,], dtype=numpy.float32)
    pnG = numpy.zeros([N,], dtype=numpy.float32)
    pnB = numpy.zeros([N,], dtype=numpy.float32)

    pnR[pn < 0] = dist[pn < 0]
    pnG[pn > 0] = dist[pn > 0]

    print refR.shape, refG.shape, refB.shape
    print pnR.shape,  pnG.shape, pnB.shape
    return [pnR, pnG, pnB]


def diffAbsDiff(refR, refG, refB, compR, compG, compB):
    diffR = numpy.abs(refR - compR)
    diffG = numpy.abs(refG - compG)
    diffB = numpy.abs(refB - compB)

    return [diffR, diffG, diffB]


def diffRelPosNeg(refR, refG, refB, compR, compG, compB):

    N = refR.shape[0]

    relR = numpy.copy(refR)
    relG = numpy.copy(refG)
    relB = numpy.copy(refB)

    relR[relR == 0] = 1.0
    relG[relG == 0] = 1.0
    relB[relB == 0] = 1.0

    diffR = 2.0*(compR - refR)/(relR+compR)
    diffG = 2.0*(compG - refG)/(relG+compG)
    diffB = 2.0*(compB - refB)/(relB+compB)

    pn = diffR+diffG+diffB
    dist = numpy.sqrt(diffR*diffR+diffG*diffG+diffB*diffB)

    pnR = numpy.zeros([N,], dtype=numpy.float32)
    pnG = numpy.zeros([N,], dtype=numpy.float32)
    pnB = numpy.zeros([N,], dtype=numpy.float32)

    pnR[pn < 0] = dist[pn < 0]
    pnG[pn > 0] = dist[pn > 0]

    print refR.shape, refG.shape, refB.shape
    print pnR.shape,  pnG.shape, pnB.shape
    return [pnR, pnG, pnB]

# We suppose that pixels are indexed from 1
def diff(referenceFileName, compFileName, outFileName, diffType="PosNeg"):
    refFilePath = os.path.abspath(referenceFileName)
    compFilePath = os.path.abspath(compFileName)

    outFilePath = os.path.abspath(outFileName)

    if not (os.path.isfile(refFilePath) and fnmatch.fnmatch(refFilePath, "*.exr")):
        print("[ERROR] Cannot find reference file file {}".format(refFilePath))
        exit(-1)

    if not (os.path.isfile(refFilePath) and fnmatch.fnmatch(refFilePath, "*.exr")):
        print("[ERROR] Cannot find reference file file {}".format(refFilePath))
        exit(-1)

    [refR, refG, refB, refSize] = loadEXRImage(refFilePath)
    [compR, compG, compB, compSize] = loadEXRImage(compFilePath)

    # print "scale: ", scale, "\tdiscardPercentage: ", discardPercentage, "\tmetricType: ", metricType

    diffR = []
    diffG = []
    diffB = []
    if diffType == "PosNeg":
        [diffR, diffG, diffB] = diffPosNeg(refR, refG, refB, compR, compG, compB)
    elif diffType == "AbsDiff":
        [diffR, diffG, diffB] = diffAbsDiff(refR, refG, refB, compR, compG, compB)
    elif diffType == "RelPosNeg":
        [diffR, diffG, diffB] = diffRelPosNeg(refR, refG, refB, compR, compG, compB)
    else:
        print "[ERROR]: unknown diff type: " + diffType
        exit(-1)

    saveEXRImage(outFilePath, diffR, diffG, diffB, refSize)


if __name__ == '__main__':
    # createInset( "reference.exr", "inset", 0, 0, 1023, 575 )
    # exit()
    if len(sys.argv) < 5:
        print sys.argv
        print "Usage: <filename1> <filename2> <outfilename> <\"PosNeg\"|\"AbsDiff\"> "        # print("\t\twhere x, y are coordinates of the upper left corner while x1, y1 of the lower right corner")
        # print("\t\tand ev is an optional exposure value of the tone-mapped (sRGB) .png inset.")

    else:
        # calcMSE( sys.argv[1], sys.argv[2], )
        # calcMSE("../example/CoronaBenchmark_ref.exr", "../example/CoronaBenchmark_our.exr", 0, 1.0, "MSE")
        # print sys.argv
        diff(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        # compare("../example/CoronaBenchmark_ref.exr", "../example/CoronaBenchmark_our.exr", 1.0, 10.0, "RMSE")
