# -*- coding: utf-8 -*-
import logging
import os
from optparse import OptionGroup
import select
import subprocess
import time

registeredSystems = []

buildLogger = logging.getLogger("SourceBuilder.BuildSystem")

def factory(context):
  s = getSystem(context)
  if s == None:
    raise NotImplementedError, "No supported build system found for %s"%(context)
  return s(context)

def getSystem(context):
  for s in registeredSystems:
    buildLogger.debug("Checking %s against %s"%(s, context))
    if s.canHandle(context):
      buildLogger.info("Using %s for build system"%(s))
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
    self.logging = logging.getLogger("SourceBuilder.BuildSystem.%s"%self.systemName)
    self.__timers = {}
    
  def __str__(self):
    return self.systemName
  
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
                if out == process.stdout:
                    log.debug(out.readline().strip())
                if out == process.stderr:
                    log.error(out.readline().strip())
    for line in process.stdout.readlines():
        log.debug(line.strip())
    for line in process.stderr.readlines():
        log.error(line.strip())
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
  
  def startTimer(self, name):
    self.__timers[name] = time.time()
  
  def stopTimer(self, name):
    return time.time() - self.__timers[name]
  
  def build(self):
    self.startTimer("build")
    if os.path.exists(self.buildDir()) == False:
        os.mkdir(self.buildDir())
    if self.cxt.doConfigure:
        logging.info("Configuring")
        self.startTimer("configure")
        if self.configure():
            logging.info("Configuration complete.")
            logging.debug("Configuration took %r seconds"%self.stopTimer("configure"))
        else:
            logging.error("Configuration failed.")
            logging.debug("Configuration took %r seconds"%self.stopTimer("configure"))
            if self.cxt.doRetry:
                logging.info("Trying to clean before trying again.")
                self.startTimer("clean")
                if self.clean():
                    logging.info("Clean complete.")
                    logging.debug("Clean took %r seconds"%self.stopTimer("clean"))
                else:
                    logging.debug("Clean took %r seconds"%self.stopTimer("clean"))
                    logging.error("Clean failed.")
                    return False
            else:
                return False
    else:
        logging.debug("Not configuring.")
    
    if self.cxt.doBuild:
        logging.info("Building")
        self.startTimer("make")
        if self.make():
            logging.info("Build complete.")
            logging.debug("Building took %r seconds"%self.stopTimer("make"))
        else:
            logging.error("Build failed.")
            logging.debug("Building took %r seconds"%self.stopTimer("make"))
            if self.cxt.doRetry:
                logging.info("Attempting reconfiguration")
                self.startTimer("reconfiguration")
                if self.reconfigure():
                    logging.info("Reconfiguration complete. Resuming build.")
                    logging.debug("Reconfiguration took %r seconds"%self.stopTimer("reconfiguration"))
                else:
                    logging.error("Reconfiguration failed. Trying to rebuild from scratch.")
                    logging.debug("Reconfiguration took %r seconds"%self.stopTimer("reconfiguration"))
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
        self.startTimer("install")
        if self.install():
            logging.info("Installation complete.")
            logging.debug("Install took %r seconds"%self.stopTimer("install"))
        else:
            logging.error("Installation failed.")
            logging.debug("Install took %r seconds"%self.stopTimer("install"))
            return False
    else:
        logging.debug("Not installing")
    logging.debug("Entire build took %r seconds"%self.stopTimer("build"))
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