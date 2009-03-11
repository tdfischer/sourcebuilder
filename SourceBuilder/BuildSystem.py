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
  STAGE_INIT, STAGE_CLEAN, STAGE_CONFIGURE, STAGE_BUILD, STAGE_INSTALL = range(5)
  STATUS_RUNNING, STATUS_FAILURE, STATUS_SUCCESS, STATUS_SKIPPED = range(4)

  def __init__(self, context):
    self.cxt = context
    self.logging = logging.getLogger("SourceBuilder.BuildSystem.%s"%self.systemName)
    self.__timers = {}
    self.__callbacks = {'stdout': [], 'stderr': [], 'progress': [], 'stage': [], 'time': []}
    
  def addCallback(self, name, callback):
    self.__callbacks[name].append(callback)
    
  def removeCallback(self, name, callback):
    self.__callbacks[name].remove(callback)
  
  def doCallback(self, name, *args, **kwargs):
    for c in self.__callbacks[name]:
        c(*args, **kwargs)
  
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
                    log.debug(line)
                    self.doCallback('stdout', line)
                if out == process.stderr:
                    log.error(line)
                    self.doCallback('stderr', line)
    for line in process.stdout.readlines():
        log.debug(line.strip())
        self.doCallback('stdout', line)
    for line in process.stderr.readlines():
        log.error(line.strip())
        self.doCallback('stderr', line)
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
    self.doCallback('stage', BuildSystem.STAGE_CLEAN, BuildSystem.STATUS_RUNNING)
    if self.clean():
      self.doCallback('stage', BuildSystem.STAGE_CLEAN, BuildSystem.STATUS_SUCCESS)
    else:
      self.doCallback('stage', BuildSystem.STAGE_CLEAN, BuildSystem.STATUS_FAILURE)
      return False
    self.doCallback('stage', BuildSystem.STAGE_CONFIGURE, BuildSystem.STATUS_RUNNING)
    if self.configure():
        self.doCallback('stage', BuildSystem.STAGE_CONFIGURE, BuildSystem.STATUS_SUCCESS)
        self.doCallback('stage', BuildSystem.STAGE_BUILD, BuildSystem.STATUS_RUNNING)
        if self.make():
            self.doCallback('stage', BuildSystem.STAGE_BUILD, BuildSystem.STATUS_SUCCESS)
            return True
        else:
            self.doCallback('stage', BuildSystem.STAGE_BUILD, BuildSystem.STATUS_FAILURE)
            return False
    else:
        self.doCallback('stage', BuildSystem.STAGE_CONFIGURE, BuildSystem.STATUS_FAILURE)
        return False
  
  def startTimer(self, name):
    self.__timers[name] = time.time()
  
  def stopTimer(self, name):
    return time.time() - self.__timers[name]
  
  def build(self):
    self.startTimer("build")
    self.doCallback('stage', BuildSystem.STAGE_INIT, BuildSystem.STATUS_RUNNING)
    if os.path.exists(self.buildDir()) == False:
        os.mkdir(self.buildDir())
    self.doCallback('stage', BuildSystem.STAGE_INIT, BuildSystem.STATUS_SUCCESS)
    if self.cxt.doConfigure:
        self.doCallback('stage', BuildSystem.STAGE_CONFIGURE, BuildSystem.STATUS_RUNNING)
        self.startTimer("configure")
        if self.configure():
            self.doCallback('time', self.stopTimer("configure"))
            self.doCallback('stage', BuildSystem.STAGE_CONFIGURE, BuildSystem.STATUS_SUCCESS)
        else:
            self.doCallback('time', self.stopTimer("configure"))
            self.doCallback('stage', BuildSystem.STAGE_CONFIGURE, BuildSystem.STATUS_FAILURE)
            if self.cxt.doRetry:
                self.doCallback('stage', BuildSystem.STAGE_CLEAN, BuildSystem.STATUS_RUNNING)
                self.startTimer("clean")
                if self.clean():
                    self.doCallback('time', self.stopTimer("clean"))
                    self.doCallback('stage', BuildSystem.STAGE_CLEAN, BuildSystem.STATUS_SUCCESS)
                else:
                    self.doCallback('time', self.stopTimer("clean"))
                    self.doCallback('stage', BuildSystem.STAGE_CLEAN, BuildSystem.STATUS_FAILURE)
                    return False
            else:
                return False
    else:
        self.doCallback('stage', BuildSystem.STAGE_CONFIGURE, BuildSystem.STATUS_SKIPPED)
    
    if self.cxt.doBuild:
        self.doCallback('stage', BuildSystem.STAGE_BUILD, BuildSystem.STATUS_RUNNING)
        self.startTimer("make")
        if self.make():
            self.doCallback('time', self.stopTimer("make"))
            self.doCallback('stage', BuildSystem.STAGE_BUILD, BuildSystem.STATUS_SUCCESS)
        else:
            self.doCallback('time', self.stopTimer("make"))
            self.doCallback('stage', BuildSystem.STAGE_BUILD, BuildSystem.STATUS_FAILURE)
            #if self.cxt.doRetry:
                #logging.info("Attempting reconfiguration")
                #self.startTimer("reconfiguration")
                #if self.reconfigure():
                    #logging.info("Reconfiguration complete. Resuming build.")
                    #logging.debug("Reconfiguration took %r seconds"%self.stopTimer("reconfiguration"))
                #else:
                    #logging.error("Reconfiguration failed. Trying to rebuild from scratch.")
                    #logging.debug("Reconfiguration took %r seconds"%self.stopTimer("reconfiguration"))
                    #if self.cleanBuild():
                        #logging.info("Clean build complete.")
                    #else:
                        #logging.error("Clean build failed.")
                        #return False
            #else:
                #logging.debug("Not retrying.")
    else:
        self.doCallback('stage', BuildSystem.STAGE_BUILD, BuildSystem.STATUS_SKIPPED)
    if self.cxt.doInstall:
        logging.info("Installing")
        self.startTimer("install")
        if self.install():
            self.doCallback('time', self.stopTimer("install"))
            self.doCallback('stage', BuildSystem.STAGE_INSTALL, BuildSystem.STATUS_SUCCESS)
        else:
            self.doCallback('time', self.stopTimer('install'))
            self.doCallback('stage', BuildSystem.STAGE_INSTALL, BuildSystem.STATUS_FAILURE)
            return False
    else:
        self.doCallback('stage', BuildSystem.STAGE_INSTALL, BuildSystem.STATUS_SKIPPED)
    self.doCallback('time', self.stopTimer("build"))
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