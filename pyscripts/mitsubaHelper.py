import os, sys
import shutil
from pytools import diff


def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z


class RenderProfile:
    params = {}
    name = ""
    integrator = ""
    spp = 1

    def __init__(self, name, integrator, spp, params):
        self.params = params
        self.name = name
        self.integrator = integrator
        self.spp = spp


# Class for handling one mitsuba run
class MitsubaHelper:
    params = {}
    mitsubaExec = ""
    scenesFolder = ""
    commonOutputFolder = ""
    scene = ""
    test_name = ""
    tests = 0

    fileTags = []

    nCores = -1
    # nCores = 15

    def __init__(self, mitsubaPath, scenesFolder, commonOutputFolder):
        self.params = {}
	self.mitsubaPath = mitsubaPath
	if sys.platform.startswith('win'):
        	self.mitsubaExec = self.mitsubaPath + "\mitsuba.exe"
	else:
        	self.mitsubaExec = self.mitsubaPath + "/mitsuba"
        self.scenesFolder = scenesFolder
        self.commonOutputFolder = commonOutputFolder
        self.tests = 0
        print "scene folder is: " + scenesFolder

    def setNumCores(self, nCores):
        if nCores > 0:
            self.nCores = nCores
        else:
            self.nCores = -1

    def setParam(self, name, value):
        self.params[name] = value

    def setIntegrator(self, value):
        self.setParam("__INTEGRATOR__", value)

    def setOutputFolder(self, value):
        self.setParam("outputFolder", self.commonOutputFolder + "/" + value)
        self.test_name = value

    def getOutputFolder(self):
        return self.getParam("outputFolder")

    def getIntegrator(self):
        return self.getParam("__INTEGRATOR__")

    def setScene(self, scene):
        self.params = {}
        self.scene = scene

    def addFileTag(self, fileTag):
        self.fileTags.append(fileTag)

    def getParam(self, name):
        return self.params[name]

    def getParamsString(self):
        paramStr = ""
        for param in self.params.items():
            paramStr += " -D " + param[0] + "=\"" + str(param[1]) + "\""
        return paramStr

    def getParamsStringSimple(self):
        paramStr = ""
        for param in self.params.items():
            paramStr += param[0] + "=\"" + str(param[1]) + "\" \n\t\t"
        return paramStr

    def getCoreString(self):
        if int(self.nCores) >0:
            return "-p " + str(int(self.nCores))
        else:
            return ""
    def getExecuteCommand(self):
	if sys.platform.startswith('win'):
		exportLIBPATH = ""
	else:
		exportLIBPATH = "export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:" + self.mitsubaPath + " ; "
        sceneFile = self.scenesFolder + "/" + self.scene + "/" + \
                    self.scene + "_auto.xml"
        cmd = exportLIBPATH + self.mitsubaExec + " " + self.getCoreString()+ " " + self.getParamsString() + \
              " -z \"" + sceneFile + "\"  > \"" + \
              self.getOutputFolder() + "/out.txt\""
        print cmd
        return cmd

    def safeCopy(self, src, dest):
        try:
            shutil.copy2(src, dest)
        except (IOError, os.error) as why:
            print "Unable to copy " + src
        except Error as err:
            print "Unable to copy" + src

    def safeMove(self, src, dest):
        try:
            shutil.move(src, dest)
        except (IOError, os.error) as why:
            print "Unable to move " + src
        except Error as err:
            print "Unable to move" + src

    def run(self):
        self.tests += 1
        print "Executing test #" + str(self.tests) + " \"" + \
              self.test_name + "\" \n\tscene: " + \
              self.scene + " \n\tparams: \n\t\t" + self.getParamsStringSimple()
        outPutFolder = self.getOutputFolder()
        try:
            if (os.path.exists(outPutFolder)):
                print "Delete all files in the destination folder"
            if (
            os.path.isfile(outPutFolder + "/" + self.scene + "_" + "auto.exr")):  # "_"+self.getIntegrator()+".exr")):
                os.remove(outPutFolder + "/" + self.scene + "_" + "auto.exr")  # "_"+self.getIntegrator()+".exr")
                # if(os.path.isfile(outPutFolder+"/" + self.scene + "_auto.log")):
                # os.remove(outPutFolder+"/" + self.scene + "_auto.log")

            if (
            os.path.isfile(outPutFolder + "/" + self.scene + "_" + "auto.png")):  # "_"+self.getIntegrator()+".png")):
                os.remove(outPutFolder + "/" + self.scene + "_" + "auto.png")  # +self.getIntegrator()+".png")

            if (os.path.isfile(outPutFolder + "/" + "out.txt")):
                os.remove(outPutFolder + "/" + "out.txt")
            os.makedirs(self.getOutputFolder())
        except os.error:
            print "Destination directory \"" + self.getOutputFolder() + "\" already exists..."

        fileNameEXR = self.scenesFolder + "/" + self.scene + "/" + self.scene + "_" + "auto.exr"  # +self.getIntegrator()+".exr";
        # fileNameOUT = self.scenesFolder + "/" + self.scene + "/" + self.scene + "_auto.log";

        if (os.path.isfile(fileNameEXR)):
            os.remove(fileNameEXR)

        # if(os.path.isfile(fileNameOUT)):
        #    os.remove(fileNameOUT)

        os.system(self.getExecuteCommand())
        self.safeMove(self.scenesFolder + "/" + self.scene + "/" + \
                      self.scene + "_auto.exr",
                      self.getOutputFolder() + "/" + self.scene + "_" + "auto.exr")  # +self.getIntegrator()+".exr")
        # self.safeCopy(self.scenesFolder + "/" + self.scene + "/" + \
        #     self.scene + "_auto.log", self.getOutputFolder() + "/" + self.scene + "_auto.log")
        for file in os.listdir(self.scenesFolder + "/" + self.scene):
            if file.startswith(self.scene + "_auto_pass_"):
                self.safeMove(self.scenesFolder + "/" + self.scene + "/" + file, self.getOutputFolder() + "/" + file)

        for fileTag in self.fileTags:
            for file in os.listdir("./"):
                if file.startswith(fileTag):
                    self.safeMove(file, self.getOutputFolder() + "/" + file)

    def setup(self, integrator, seconds, spp):
        self.setIntegrator(integrator)
        self.setParam("sampleCount", spp)
        self.setParam("timeout", seconds)

    def runAll(self, prefix, scene, time, integrator_list, spp_table):
        self.setScene(scene)

        for integrator in integrator_list:
            self.setOutputFolder(prefix + "/" + scene + "_" + integrator)
            self.setup(integrator, time, spp_table[integrator])
            self.run()

    def runProfile(self, prefix, scene, timeout, profile, params):
        self.setScene(scene)
        self.params = params
        self.setOutputFolder(prefix + "/" + scene + "_" + profile)
        ##print profile[1]
        # self.setup(profile["integrator"],timeout,profile["spp"])
        self.run()

    def runAllProfiles(self, prefix, scene, timeout, profile_list, common_param):
        self.setScene(scene)

        for profile in profile_list:
            self.runProfile(prefix, scene, timeout, profile, merge_two_dicts(common_param, profile_list[profile]))

    def calDiff(self, prefix, scene, profile, integrator, type):
        self.setScene(scene)
        self.setOutputFolder(prefix + "/" + scene + "_" + profile)
        refFile = self.scenesFolder + "/" + self.scene + "/" + self.scene + "_ref.exr"
        fileName = self.commonOutputFolder + "/" + prefix + "/" + scene + "_" + profile + "/" + self.scene + "_" + integrator + ".exr"
        outFileName = self.commonOutputFolder + "/" + prefix + "/" + scene + "_" + profile + "/" + self.scene + "_" + integrator + "_error.exr"
        diff.diff(refFile, fileName, outFileName, type)

    def calDiffAll(self, prefix, scene, profile_list, common_param, type):
        for profile in profile_list:
            params = merge_two_dicts(profile_list[profile], common_param)
            self.calDiff(prefix, scene, profile, params["__INTEGRATOR__"], type)

            # self.setScene(scene)
            # self.setOutputFolder(prefix + "/" + scene + "_" + profile)
