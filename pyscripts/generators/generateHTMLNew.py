#!/usr/bin/python

import os, sys
import importlib
import shutil
import random

#scene_directory = "../scenes"
#test_directory = "results/guidedVolTestAll"
tools_directory = "generateHTMLtools"

default_conversion = "-e 0 --srgb"
convert_tool = "python pyscripts/pytools/batchToneMapper.py"
diff_tool = "python pyscripts/pytools/diff.py"
"""
conversion_table = {
                    "cbox_glossy": "-e 0 --srgb",
			"cube": "-e 0 --srgb",
			"nebulae_spot": "-e 2 --srgb",
			"nebulae_spot_60": "-e 2 --srgb",
                    }

algorithm_table = {
	"path": "Vanilla path-tracing",
	"bdpt": "Bidirectional path-tracing",
	"volpath": "Vanilla volumetric path-tracing",
	"guided_volpath": "Guided volumetric path-tracing",
	"guided_volpath_eightbin": "Guided volumetric path-tracing (histogram)",
	"guided_volpath_vmfm": "Guided volumetric path-tracing (vMF mixture)",
	"ref": "reference image",
	"a": "distance sampling, grid cache (64^3), prior initialization",
	"b": "distance sampling, grid cache (64^3), without prior initialization",
	"c": "directional+distance sampling, grid cache (64^3), prior initialization, eightBin",
	"d": "standard transmittance based sampling",
	"e": "directional sampling, grid cache (64^3), eightBin",


}
"""
unique = 0

