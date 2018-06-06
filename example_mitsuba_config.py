#!/usr/bin/python


import os, sys
import shutil


class MitsubaConfig:
    # Common settings


    scene_path = "./scenes"
    out_path = "./results"

    mitsuba_path = ""

    def __init__(self):

        if sys.platform.startswith('win'):
            # mitsuba_path = os.environ['MITSUBADIR']+"/mitsuba.exe"
            self.mitsuba_path = "mitsuba\dist"
        else:
            # mitsuba_path = "$HOME/mitsuba/dist/mitsuba"
            self.mitsuba_path = "./mitsuba/dist/release"
        print "mitsuba path is: " + self.mitsuba_path
        print "scene folder is: " + self.scene_path
        print "output folder is: " + self.out_path


        ###class RenderProfile:
