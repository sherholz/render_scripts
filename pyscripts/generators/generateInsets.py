'''
Created on 20.11.2015

@author: Jirka
'''


import os, sys
import importlib
import shutil
import subprocess as sub
import pytools.inset as myinset
#import firefly
from config import *

def createInset( fileName, fileNameInset, x1, y1, x2, y2, exp, scale ,outputDirectory ):
    myinset.createInset( fileName, outputDirectory+ "/" + fileNameInset, x1, y1, x2, y2, exp, scale )
    #sub.call( ["batchToneMapper.exe", "--srgb", "-e", str( exp ), fileNameInset ] )
    #shutil.move( fileNameInsetPlain + ".png", os.path.join( outputDirectory, fileNameInsetPlain + ".png" ) )
    
def removeFireFlies( fileName, outFileName, w, threshold, exp):    
    firefly.removeFireFlies(fileName,outFileName, w, threshold, exp)



class InsetGenerator:
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

    def generate_scene_insets(self,scene, testCases, outputFolder, genDiffInsets):
        if self.scene_data.has_key(scene):
            sData = self.scene_data[scene]
            print "scene: ", scene, "\t testCase: ", testCases
            insets = sData["insets"]

            for testCase in testCases:
                i = 0
                fileFolder = self.test_directory + "/" + scene + "/" + testCase + "/"
                fileName = scene + "_auto.exr"
                fileOutputFolder = fileFolder
                if outputFolder != "":
                    fileOutputFolder = outputFolder
                for inset in insets:

                    #print "scene: ", scene, "\t testCase: ", testCase
                    print inset
                    coords = inset['coords']
                    insetFileName =  scene + "_" + testCase +"_inset_" + str(i) + ".exr"
                    scale = inset['scale']
                    exp = inset['exp']
                    createInset(fileFolder + fileName, insetFileName, coords[0][0], coords[0][1], coords[0][0]+coords[1][0], coords[0][1]+coords[1][1], exp, scale, fileOutputFolder)
		    if genDiffInsets:
			diffExp = sData['diffexp']
			diffFileName = scene + "_diff.exr"
			diffInsetFileName =  scene + "_" + testCase +"_inset_" + str(i) + "_diff"+".exr"
			createInset(fileFolder + diffFileName, diffInsetFileName, coords[0][0], coords[0][1], coords[0][0]+coords[1][0], coords[0][1]+coords[1][1], diffExp, scale, fileOutputFolder)
                    print fileName
                    print insetFileName
                    i += 1
                #copy full image
                exp = sData["exp"]
                fullFileName = scene + "_" + testCase + ".exr"
                createInset(fileFolder + fileName, fullFileName, 0, 0,
                            -1, -1, exp, 1, fileOutputFolder)

    def generateInsets(self, genDiffInsets = False, genPNG = False, outputFolder = ""):
        directories = self.get_immediate_subdirectories(self.test_directory)
        print directories

        if not os.path.exists(outputFolder):
            print "Create destination folder: " + outputFolder
            os.makedirs(outputFolder)

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
            self.generate_scene_insets(scene[0], scene[1], outputFolder, genDiffInsets)

        #print "testCases: ", scenes