class HTMLGenerator:

    def __init__(self, mtsConfig, testCases, prefix):
        # adds the folder of the mitsuba config to the path
        sys.path.append(os.path.dirname(mtsConfig))
        # imports the mitsuba config file and creates an instance of the
        # MitsubaConfig class
        mcMod = importlib.import_module(os.path.basename(mtsConfig))
        config = mcMod.MitsubaConfig()

        self.scene_path = config.scene_path
        print self.scene_path
        #adds the scene folder to the path and loads the scene information data
        sys.path.append(os.path.dirname(self.scene_path+"/scenes"))
        sceneMod = importlib.import_module(os.path.basename(self.scene_path+"/scenes"))
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

    def copy_reference(self, scenes):
        print scenes

        for scene in scenes.items():
            #print self.scene_data[scene[0]]["ref"]
            outPutFolder = self.test_directory + "/" + scene[0] + "/" + "ref"
            if not os.path.exists(outPutFolder):
                os.makedirs(outPutFolder)
                # add "ref" to the algorithm list
                # scene[1].append("ref")
            sceneRefImageName =  scene[0] + "_ref"
            if self.scene_data[scene[0]].has_key("ref"):
                sceneRefImageName = self.scene_data[scene[0]]["ref"]
            refImage = self.scene_directory + "/" + scene[0] + "/" +sceneRefImageName + ".exr"
            outImage = outPutFolder + "/" + scene[0] + "_auto.exr"

            self.copy(refImage, outImage)
        print scenes

    def convert_to_png(self, scenes, convertDiff):
        for scene in scenes.items():
            for algorithm in scene[1]:
                resultFile = self.test_directory + "/" + scene[0] + "/" + algorithm + "/" + scene[0] + "_auto.exr";
                diffFile = self.test_directory + "/" + scene[0] + "/" + algorithm + "/" + scene[0] + "_diff.exr";
                #scene_name = scene[0].lower();
		scene_name = scene[0]
                conversion_param = default_conversion;
                if self.scene_data.has_key(scene_name):
                    sData = self.scene_data[scene_name]
                    #print sData
                    if sData.has_key("exp"):
                        conversion_param = "-e " + str(sData["exp"]) + " --srgb"
                print "Converting: " + resultFile + " with param " + conversion_param;
                os.system(convert_tool + " " + conversion_param + ' "' + resultFile + '"');
                if convertDiff:
                    sData = self.scene_data[scene_name]
                    #print sData
                    if sData.has_key("diffexp"):
                        conversion_param = "-e " + str(sData["diffexp"]) + " --srgb"
                    print "Converting: " + resultFile + " with param " + conversion_param;
                    os.system(convert_tool + " " + conversion_param + ' "' + diffFile + '"');


    def calculate_diff(self, scenes, diffType = "PosNeg"):
        for scene in scenes.items():
            for algorithm in scene[1]:
                resultImage = self.test_directory + "/" + scene[0] + "/" + algorithm + "/" + scene[0] + "_auto.exr"
                #refImage = scene_directory + "/" + scene[0] + "/" + scene[0] + "_ref.exr"
                refImage = self.test_directory + "/" + scene[0] + "/" + "ref" + "/" + scene[0] + "_auto.exr"
                diffImage = self.test_directory + "/" + scene[0] + "/" + algorithm + "/" + scene[0] + "_diff.exr"
                print resultImage
                print refImage
                #scene_name = scene[0].lower()
		scene_name = scene[0]
                #conversion_param = default_conversion
                #if (conversion_table.has_key(scene_name)):
                #    conversion_param = conversion_table[scene_name]
                print "Diff: " + refImage + " with " + resultImage
                cmd = diff_tool + ' "' + refImage + '" "' + resultImage + '" "' + diffImage + '" ' + '"' + diffType + '"'
                print cmd
                os.system(cmd)


    def copy(self, src, dest):
        try:
            shutil.copy2(src, dest)
        except (IOError, os.error) as why:
            print "Unable to copy " + src + " to " + dest
        except Error as err:
            print "Unable to copy " + src + " to " + dest


    def copy_html_support_files(self):
        try:
            os.makedirs(self.test_directory + "/js")
        except os.error:
                print "Destination directory \"" + self.test_directory + "/js" + "\" already exists..."
        self.copy(tools_directory + "/html_support/js/jquery.min.js", self.test_directory + "/js/jquery.min.js");
        self.copy(tools_directory + "/html_support/js/jquery-ui.min.js", self.test_directory + "/js/jquery-ui.min.js");
        self.copy(tools_directory + "/html_support/js/jquery.comp.js", self.test_directory + "/js/jquery.comp.js");
        self.copy(tools_directory + "/html_support/js/jquery.comp2.js", self.test_directory + "/js/jquery.comp2.js");
        self.copy(tools_directory + "/html_support/js/plotly-latest.min.js", self.test_directory + "/js/plotly-latest.min.js");
        self.copy(tools_directory + "/html_support/style.css", self.test_directory + "/style.css");


    def getLinesBetweenTags(lines, tag, outLines):
        started = 0
        for line in lines:
            if started == 1:
                if line.startswith('<</' + tag):
                    return
                outLines.append(line)
            else:
                if line.startswith('<<' + tag):
                    started = 1


    def readConfig(configFile, outNormalization, outConfig, outStats, outPhotonStats, outRendering):
        # Open a config file and read it
        fo = open(configFile, "r+")
        config = fo.read();
        fo.close()
        # Parse config file
        lines = config.splitlines();
        # Get configuration
        getLinesBetweenTags(lines, 'CONFIG', outConfig)
        # Get stats
        temp = []
        getLinesBetweenTags(lines, 'ALGORITHM_STATS', temp)
        chain = 1
        while (1):
            temp2 = []
            getLinesBetweenTags(temp, 'CHAIN #' + str(chain), temp2)
            if len(temp2) == 0:
                break
            outStats.append(temp2)
            chain += 1
        # Get photon stats
        getLinesBetweenTags(lines, 'PHOTON_STATS', outPhotonStats)
        # Get normalization
        temp = []
        getLinesBetweenTags(lines, 'ALGORITHM_STATS', temp)
        iter = 0
        while (1):
            temp2 = []
            getLinesBetweenTags(lines, 'ITERATION' + str(iter), temp2)
            if len(temp2) == 0:
                break
            for line in temp2:
                if (len(line) == 0):
                    continue;
                splitted = line.split(':');
                if (splitted[0].find("normalization") != -1):
                    if (outNormalization.has_key(splitted[0])):
                        outNormalization[splitted[0]].append(splitted[1])
                    else:
                        outNormalization[splitted[0]] = [splitted[1]]
            iter += 1
        # Get rendering
        getLinesBetweenTags(lines, 'RENDERING', outRendering)


    def printConfigurationAndStats(configLines, statLines, photonStatLines, renderingLines):
        html_str = "<table class='config'>"
        html_str += "<tr celspan='2'><th><b>RENDERING</b></th></tr>"
        for line in renderingLines:
            if (len(line) == 0):
                continue
            c = line.find(':')
            html_str += "<tr><td><b>" + line[0:c] + "</b></td><td>" + line[c + 1:] + "</td></tr>";
        html_str += "<tr celspan='2'><th><b>CONFIGURATION</b></th></tr>"
        for line in configLines:
            if (len(line) == 0):
                continue
            c = line.find(':')
            html_str += "<tr><td><b>" + line[0:c] + "</b></td><td>" + line[c + 1:] + "</td></tr>";
        html_str += "<tr celspan='2'><th><b>ALGORITHM STATS</b></th></tr>"
        cnt = 1
        for chain in statLines:
            for line in chain:
                if (len(line) == 0):
                    continue
                c = line.find(':')
                html_str += "<tr><td><b>Chain #" + str(cnt) + " - " + line[0:c] + "</b></td><td>" + line[c + 1:] + "</td></tr>";
            cnt += 1
        html_str += "<tr celspan='2'><th><b>PHOTON STATS</b></th></tr>"
        for line in photonStatLines:
            if (len(line) == 0):
                continue
            c = line.find(':')
            html_str += "<tr><td><b>" + line[0:c] + "</b></td><td>" + line[c + 1:] + "</td></tr>";
        html_str += "</table>"
        return html_str


    def normalizationGraph(normalization):
        global unique
        unique += 1
        html_str = "<div id='myDiv" + str(unique) + "' style='width: 480px; height: 400px;'></div><script>"
        html_str += "var data = ["
        for items in normalization.items():
            html_str += "{ y: ["
            for value in items[1]:
                html_str += value + ', '
            html_str = html_str[0:len(html_str) - 2];
            html_str += "], type: 'scatter', name: '" + items[0] + "' }, ";
        html_str = html_str[0:len(html_str) - 2];
        html_str += "]; Plotly.newPlot('myDiv" + str(unique) + "', data);</script>"
        return html_str


    def write_comparison_html(self, scene, algorithms, compareWithRef):

        scene_beauty_name = scene
        if self.scene_data.has_key(scene):
            sData = self.scene_data[scene]
            if sData.has_key("beauty name"):
                scene_beauty_name = sData["beauty name"]

        # Html header
        html_str = """
      <!DOCTYPE html PUBLIC "-/W3C/DTD XHTML 1.0 Strict/EN" "http:/www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http:/www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <head>
            <title>
      """
        html_str += "Comparison of " + scene_beauty_name
        html_str += """
            </title>
            <meta http-equiv="content-Type" content="text/html; charset=utf-8" />
            <link rel="stylesheet" href="style.css" type="text/css" media="screen" />
            <script type="text/javascript" src="js/jquery.min.js"></script>
            <script type="text/javascript" src="js/jquery-ui.min.js"></script>
            <script type="text/javascript" src="js/jquery.comp.js"></script>
            <script type="text/javascript" src="js/jquery.comp2.js"></script>
            <script type="text/javascript" src="js/plotly-latest.min.js"></script>
        </head>
        """
        html_str += "   <body>\n"
        html_str += "       <div id='content'>\n"
        html_str += "           <h1 style='text-align:center'>"
        html_str += "Comparison of " + scene_beauty_name + "</h1>\n"

        if self.test_case_description != "":
            html_str += "           <h2 style='text-align:center'>"
            html_str += self.test_case_description + "</h2>\n"

        # Algorithms shortcuts
        html_str += "           <table class='shortcuts'>\n"
        for alg in algorithms:
            alg_description = "UNKNOWN"
            #if self.test_cases.has_key(alg.lower()):
            if self.test_cases.has_key(alg):
                #alg_description = self.test_cases[alg.lower()]["description"]
                alg_description = self.test_cases[alg]["description"]
            elif alg.lower() == "ref":
                alg_description = "reference"

            html_str += "           <tr>\n"

            html_str += "<td>\n<b>" + alg + "</b>\n</td>\n<td> " + alg_description + " </td>\n"
            html_str += "</tr>\n"
        html_str += "</table>\n"

        html_str += "<table>\n"
        html_str += "\t<tr>\n"
        html_str += "\t\t<td>\n"

        # Comparison
        html_str += "\t\t\t<div class='comp'>\n"
        for alg in algorithms:
            html_str += "\t\t\t\t<img src='" + scene + "/" + alg + "/" + scene + "_auto.png' alt='"
            html_str += alg;
            html_str += "'/>\n";
        html_str += "\t\t\t</div>\n"
        html_str += "\t\t</td>\n"

        if compareWithRef:
            # Diff
            html_str += "\t\t<td>\n"
            html_str += "\t\t\t<div class='comp'>\n"
            for alg in algorithms:
                html_str += "\t\t\t\t<img src='" + scene + "/" + alg + "/" + scene + "_diff.png' alt='"
                html_str += alg
                html_str += "'/>\n"
            html_str += "\t\t\t</div>\n"
            html_str += "\t\t</td>\n"

        html_str += "\t</tr>\n"
        html_str += "</table>\n"



        # COMMENTED OUT GENERATION OF STATISTICS AND GRAPHS from [scene]_auto.log
        # html_str += "<h2>Log and plots of algorithm in scene " + scene + "</h2>"
        # Log and plots
        # for alg in algorithms:
        #    html_str += "<a href=#1 onclick=/"return showhide('" + alg +"');/" alt='Click to toggle'><h3>" + alg + "</h3></a><div id ='" + alg + "' style='display:none'>";
        #    outNormalization = {};
        #    outStats = [];
        #    outPhotonStats = [];
        #    outConfig = [];
        #    outRendering = [];
        #    readConfig(test_directory + "/" + scene + " " + alg + "/" + scene + "_auto.log", outNormalization, outConfig, outStats, outPhotonStats, outRendering)
        #    html_str += printConfigurationAndStats(outConfig, outStats, outPhotonStats, outRendering)
        #    html_str += normalizationGraph(outNormalization)
        #    html_str += "</div>"
        # END OF COMMENTED OUT CODE

        # Close html file
        html_str += """
            </body>
        </html>
        """
        Html_file = open(self.test_directory + "/compare_" + scene + ".html", "w")
        Html_file.write(html_str)
        Html_file.close()

    def generateAll(self, compareWithRef, copyRef = True, diffType = "PosNeg"):

        directories = self.get_immediate_subdirectories(self.test_directory)
        print directories

        scenes = self.get_scenes_from_directories(directories)
        if compareWithRef and copyRef:
            self.copy_reference(scenes)
        scenes = self.get_test_cases_from_scene_directories(scenes)
        #print directories
        ##print scenes

        if compareWithRef:
            #self.copy_reference(scenes)
            #directories = self.get_immediate_subdirectories(self.test_directory)
            self.calculate_diff(scenes, diffType = diffType)

        self.convert_to_png(scenes, compareWithRef)

        self.copy_html_support_files()
        for scene in scenes.items():
            self.write_comparison_html(scene[0], scene[1],compareWithRef)

if __name__ == '__main__':

    mtsConfig = "example/example_mitsuba_config"
    testCases = "example/example_test_case"

    prefix = "exp"

    htmlGenerator = HTMLGenerator(mtsConfig, testCases, prefix)

    htmlGenerator.generateAll(True)
