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
import matplotlib.pyplot as plt
import pandas as pd

def calcMSE( refFileName, fileName, metricType, discardPercentage = 0.00, scale = 1.0):
    comp = compare.compare( refFileName, fileName, metricType, discardPercentage, scale )
    return comp

class MSEPlotGenerator:
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

    def generate_scene_plots_spp(self,scene, testCases,metricType,discardPercentage):
        if self.scene_data.has_key(scene):
            sData = self.scene_data[scene]
            print "scene: ", scene, "\t testCase: ", testCases
            #insets = sData["insets"]
            #i = 0
            #for inset in insets:

            metricTypes = ["MSE", "MSA", "relMSE", "L2"]
            #metricType = "MSE"
            plotFigureFileName = self.test_directory + "/" + scene + "/" + metricType +"_spp"+"_plot_"+scene+".png"
            lines = []
            for testCase in testCases:
                if testCase == "ref":
                    pass
                else:
                    # for metricType in metricTypes:
                    testCasePath = self.test_directory + "/" + scene + "/" + testCase + "/"
                    refCaseFileName = self.test_directory + "/" + scene + "/" + "ref" + "/" + scene + "_auto.exr"

                    filelist =os.listdir(testCasePath)
                    exrs = []
                    for afile in filelist:
                        if afile.endswith(".exr"):
                            if afile.split("_")[1].startswith("SPP"):
                                exrs.append(afile)
                    


                    data = np.zeros([len(exrs), 2])
                    i = 0 
                    for exrFile in exrs:
                        spp = exrFile.split("_")[0]
                        d = calcMSE(refCaseFileName, testCasePath+"/"+exrFile, metricType,discardPercentage)
                        data[i,0] = spp
                        data[i,1] = d
                        i+=1
                    #fileName =  scene + "_auto.exr"
                    #insetFileName =  scene + "_inset_" + str(i) + ".exr"
                    #scale = inset['scale']
                    #exp = inset['exp']
                    #createInset(fileFolder + fileName, insetFileName, coords[0][0], coords[0][1], coords[0][0]+coords[1][0], coords[0][1]+coords[1][1], exp, scale, fileFolder)
                    print data
                    data = data[data[:,0].argsort()]
                    print data

                    plotDataFileName = testCasePath + metricType +"spp"+"_plot_"+scene+".csv"
                    # treeDepth = testCase.split("_")[1]
                    line, = plt.plot(data[:,0], data[:,1], label=testCase)
                    lines.append(line)
                    # plotDataFileName = self.test_directory + "/" + scene + "/" + metricType +"_plot_"+scene+".csv"
                    plotDataFileName = testCasePath + metricType +"spp"+"_plot_"+scene+".csv"
                    df = pd.DataFrame(data)
                    df.to_csv(plotDataFileName, index=False, header=False, sep=',')
                
            plt.legend(handles=lines)
            plt.xlabel('Samples per Pixel')
            plt.ylabel("Relative MSE")
            plt.savefig(plotFigureFileName)
            plt.gcf().clear()

    def generate_scene_plots_time(self,scene, testCases, metricType,discardPercentage):
        if self.scene_data.has_key(scene):
            sData = self.scene_data[scene]
            print "scene: ", scene, "\t testCase: ", testCases
            #insets = sData["insets"]
            #i = 0
            #for inset in insets:

            metricTypes = ["MSE", "MSA", "relMSE", "L2"]
            # metricTypes = ["MSE"]
            # metricType = "relMSE"
            
            plotFigureFileName = self.test_directory + "/" + scene + "/" + metricType +"_time"+"_plot_"+scene+".png"
            lines = []
            for testCase in testCases:
                if testCase == "ref":
                    pass
                else:
                    # for metricType in metricTypes:
                    testCasePath = self.test_directory + "/" + scene + "/" + testCase + "/"
                    refCaseFileName = self.test_directory + "/" + scene + "/" + "ref" + "/" + scene + "_auto.exr"

                    filelist =os.listdir(testCasePath)
                    exrs = []
                    for afile in filelist:
                        if afile.endswith(".exr"):
                            if afile.split("_")[1].startswith("secs"):
                                exrs.append(afile)
                    


                    data = np.zeros([len(exrs), 2])
                    i = 0 
                    for exrFile in exrs:
                        time = exrFile.split("_")[0]
                        d = calcMSE(refCaseFileName, testCasePath+"/"+exrFile, metricType,discardPercentage)
                        data[i,0] = time
                        data[i,1] = d
                        i+=1
                    #fileName =  scene + "_auto.exr"
                    #insetFileName =  scene + "_inset_" + str(i) + ".exr"
                    #scale = inset['scale']
                    #exp = inset['exp']
                    #createInset(fileFolder + fileName, insetFileName, coords[0][0], coords[0][1], coords[0][0]+coords[1][0], coords[0][1]+coords[1][1], exp, scale, fileFolder)
                    print data
                    data = data[data[:,0].argsort()]
                    print data

                    plotDataFileName   = testCasePath + metricType +"_time"+"_plot_"+scene+".csv"
                    line, = plt.plot(data[:,0], np.log2(data[:,1]), label=testCase)
                    lines.append(line)
                    # plotDataFileName = self.test_directory + "/" + scene + "/" + metricType +"_plot_"+scene+".csv"
                    # plotDataFileName =testCasePath + metricType +"time"+"_plot_"+scene+".csv"
                    df = pd.DataFrame(data)
                    df.to_csv(plotDataFileName, index=False, header=False, sep=',')

            plt.legend(handles=lines)
            plt.xlabel('Time: Seconds')
            plt.ylabel(metricType)
            plt.savefig(plotFigureFileName)
            plt.gcf().clear()

    def generateMSEPlotSPP(self,genDiffInsets = False, genPNG = False, metricType = "relMSE",discardPercentage = 0.001):
        directories = self.get_immediate_subdirectories(self.test_directory)
        print directories

        scenes = self.get_scenes_from_directories(directories)
        #print "scenes: ", scenes
        #if genDiffInsets and copyRef:
        #    self.copy_reference(scenes)
        scenes = self.get_test_cases_from_scene_directories(scenes)
        print "scenes: ", scenes

        for scene in scenes.items():
            #pass
            print scene
            self.generate_scene_plots_spp(scene[0], scene[1],metricType,discardPercentage)

        #print "testCases: ", scenes

    def generateMSEPlotTime(self,genDiffInsets = False, genPNG = False, metricType = "relMSE",discardPercentage = 0.001):
        directories = self.get_immediate_subdirectories(self.test_directory)
        print directories

        scenes = self.get_scenes_from_directories(directories)
        #print "scenes: ", scenes
        #if genDiffInsets and copyRef:
        #    self.copy_reference(scenes)
        scenes = self.get_test_cases_from_scene_directories(scenes)
        print "scenes: ", scenes

        for scene in scenes.items():
            #pass
            print scene
            self.generate_scene_plots_time(scene[0], scene[1],metricType,discardPercentage)
