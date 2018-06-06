'''
Created on 20.11.2015

@author: Jirka
'''


import os, sys
import importlib
import shutil
import subprocess as sub
import pytools.compare as compare
#import firefly
from config import *
import numpy as np
import pandas as pd

def calcMSE( refFileName, fileName, metricType, discardPercentage = 0.001, scale = 1.0):
    comp = compare.compare( refFileName, fileName, metricType, discardPercentage, scale )
    return comp

class MSEGenerator:
    def __init__(self, mtsConfig, testCases, prefix):
        # adds the folder of the mitsuba config to the path
        sys.path.append(os.path.dirname(mtsConfig))
        # imports the mitsuba config file and creates an instance of the
        # MitsubaConfig class
        mcMod = importlib.import_module(os.path.basename(mtsConfig))
        config = mcMod.MitsubaConfig()

        self.scene_path = config.scene_path
        print self.scene_path
        # adds the scene folder to the path and loads the scene information data
        sys.path.append(os.path.dirname(self.scene_path + "/scenes"))
        sceneMod = importlib.import_module(os.path.basename(self.scene_path + "/scenes"))
        self.scene_data = sceneMod.scenes

        sys.path.append(os.path.dirname(testCases))
        tc = importlib.import_module(os.path.basename(testCases))
        self.test_cases = tc.test_cases

        self.test_case_description = ""
        if hasattr(tc, "test_case_description"):
            self.test_case_description = tc.test_case_description

        self.test_directory = config.out_path + "/" + prefix
        self.scene_directory = config.scene_path

        print self.test_directory
        print self.scene_data
        print self.test_cases

    def get_immediate_subdirectories(self, a_dir):
        return [name for name in os.listdir(a_dir)
                if os.path.isdir(os.path.join(a_dir, name))]


    def get_scenes_from_directories(self, directories):
        scenes = {};
        for dir in directories:
            if (dir != "js"):
                """
                s = dir.split()
                if scenes.has_key(s[0]):
                    scenes[s[0]].append(s[1])
                else:
                    scenes[s[0]] = [s[1]]
                """
                print dir
                scenes[dir] = []
        return scenes

    def get_test_cases_from_scene_directories(self, scenes):
        #print scenes
        for scene in scenes:
            a_dir = self.test_directory +"/" + scene
            #print a_dir
            ts = [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]
            #print ts
            for t in ts:
                scenes[scene].append(t)
            #print scenes
        return scenes

    def generate_scene_mse(self,scene, testCases,discardPercentage):
        if self.scene_data.has_key(scene):
            sData = self.scene_data[scene]
            exp = sData["exp"]
            #insets = sData["insets"]
            #i = 0
            #for inset in insets:

            metricTypes = ["MSE", "MSA", "relMSE", "L2"]
            data = np.zeros([len(metricTypes), len(testCases)])
            i=0

            for testCase in testCases:
                j = 0
                for metricType in metricTypes:
                    testCaseFileName = self.test_directory + "/" + scene + "/" + testCase + "/"  + scene + "_auto.exr"
                    refCaseFileName = self.test_directory + "/" + scene + "/" + "ref" + "/" + scene + "_auto.exr"

                    #fileName =  scene + "_auto.exr"
                    #insetFileName =  scene + "_inset_" + str(i) + ".exr"
                    #scale = inset['scale']
                    #exp = inset['exp']
                    #createInset(fileFolder + fileName, insetFileName, coords[0][0], coords[0][1], coords[0][0]+coords[1][0], coords[0][1]+coords[1][1], exp, scale, fileFolder)

                    print testCaseFileName
                    print refCaseFileName
                    d = calcMSE(refCaseFileName, testCaseFileName, metricType, discardPercentage, scale=np.power(2.0,exp))
                    #d = calcMSE(refCaseFileName, testCaseFileName, metricType, discardPercentage, scale=1.0)
                    data[j,i] = d
                    j += 1
                i+=1
            print data
            compareFileName = self.test_directory + "/" + scene + "/" + "compare_"+scene+".csv"
            df = pd.DataFrame(data, index=metricTypes, columns = testCases)
            df.to_csv(compareFileName, index=True, header=True, sep=',')

    def generateMSE(self, genDiffInsets = False, genPNG = False, discardPercentage = 0.001):
        directories = self.get_immediate_subdirectories(self.test_directory)
        print directories

        scenes = self.get_scenes_from_directories(directories)
        #print "scenes: ", scenes
        #if genDiffInsets and copyRef:
        #    self.copy_reference(scenes)
        scenes = self.get_test_cases_from_scene_directories(scenes)
        print "scenes: ", scenes
        if genPNG:
            self.convert_to_png(scenes, genDiffInsets)

        for scene in scenes.items():
            #pass
            print scene
            self.generate_scene_mse(scene[0], scene[1],discardPercentage)

        #print "testCases: ", scenes

