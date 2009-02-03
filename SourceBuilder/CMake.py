# -*- coding: utf-8 -*-
import os
import BuildSystem
import BuildContext
import copy

class CMakeSystem(BuildSystem.BuildSystem):
  systemName = "CMake"
  
  def __init__(self, context):
    BuildSystem.BuildSystem.__init__(self, context)
    self.buildContext = copy.deepcopy(self.cxt)
    self.buildContext.source = self.buildContext.build
    self.logging.debug("CMake context: %s", context)
    self.logging.debug("Real build context: %s",self.buildContext)

  @staticmethod
  def canHandle(context):
    return os.path.exists(context.source+"/CMakeLists.txt")
    
  @staticmethod
  def parseArgs(options):
    options.add_option("-d","--debug", help="Build with debugging symbols")
    options.add_option("-D","--cmake-define", default=[], dest="cmake_defines", type="string", action="append", metavar="VAR")
    return options
    
  def configure(self):
    if not os.path.exists(self.buildDir()):
      os.mkdir(self.buildDir())
    os.chdir(self.buildDir())
    ret = self.runCommand(["cmake","-DCMAKE_INSTALL_PREFIX=%s"%(self.installPath())]+self.cxt.cmake_defines+[self.srcDir(),])
    if ret == 0:
      return True
  
  def make(self):
    realBuilder = BuildSystem.factory(self.buildContext)
    return realBuilder.make()
  
  def install(self):
    realBuilder = BuildSystem.factory(self.buildContext)
    return realBuilder.install()
    
  def clean(self):
    realBuilder = BuildSystem.factory(self.buildContext)
    return realBuilder.clean()

BuildSystem.register(CMakeSystem)
