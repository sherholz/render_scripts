'''
Created on 20.11.2015

@author: Jirka
'''

import subprocess as sub

from config import *
from pytools import firefly, inset


def createInset( fileName, fileNameInset, x1, y1, x2, y2, exp, scale ,outputDirectory, fileNameInsetPlain ):    
    inset.createInset(fileName, outputDirectory + "/" + fileNameInset, x1, y1, x2, y2, exp, scale)
    #sub.call( ["batchToneMapper.exe", "--srgb", "-e", str( exp ), fileNameInset ] )
    #shutil.move( fileNameInsetPlain + ".png", os.path.join( outputDirectory, fileNameInsetPlain + ".png" ) )
    
def removeFireFlies( fileName, outFileName, w, threshold, exp):    
    firefly.removeFireFlies(fileName, outFileName, w, threshold, exp)



# all scenes are processed by default, uncomment the next line to change which scenes to process

scenesToProcess = [ 'necklace' ]
#scenesToProcess = ['CoronaBenchmark', 'kitchen2', 'necklace' ]
#algs = [ 'jirka', 'product', 'product_bsdf' ,'product_all', 'pt' , 'bdpt', 'gdpt', 'gdbdpt']
#algs = [ 'pt' , 'bdpt', 'gdpt', 'gdbdpt', 'product']
algs = [ 'jirka', 'product']
algs = [ 'product_ceres', 'product_em']
#algs = [ 'ref', 'pt', 'cache', 'cache_translate', 'cache_translate_256']
resultTypes = [ 'auto' ]                

folder = 'revision_spp'
#folder = 'revision_gd'
#folder = 'revision'
#folder = 'revision_translate'

folder = 'revision_ceresVsEM'


for scene in scenesToProcess:
    
    """ Reference insets """
        
    refInputDirectory = os.path.join( refDir+folder, "ref" ) 
    refInputDirectory = os.path.join( refInputDirectory, scenes[ scene ][ 'ref' ] )
   
    refPngOutputDirectory = os.path.join( os.path.join( resultsDir, "png" ), "references" )                
    refFullPathName    = os.path.join( refInputDirectory, scenes[ scene ][ 'ref' ] + "_" + refFileName )
    
    if os.path.exists( refFullPathName ):
        if not os.path.exists( refPngOutputDirectory ):
            os.makedirs( refPngOutputDirectory )
        
        #os.chdir( refInputDirectory )
        
        sub.call( ["python", "pytools\\batchToneMapper.py", "--srgb", "-e", str( scenes[ scene ][ 'exp' ]), refFullPathName ] )
        
        count = 0
        for insetCfg in scenes[ scene ][ 'insets' ]:
            count = count + 1
            fileNameInsetPlain = scene + "_inset_" + str(count)
            fileNameInset = fileNameInsetPlain + extension
            print("[INFO] Creates inset '{}'.".format( fileNameInset ))
            ((x,y), (w, h)) = insetCfg[ 'coords' ]
            createInset( refFullPathName, fileNameInset, x, y, x+w, y+h, float(insetCfg[ 'exp' ]), int(insetCfg[ 'scale' ]), refInputDirectory, fileNameInsetPlain )
    else:
        print("[WARN] Reference '{}' not found.".format( refFullPathName ))
    
    print algs
    print("[WARN] ALGOS")    
    for algorithm in algs:
        print algorithm
        inputDirectory = os.path.join( resultsDir+folder, algorithm )
        inputDirectory = os.path.join( inputDirectory, scenes[ scene ][ 'dir' ] )
        
        if os.path.exists( inputDirectory ) == False:
            print("[WARN] Scene '{}' in directory '{}' was not found!".format( scene, inputDirectory ))
            continue
        print("[INFO] Processing scene '{}' in directory {}...".format( scene, inputDirectory ))
        
        
        #outputDirectory = os.path.join( resultsDir, "png" )
        #outputDirectory = os.path.join( outputDirectory, algorithm )
        #outputDirectory = os.path.join( outputDirectory, scenes[ scene ][ 'dir' ] )
        
        outputDirectory = inputDirectory
        
        
        if os.path.exists( outputDirectory ) == False:
            os.makedirs( outputDirectory )
                
        #os.chdir( inputDirectory )
        
        for resultType in resultTypes:
            fileNamePlain   = scene + "_" + resultType
            fileName        = fileNamePlain + extension
            fullPathName    = os.path.join( inputDirectory, fileName )
            
            fffileNamePlain   = scene + "_" + "ff"
            fffileName        = fffileNamePlain + extension
            fffullPathName    = os.path.join( inputDirectory, fffileName )            
            
            if os.path.exists( fullPathName ) == False:
                #print("[WARN] result type {} not found".format(fullPathName))
                continue
            
            print("[INFO] Result: '{}'".format( fileName ))

            sub.call( ["python", "pytools\\batchToneMapper.py", "--srgb", "-e", str( scenes[ scene ][ 'exp' ]), fullPathName ] )
            #shutil.move( fileNamePlain + ".png", os.path.join( outputDirectory, fileNamePlain + ".png" ) )
            
            """ FIRE FLIES """            
            
            #removeFireFlies(fullPathName,fffullPathName, 3, 4, float(scenes[ scene ][ 'exp' ]))
            
            """ INSETS """
            
            count = 0
            for insetCfg in scenes[ scene ][ 'insets' ]:
                count = count + 1
                fileNameInsetPlain = scene + "_" + algorithm + "_inset_" + str(count)
                fileNameInset = fileNameInsetPlain + extension
                print("[INFO] Creates inset '{}'.".format( fileNameInset ))
                ((x,y), (w, h)) = insetCfg[ 'coords' ]
                createInset( fullPathName, fileNameInset, x, y, x+w, y+h, float(insetCfg[ 'exp' ]),int(insetCfg[ 'scale' ]), outputDirectory, fileNameInsetPlain )
                                    
    print("[INFO] Scene '{}'...DONE".format( scene ))
    print("\n")
    
os.chdir( originalWorkingDir )
