#!/usr/bin/python

from pyscripts.testCase import TestCase
from pyscripts.generators.generateHTMLNew import HTMLGenerator

# mitsuba config file !! needs to be adjusted !!
mtsConfig = "example_mitsuba_config"
# test case file !! replace it with your own test cases !!
testCasesFile = "test_cases/example_test_case"


# test scene
scene = "cbox_glossy"

#check the example/scens/scenes.py to set up additional scenes

prefix = "exp"

tc = TestCase(mtsConfig, prefix)

tc.loadTestCases(testCasesFile)

#sets the scene used for the test
tc.setScene(scene)
#example to run all testcases
tc.runAllTestCases(copyRef = True)

#example run a single test case
#tc.runTestCase("vol")
# copies the reference file to the result folder
#tc.copyRefenrence()

#generates the HTML comparision files
htmlGenerator = HTMLGenerator(mtsConfig, testCasesFile, prefix)
htmlGenerator.generateAll(True,False)
