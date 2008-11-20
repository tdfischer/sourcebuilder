# -*- coding: utf-8 -*-
import logging
import os
from optparse import OptionGroup
import select
import subprocess

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
  
  def runCommand(self, *args, **kwargs):
    proc = subprocess.Popen(stdout=subprocess.PIPE, stderr=subprocess.PIPE, *args, **kwargs)
    return self.logPopen(proc)
    
  def logPopen(self, process):
    log = logging.getLogger("SourceBuilder.process.%s"%(process.pid))
    while process.poll()==None:
        (outputs,inputs,excepts) = select.select([process.stdout, process.stderr],[],[])
        for out in outputs:
            line = out.readline().strip()
            if line != "":
                log.debug(out.readline().strip())
    for out in (process.stdout,process.stderr):
        for line in out.readlines():
            log.debug(line.strip())
    return process.poll()
  
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
    if os.path.exists(self.buildDir()) == False:
        os.mkdir(self.buildDir())
    if self.cxt.doConfigure:
        logging.info("Configuring")
        if self.configure():
            logging.info("Configuration complete.")
        else:
            logging.error("Configuration failed.")
            if self.cxt.doRetry:
                logging.info("Trying to clean before trying again.")
                if self.clean():
                    logging.info("Clean complete.")
                else:
                    logging.error("Clean failed.")
                    return False
            else:
                return False
    else:
        logging.debug("Not configuring.")
    
    if self.cxt.doBuild:
        logging.info("Building")
        if self.make():
            logging.info("Build complete.")
        else:
            logging.error("Build failed.")
            if self.cxt.doRetry:
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
            else:
                logging.debug("Not retrying.")
    else:
        logging.debug("Not building.")
    if self.cxt.doInstall:
        logging.info("Installing")
        if self.install():
            logging.info("Installation complete.")
        else:
            logging.error("Installation failed.")
            return False
    else:
        logging.debug("Not installing")
    return True
    
  def clean(self):
    pass
  
  def configure(self):
    pass
  
  def reconfigure(self):
    pass
  
  def make(self):
    pass
  
  def install(self):
    pass