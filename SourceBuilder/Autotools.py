# -*- coding: utf-8 -*-
import os
import subprocess
import BuildSystem
import logging

class AutotoolsSystem(BuildSystem.BuildSystem):
  systemName = "Autotools"
  
  def __init__(self, args):
    BuildSystem.BuildSystem.__init__(self, args)
  
  @staticmethod
  def canHandle(context):
    return os.path.exists(context.source+"/configure") or os.path.exists(context.source+"/Makefile")
  
  def configure(self):
    if os.path.exists(self.srcDir()+"/configure"):
        os.chdir(self.buildDir())
        ret = subprocess.call([self.srcDir()+"/configure", "--prefix=%s"%(self.installPath())])
        if ret == 0:
            return True
        return False
    else:
        return True
  
  def make(self):
    os.chdir(self.buildDir())
    ret = subprocess.call("make")
    if ret == 0:
        return True
    return False
  
  def install(self):
    os.chdir(self.buildDir())
    if self.cxt.sudo:
        ret = subprocess.call(["sudo","make","install"])
    else:
        ret = subprocess.call(["make","install"])
    if ret == 0:
        return True
    return False
  
  def clean(self):
    os.chdir(self.buildDir())
    ret = subprocess.call(["make","clean"])
    if ret == 0:
        return True
    return False

BuildSystem.register(AutotoolsSystem)