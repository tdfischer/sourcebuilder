# -*- coding: utf-8 -*-
import logging
from optparse import OptionGroup
import os

registeredContexts = []

def factory(args):
  s = getContext(args)
  if s == None:
    raise NotImplementedError, "No supported build context found"
  return s(args)

def getContext(args):
    for s in registeredContexts:
        BuildContext.logging.debug("Checking context %s"%(s))
        if s.canHandle(args):
            return s

def buildArgs(parser):
    for s in registeredContexts:
        group = OptionGroup(parser, s.contextName)
        parser.add_option_group(s.parseArgs(group))

def register(system):
  registeredContexts.append(system)

class BuildContext:
    contextName=None
    logging = logging.getLogger("SourceBuilder.BuildContext")
    def __init__(self, args):
        if args.build == None:
            args.build = "/tmp/build-"+args.name
        self._args = args
    
    def __getattr__(self, name):
        return getattr(self._args,name)
    
    def args(self):
        return self._args
    
    def setArgs(self, args):
        self._args = args
    
    def __str__(self):
        return self.contextName
    
    def __repr__(self):
        return "<BuildContext(%s) in src:%s, build:%s>"%(self.__class__.contextName, self.source, self.build)
    
    def save(self):
        raise NotImplementedError
    
    def load(self):
        raise NotImplementedError
    
    @staticmethod
    def parseArgs(options):
        options.set_description("No options")
        return options

#class BuildContext:
#    def __init__(self, args):
#       self.source = args.source
#        self.build = args.build
#        #If its a file, we're probably just installing something from a tarball,
#        #So a temp build is just fine.
#        if os.path.isfile(target):
#            raise NotImplementedError, "Currently, only building the current directory or configured packages is supported"
#            s = Settings()
#            #If its a path, we're probably working on a project.
#            if os.path.isdir(target):
#                target = os.path.abspath(target)
#                for section in s.sections():
#                    if s.has_option(section, "sourceDir") and s.get(section, 'sourceDir') == target:
#                        packageName = section
#                        break
#                else:
#                    #TODO: More advanced detection. What if we're in a subdirectory?
#                    packageName = target.split('/')[-1]
#                    buildLogger.warning("Guessing package name to be %s",packageName)
#                    s.add_section(packageName)
#                    s.set(packageName, "sourceDir", target)
#                    s.save()
#            else:
#                if (s.has_section(target)):
#                    packageName = target
#                else:
#                    raise IOError, "%s not found"%(target)
#            self.s = PackageSettings(packageName)
#            self.package = packageName#
#
#    def sourceDir(self):
#        return self.s.get('sourceDir')
#
#    def buildDir(self):
#        return self.s.get('buildDir')
#
#    def __str__(self):
#        return "<BuildContext for %s, src:%s, build:%s>"%(self.package, self.sourceDir(), self.buildDir())