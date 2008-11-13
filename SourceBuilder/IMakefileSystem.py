import logging
import Autotools
import BuildSystem
import subprocess
import os

class IMakefileSystem(Autotools.AutotoolsSystem):
    @staticmethod
    def canHandle(context):
        return os.path.exists(context.source+"/Imakefile")
    
    @staticmethod
    def parseArgs(options):
        return options
    
    def configure(self):
        os.chdir(self.buildDir())
        ret = subprocess.call("xmkmf")
        return ret == 0

BuildSystem.register(IMakefileSystem)