# -*- coding: utf-8 -*-
import os
import BuildSystem
import logging

class AutotoolsSystem(BuildSystem.BuildSystem):
  systemName = "Autotools"
  
  def __init__(self, args):
    BuildSystem.BuildSystem.__init__(self, args)
  
  @staticmethod
  def canHandle(context):
    return os.path.exists(context.source+"/configure") or os.path.exists(context.source+"/Makefile") or os.path.exists(context.source+"/autogen.sh")
  
  def configure(self):
    if os.path.exists(self.srcDir()+"/configure"):
        os.chdir(self.buildDir())
        ret = self.runCommand([self.srcDir()+"/configure", "--prefix=%s"%(self.installPath())])
        if ret == 0:
            return True
        return False
    elif os.path.exists(self.srcDir()+"/autogen.sh"):
        os.chdir(self.buildDir())
        ret = self.runCommand([self.srcDir()+"/autogen.sh", "--prefix=%s"%(self.installPath())])
        if ret == 0:
            return True
        return False
    else:
        return True
  
  def make(self):
    os.chdir(self.buildDir())
    ret = self.runCommand("make")
    if ret == 0:
        return True
    return False
  
  def install(self):
    os.chdir(self.buildDir())
    if self.cxt.sudo:
        ret = self.runCommand(["sudo","make","install"])
    else:
        ret = self.runCommand(["make","install"])
    if ret == 0:
        return True
    return False
  
  def clean(self):
    os.chdir(self.buildDir())
    ret = self.runCommand(["make","distclean"])
    if ret == 0:
        return True
    ret = self.runCommand(["make", "clean"])
    if ret == 0:
        return True
    return False

BuildSystem.register(AutotoolsSystem)