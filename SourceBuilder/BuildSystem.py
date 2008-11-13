# -*- coding: utf-8 -*-
import logging
from optparse import OptionGroup

registeredSystems = []

def factory(context):
  s = getSystem(context)
  if s == None:
    raise NotImplementedError, "No supported build system found for %s"%(context)
  return s(context)

def getSystem(context):
  for s in registeredSystems:
    logging.debug("Checking %s against %s"%(s, context))
    if s.canHandle(context):
      logging.info("Using %s for building"%(s))
      return s

def buildArgs(parser):
    for s in registeredSystems:
        group = OptionGroup(parser, s.systemName)
        parser.add_option_group(s.parseArgs(group))

def register(system):
  registeredSystems.append(system)

class BuildSystem:
  registeredSystems = []
  systemName = None

  def __init__(self, context):
    self.cxt = context
  
  def package(self):
    return self.cxt.name
  
  def srcDir(self):
    return self.cxt.source
  
  def buildDir(self):
    return self.cxt.build
  
  def installPath(self):
    return self.cxt.installPath
    
  @staticmethod
  def parseArgs(parser):
    parser.set_description("No options")
    return parser
  
  @staticmethod
  def canHandle(context):
    return false
    
  def cleanBuild(self):
    if self.clean():
      logging.info("Build cleaned.")
    else:
      logging.error("Cleanup failed.")
    return self.configure() and self.make()
  
  def build(self):
    if self.configure():
      logging.info("Configuration complete.")
    else:
      logging.error("Configuration failed.")
      return False
    
    if self.make():
      logging.info("Build complete.")
    else:
      logging.error("Build failed.")
      logging.info("Attempting reconfiguration")
      if self.reconfigure():
        logging.info("Reconfiguration complete. Resuming build.")
      else:
        logging.error("Reconfiguration failed. Trying to rebuild from scratch.")
        if self.cleanBuild():
          logging.info("Clean build complete.")
        else:
          logging.error("Clean build failed.")
          return False
    if self.install():
      logging.info("Installation complete.")
    else:
      logging.error("Installation failed.")
      return False
    return True
    
  def configure(self):
    pass
  
  def reconfigure(self):
    pass
  
  def make(self):
    pass
  
  def install(self):
    pass