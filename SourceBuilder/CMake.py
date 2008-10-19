import os
import subprocess
import BuildSystem

class CMakeSystem(BuildSystem.BuildSystem):
  systemName = "CMake"
  
  def __init__(self, context):
    BuildSystem.BuildSystem.__init__(self, context)

  @staticmethod
  def canHandle(context):
    return os.path.exists(context.source+"/CMakeLists.txt")
    
  def configure(self):
    if not os.path.exists(self.buildDir()):
      os.mkdir(self.buildDir())
    os.chdir(self.buildDir())
    ret = subprocess.call(["cmake","-DCMAKE_INSTALL_PREFIX=%s"%(self.setting('installPrefix'))]+self.setting('cmakeArgs').split()+[self.srcDir(),])
    if ret == 0:
      return True
  
  def make(self):
    ret = subprocess.call(self.setting('make').split())
    if ret == 0:
      return True
  
  def install(self):
    ret = subprocess.call(self.setting('install').split())
    if ret == 0:
      return True

BuildSystem.register(CMakeSystem)
