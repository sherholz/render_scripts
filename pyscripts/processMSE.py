# -*- coding: utf-8 -*-
"""
Created on Wed May 18 17:37:22 2016

@author: sherholz
"""

'''
Created on 20.11.2015

@author: Jirka
'''

import math

import numpy as np
import pandas as pd

from config import *
from pytools import mse


def calcMSE( refFileName, fileName):    
    mse.createInset(refFileName, fileName)
    #sub.call( ["batchToneMapper.exe", "--srgb", "-e", str( exp ), fileNameInset ] )
    #shutil.move( fileNameInsetPlain + ".png", os.path.join( outputDirectory, fileNameInsetPlain + ".png" ) )
    


# all scenes are processed by default, uncomment the next line to change which scenes to process
# scenesToProcess = [ 'veach_door_v050', 'cryteksponza' ]
#scenesToProcess = [ 'veach_door_original', 'veach_door_v050' ]
#scenesToProcess = [ 'veach_door_original', 'hachibox' ]
#scenesToProcess = [ 'hachibox' ]
#algs = [ 'pt' ]
#scenesToProcess = [ 'veach_door_original' ]

# uncomment the following lines to produce sponza results after 20 minutes 
#scenesToProcess = [ 'cryteksponza' ]
#algs = [ 'pt' ]
#resultTypes = [ 'adrrs',
#                'guided_adrrs_0020',                
#                'guided_0020',
#                'guided_adrrs_nosplit_0020' ]
                
# uncomment the following lines to produce demonstration of wwsize parameter on veach_door_v050 scene
# we suppose that the results were already shifted   
#scenesToProcess = [ 'veach_door_v050' ]
#scenesToProcess = [ 'CoronaBenchmark', 'kitchen2' ]
scenesToProcess = ['CoronaBenchmark', 'kitchen2', 'necklace' ]
algs = [ 'pt', 'bdpt','jirka', 'product', 'product_bsdf' ,'product_all' ]
resultTypes = [ 'auto' ]                

folder = 'revision'


#scenesToProcess = [ 'kitchen2' ]
#scenesToProcess = [ 'cbox_glossy_2' ]
scenesToProcess = [ 'kitchen' ]
#scenesToProcess = ['CoronaBenchmark', 'kitchen2', 'necklace' ]
#algs = [ 'jirka', 'product', 'product_bsdf' ,'product_all', 'pt' , 'bdpt', 'gdpt', 'gdbdpt']
#algs = [ 'pt' , 'bdpt', 'gdpt', 'gdbdpt']
algs = [ 'jirka', 'product']
#algs = [ 'pt', 'cache', 'cache_translate', 'cache_translate_256']
resultTypes = [ 'auto' ]                

folder = 'revision_spp'


# uncomment the following lines to produce demonstration of wwsize parameter on veach_door_v050 scene
# we suppose that the results were already shifted   
#scenesToProcess = [ 'veach_door_v050' ]
#scenesToProcess = [ 'kitchen2' ]
#scenesToProcess = [ 'cbox_glossy_2' ]
#scenesToProcess = [ 'kitchen2' ]
#scenesToProcess = [ 'kitchen' ]
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


nmse = np.zeros([len(scenesToProcess),len(algs)])
nrmse = np.zeros([len(scenesToProcess),len(algs)])

nrelmse = np.zeros([len(scenesToProcess),len(algs)])
nrelrmse = np.zeros([len(scenesToProcess),len(algs)])
i = 0
for scene in scenesToProcess:
    
    """ Reference insets """
    refInputDirectory = os.path.join( refDir+folder, "ref" ) 
    refInputDirectory = os.path.join( refInputDirectory, scenes[ scene ][ 'ref' ] )
   
    refPngOutputDirectory = os.path.join( os.path.join( resultsDir, "png" ), "references" )                
    refFullPathName    = os.path.join( refInputDirectory, scenes[ scene ][ 'ref' ] + "_" + refFileName )
    
    
    j = 0;
    for algorithm in algs:
        inputDirectory = os.path.join( resultsDir+folder, algorithm )
        inputDirectory = os.path.join( inputDirectory, scenes[ scene ][ 'dir' ] )
        
        if os.path.exists( inputDirectory ) == False:
            print("[WARN] Scene '{}' in directory '{}' was not found!".format( scene, inputDirectory ))
            continue
        print("[INFO] Processing scene '{}' in directory {}...".format( scene, inputDirectory ))
        
        
        outputDirectory = os.path.join( resultsDir, "png" )
        outputDirectory = os.path.join( outputDirectory, algorithm )
        outputDirectory = os.path.join( outputDirectory, scenes[ scene ][ 'dir' ] )
        
        outputDirectory = inputDirectory
        
        
        scale = math.pow(2.0,float(str( scenes[ scene ][ 'exp' ])))         
        
        if os.path.exists( outputDirectory ) == False:
            os.makedirs( outputDirectory )

        
        for resultType in resultTypes:
            fileNamePlain   = scene + "_" + resultType
            fileName        = fileNamePlain + extension
            fullPathName    = os.path.join( inputDirectory, fileName )
            tmpMSE = mse.calcMSE(refFullPathName, fullPathName, scale, str(0.3), "MSE")
            nmse[i,j] = float(tmpMSE);
            nrmse[i,j] = math.sqrt( float( tmpMSE ) ) ;
            
            tmpRelMSE = mse.calcMSE(refFullPathName, fullPathName, scale, str(0.3), "MSER")
            nrelmse[i,j] = float(tmpRelMSE);
            nrelrmse[i,j] = math.sqrt( float( tmpRelMSE ) ) ;            
            
            #mse.calcMSE(refFullPathName,fullPathName, 1.0) 
        j+=1;    
            
    i+=1;        
    print("[INFO] Scene '{}'...DONE".format( scene ))
    print("\n")

df = pd.DataFrame(nmse, index=scenesToProcess, columns = algs)
df.to_csv(refDir+folder+"/mse.csv", index=True, header=True, sep=',')

df = pd.DataFrame(nrmse, index=scenesToProcess, columns = algs)
df.to_csv(refDir+folder+"/rmse.csv", index=True, header=True, sep=',')


df = pd.DataFrame(nrelmse, index=scenesToProcess, columns = algs)
df.to_csv(refDir+folder+"/relmse.csv", index=True, header=True, sep=',')

df = pd.DataFrame(nrelrmse, index=scenesToProcess, columns = algs)
df.to_csv(refDir+folder+"/relrmse.csv", index=True, header=True, sep=',')


os.chdir( originalWorkingDir )
