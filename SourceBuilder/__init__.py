import os
from iniparse import SafeConfigParser
import logging
import BuildSystem

import CMake
import Autotools

__all__ = [
  "BuildContext",
  #"BuildSystem",
  #"CMake",
  #"Autotools",
  "builder"
]

buildLogger = logging.getLogger("SourceBuilder")

class Settings(SafeConfigParser):
  def __init__(self):
    SafeConfigParser.__init__(self)
    self.read(os.getenv("HOME")+"/.pybuildrc")

  def reload(self):
    self.read(os.getenv("HOME")+"/.pybuildrc")

  def save(self):
    f = open(os.getenv("HOME")+"/.pybuildrc","w")
    self.write(f)
    f.close()

  def packageSetting(self, key):
    if (self.has_section(self.package) and self.has_option(self.package, key)):
      return self.get(self.package, key)
    return self.get('defaults', key, vars={"package": self.package});

class PackageSettings(SafeConfigParser):
  def __init__(self, package):
    SafeConfigParser.__init__(self, {'package': package})
    self.package = package
    self.read(os.getenv("HOME")+"/.pybuildrc")

  def reload(self):
    self.read(os.getenv("HOME")+"/.pybuildrc")

  def save(self):
    f = open(os.getenv("HOME")+"/.pybuildrc","w")
    self.write(f)
    f.close()

  def get(self, key):
    if (self.has_section(self.package) and self.has_option(self.package, key)):
      return SafeConfigParser.get(self, self.package, key)
    return SafeConfigParser.get(self, 'defaults', key);

class BuildContext:
  def __init__(self, target):
    self.source = target
    if os.path.isfile(self.source):
      raise NotImplementedError, "Currently, only building the current directory or configured packages is supported"
    s = Settings()
    if os.path.isdir(self.source):
      packageName = self.source.replace(s.get('pybuildrc','projectDir'), '').split('/')[1]
      self.s = PackageSettings(packageName)
      self.package = packageName
      self.build = self.s.get('buildDir')
    #else:
      
  
  def sourceDir(self):
    return self.source
  
  def buildDir(self):
    return self.build
  
  def __str__(self):
    return self.sourceDir()

def builder(source):
  return BuildSystem.factory(BuildContext(source))

def build():
  s = Settings()
  sourceDir = os.getcwd()
  packageName = os.getcwd().replace(s.get('pybuildrc','projectDir'), '').split('/')[1]
  Settings.package = packageName
  buildDir=s.get('pybuildrc','buildDir')+'/'+packageName+s.get('pybuildrc','suffix')
  if os.path.exists(buildDir) == False:
    os.mkdir(buildDir)
  os.chdir(buildDir)
  buildClass = BuildSystem.get(sourceDir)
  builder = buildClass(source=sourceDir, build=buildDir, package=packageName)
  logging.debug("Using %s build system", builder)
  logging.debug("Switching to %s", buildDir)
  logging.info("Building %s", packageName)
  builder.build()