#!/usr/bin/python

import os, sys, shutil
import importlib
import json
from mitsubaHelper import MitsubaHelper


class TestCase:
    """ Test case class for runing test cases with the mitsuba scripts.

    """

    def __init__(self, mitsuba_config, prefix):
        """ Constructor for the TestCase class. It loads a mitsuba config and sets up
        the MitsubaHelper class instance.

        :param mitsuba_config: path to the mitsuba config


        :param prefix: prefix of the folder, where the results of the test cases
                        are stored
        """

        # adds the folder of the mitsuba config to the path
        sys.path.append(os.path.dirname(mitsuba_config))
        # imports the mitsuba config file and creates an instance of the
        # MitsubaConfig class
        mcMod = importlib.import_module(os.path.basename(mitsuba_config))
        self.config = mcMod.MitsubaConfig()

        # loade scene info
        scene_path = self.config.scene_path
        # adds the scene folder to the path and loads the scene information data
        sys.path.append(os.path.dirname(scene_path + "/scenes"))
        sceneMod = importlib.import_module(os.path.basename(scene_path + "/scenes"))
        self.scene_data = sceneMod.scenes

        # sets up the MitsubaHelper
        self.mitsuba = MitsubaHelper(self.config.mitsuba_path,
                                     self.config.scene_path,
                                     self.config.out_path)
        # self.mitsuba.setNumCores(7)
        self.prefix = prefix

    def getSceneInfos(self):
        return self.scene_data

    def loadTestCases(self, testCase, script_params={}):
        """ Lodes the test case file and extracts the common parameters and
        the test case parameters.

        :param testCase: path to the test case description file

        """
        sys.path.append(os.path.dirname(testCase))
        tc = importlib.import_module(os.path.basename(testCase))
        self.common_params = tc.common_params
        self.test_cases = tc.test_cases
        self.description = tc.test_case_description

        for key in script_params:
            self.common_params[key] = script_params[key]

        self.mitsuba.setOutputFolder(self.prefix)

        testFolder = self.mitsuba.getOutputFolder()
        # generates the folder if it does not exits
        if not os.path.exists(testFolder):
            os.makedirs(testFolder)

        # store test case infos
        tInfo = {}
        tInfo["description"] = self.description

        with open(testFolder + '/test_info.json', 'w') as fp:
            json.dump(tInfo, fp, indent=True)

    def runTestCase(self, tcName, preProcess=False):
        """ Runs a given test case from the test case list for a specific scene.
        The test case is specified by its name.

        :param scene: name of the test scene
        :param tcName:  name of the test case

        """

        # gets the test case from the list
        tc = self.test_cases[tcName]

        # loads the scene
        self.mitsuba.setScene(self.m_scene)

        # loads and sets up the common parameters
        for cparam in self.common_params:
            if cparam == "__INTEGRATOR__":
                self.mitsuba.setIntegrator(self.common_params[cparam])
            else:
                self.mitsuba.setParam(cparam, self.common_params[cparam])

        # gets the test case specific parameters
        tcparams = tc['param']

        # sets up the test case specific parameters
        for tcparam in tcparams:
            if tcparam == "__INTEGRATOR__":
                self.mitsuba.setIntegrator(tcparams[tcparam])
            else:
                self.mitsuba.setParam(tcparam, tcparams[tcparam])

        # sets the output folder for the results
        # self.mitsuba.setOutputFolder(self.prefix + "/" + scene + "/" + self.mitsuba.getIntegrator() + " " + tcName)

        self.mitsuba.setOutputFolder(self.prefix + "/" + self.m_scene + "/" + tcName)

        testCaseFolder = self.mitsuba.getOutputFolder()
        # generates the folder if it does not exits
        if not os.path.exists(testCaseFolder):
            os.makedirs(testCaseFolder)

        # store test case infos
        tcInfo = {}
        tcInfo["tcName"] = tcName
        tcInfo["description"] = tc["description"]

        with open(testCaseFolder + '/test_case_info.json', 'w') as fp:
            json.dump(tcInfo, fp, indent=True)

        # starts the test case
        self.mitsuba.run()

        if preProcess:
            path = self.mitsuba.getOutputFolder()
            if os.path.exists(path):
                # remove if exists
                shutil.rmtree(path)
            else:
                print path, " does not exists"

    def setScene(self, scene):
        self.m_scene = scene

        sData = self.scene_data[scene]
        sceneInfo = {}
        sceneInfo["name"] = scene
        sceneInfo["beautyName"] = sData["beauty name"]
        sceneInfo["exp"] = sData["exp"]
        sceneInfo["diffexp"] = sData["diffexp"]
        sceneInfo["insets"] = sData["insets"]

        self.mitsuba.setOutputFolder(self.prefix + "/" + self.m_scene)
        sceneFolder = self.mitsuba.getOutputFolder()

        # generates the folder if it does not exits
        if not os.path.exists(sceneFolder):
            os.makedirs(sceneFolder)

        with open(sceneFolder + '/scene_info.json', 'w') as fp:
            json.dump(sceneInfo, fp, indent=True)

    def copyReference(self):
        sData = self.scene_data[self.m_scene]
        sFolder = sData["dir"]
        sRef = sData["ref"]

        sceneFolder = self.mitsuba.getScenesFolder() + "/" + sFolder + "/"

        self.mitsuba.setOutputFolder(self.prefix + "/" + self.m_scene + "/" + "ref")
        refOutFolder = self.mitsuba.getOutputFolder()

        # generates the folder if it does not exits
        if not os.path.exists(refOutFolder):
            os.makedirs(refOutFolder)

        self.mitsuba.safeCopy(sceneFolder + sRef + ".exr", refOutFolder + "/" + self.m_scene + "_auto.exr")

        tcInfo = {}
        tcInfo["tcName"] = "ref"
        tcInfo["description"] = "Reference"

        with open(sceneFolder + '/test_case_info.json', 'w') as fp:
            json.dump(tcInfo, fp, indent=True)

    def runAllTestCases(self, runRef=True, copyRef=False):
        """ Runs all test cases of the test case list for a specific scene.

        :param scene: the name of scene the test cases are run for
        """

        for tc in self.test_cases:
            print tc
            if tc != "ref":
                self.runTestCase(tc)
            else:
                if runRef:
                    self.runTestCase(tc)

        if copyRef:
            self.copyReference()

    def runTestCaseByIdx(self, idx):
        pass

    def getNumOftestCases(self):
        pass

    def setNumCores(self, nCores):
        """ Set the number of cpu cores/thread, which should be used
         for the test case. The default ist -1, which means all available
         cores are used.

        :param nCores: number of cores/threads (default:-1)
        """
        if nCores > 0:
            self.nCores = nCores
        else:
            self.nCores = -1

        self.mitsuba.setNumCores(self.nCores)

    def getConfig(self):
        print self.config
        return self.config


if __name__ == '__main__':
    print "test for the TestCase"
    tc = TestCase("example/example_mitsuba_config", "tc")
    tc.loadTestCases("example/example_test_case")
    tc.runTestCase('cbox_glossy', 'vol')
    tc.runAllTestCases('cbox_glossy')
