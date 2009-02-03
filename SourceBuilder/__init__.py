# -*- coding: utf-8 -*-
import os
#from iniparse import SafeConfigParser
import logging
import BuildSystem
import BuildContext
from optparse import OptionParser, OptionGroup

import IMakefileSystem
import Autotools
import CMake
import DirectoryContext
import TarballContext

__all__ = [
  #"BuildContext",
  #"BuildSystem",
  #"CMake",
  #"Autotools",
  "builder"
]

buildLogger = logging.getLogger("SourceBuilder")
procLogger = logging.getLogger("SourceBuilder.process")

def setVerbosity(option, opt_str, value, parser):
  nextLevel = {logging.WARNING: logging.INFO, logging.INFO:logging.DEBUG, logging.DEBUG: logging.DEBUG}
  buildLogger.setLevel(nextLevel[buildLogger.getEffectiveLevel()])
  procLogger.setLevel(nextLevel[procLogger.getEffectiveLevel()])

def builder():
  buildLogger.setLevel(logging.INFO)
  procLogger.setLevel(logging.WARNING)
  
  parser = OptionParser(conflict_handler="resolve", usage="%prog [options] source")
  parser.set_defaults(installPath="/opt", doConfigure=True, doBuild=True, doInstall=True, doClean=False, verbose=False, doRetry=True, sudo=False, devel=False, save=True, merge=False)
  common = OptionGroup(parser, "Common Options")
  common.add_option("-d", "--devel", action="store_true", help="Build the project in development mode", dest="devel")
  common.add_option("--prefix", type="string", help="Install prefix", dest="installPath")
  common.add_option("-s","--source-path", type="string", help="Path to source", dest="source")
  common.add_option("-b","--build-path", type="string", help="Build path", dest="build")
  common.add_option("-v", "--verbose", action="callback", help="Verbose", callback=setVerbosity)
  common.add_option("-N", "--name", type="string", help="Name of project")
  common.add_option("--configure", action="store_true", help="Run configuration", dest="doConfigure")
  common.add_option("--no-configure", action="store_false", help="Don't run configuration", dest="doConfigure")
  common.add_option("--compile", action="store_true", help="Compile", dest="doBuild")
  common.add_option("--no-compile", action="store_false", help="Don't compile", dest="doBuild")
  common.add_option("--install", action="store_true", help="Install", dest="doInstall")
  common.add_option("--no-install", action="store_false", help="Don't install", dest="doInstall")
  common.add_option("-S", "--sudo", action="store_true", help="Run install with sudo", dest="sudo")
  common.add_option("--retry", action="store_true", help="Clean the build and try building again after a failure.", dest="doRetry")
  common.add_option("--no-retry", action="store_false", help="Don't clean the build before retrying", dest="doRetry")
  common.add_option("--clean", action="store_true", help="Clean the build directory", dest="doClean")
  common.add_option("--no-clean", action="store_false", help="Don't clean the build directory", dest="doClean")
  common.add_option("--save", action="store_true", help="Save these settings between runs", dest="save")
  common.add_option("--no-save", action="store_false", help="Don't save settings.", dest="save")
  common.add_option("--load", action="store_true", help="Load saved options", dest="load")
  common.add_option("--no-load", action="store_false", help="Don't load saved options", dest="load")
  common.add_option("--merge", action="store_true", help="Load user options first, with saved options overwriting them.", dest="merge")
  parser.add_option_group(common)
  BuildSystem.buildArgs(parser)
  BuildContext.buildArgs(parser)
  (options,args) = parser.parse_args()
  if len(args) > 0:
      options.source = args.pop()
  if options.source == None:
      options.source = os.getcwd()
  cxt = BuildContext.factory(options)
  try:
    cxt.load()
  except NotImplementedError:
    buildLogger.warn("Loading options not supported.")
  try:
    cxt.save()
  except NotImplementedError:
    buildLogger.warn("Saving options not supported.")
  return BuildSystem.factory(cxt)
