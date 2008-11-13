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
y
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

def builder():
  parser = OptionParser(conflict_handler="resolve", usage="%prog [options] source")
  parser.set_defaults(installPath="/opt", configure=True, compile=True, install=True, clean=False, verbose=False, sudo=False)
  common = OptionGroup(parser, "Common Options")
  common.add_option("--prefix", type="string", help="Install prefix", dest="installPath")
  common.add_option("-s","--source-path", type="string", help="Path to source", dest="source")
  common.add_option("-b","--build-path", type="string", help="Build path", dest="build")
  common.add_option("-v", "--verbose", action="store_true", help="Verbose")
  common.add_option("-N", "--name", type="string", help="Name of project")
  common.add_option("--configure", action="store_true", help="Run configuration")
  common.add_option("--compile", action="store_true", help="Compile")
  common.add_option("--install", action="store_true", help="Install")
  common.add_option("-S", "--sudo", action="store_true", help="Run install with sudo", dest="sudo",)
  common.add_option("--clean", action="store_true", help="Clean the build directory")
  parser.add_option_group(common)
  BuildSystem.buildArgs(parser)
  BuildContext.buildArgs(parser)
  (options,args) = parser.parse_args()
  if len(args) > 0:
      options.source = args.pop()
  if options.source == None:
      options.source = os.getcwd()
  return BuildSystem.factory(BuildContext.factory(options))