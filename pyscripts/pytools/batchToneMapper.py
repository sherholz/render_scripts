'''
Created on 20.11.2015

@author: sherholz
'''

import os
import numpy
import fnmatch
import sys

import argparse

from exrtools import *


def toSRGB(val, ev):
    tval = numpy.zeros(val.shape)
    res = val * pow(2, ev)
    tval[res <= 0.0031308] = res[res <= 0.0031308] * 12.92
    a = 0.055

    tval[res > 0.0031308] = (1 + a) * numpy.power(res[res > 0.0031308], 1 / 2.4) - a

    return tval


# def isReal(v):
#    v = float(v)
#    return v == v and v != float('+inf') and v != float('-inf')

def toneMapExp(R, G, B, ev):
    tmR = toSRGB(R, ev)
    tmG = toSRGB(G, ev)
    tmB = toSRGB(B, ev)

    return [tmR, tmG, tmB]


# We suppose that pixels are indexed from 1
def toneMap(inFileName, outFileName, exposure=0.0):
    inFilePath = os.path.abspath(inFileName)

    outFilePath = os.path.abspath(outFileName)

    if not (os.path.isfile(inFilePath) and fnmatch.fnmatch(inFilePath, "*.exr")):
        print("[ERROR] Cannot find reference file file {}".format(inFilePath))
        exit(-1)

    [inR, inG, inB, inSize] = loadEXRImage(inFilePath)

    [tmR, tmG, tmB] = toneMapExp(inR, inG, inB, exposure)

    savePNGImage(outFilePath, tmR, tmG, tmB, inSize)


if __name__ == '__main__':
    # createInset( "reference.exr", "inset", 0, 0, 1023, 575 )
    # exit()

    print sys.argv
    
    if len(sys.argv) > 2:

        parser = argparse.ArgumentParser(description='Process some integers.')

        parser.add_argument('--srgb', action='store_false')
        parser.add_argument('--exposure', '-e', default=0, type=float)
        parser.add_argument('input', nargs=1, type=str)
        parser.add_argument('output', nargs='?', default='', type=str)

        args = parser.parse_args(sys.argv[1:])

        if args.output == '':
            print args.input
            args.output = args.input[0].replace(".exr", ".png")

        toneMap(args.input[0], args.output, args.exposure)

    else:
        toneMap("../example/CoronaBenchmark_ref.exr", "../example/CoronaBenchmark_tm.png", 3)
