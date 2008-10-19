import os
import subprocess
import BuildSystem

class AutotoolsSystem(BuildSystem.BuildSystem):
  systemName = "Autotools"
  
  def __init__(self, source, build, package):
    BuildSystem.BuildSystem.__init__(self, source, build, package)
  
  @staticmethod
  def canHandle(path):
    return os.path.exists(path+"/configure")
  
  def configure(self):
    os.chdir(self.buildDir())
    s = Settings()
    subprocess.call(self.srcDir()+"/configure --prefix=%s"%(s.packageSetting('installPrefix')))
  
  def make(self):
    subprocess.call("make")
  
  def install(self):
    subprocess.call("make install")

BuildSystem.register(AutotoolsSystem)