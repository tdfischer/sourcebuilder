# -*- coding: utf-8 -*-
import os
import BuildContext
import logging
import cPickle


class DirectoryContext(BuildContext.BuildContext):
    contextName="Directory"
    def __init__(self, args):
        args.source = os.path.abspath(args.source)
        if args.name == None:
            args.name = os.path.basename(args.source)
        BuildContext.BuildContext.__init__(self,args)
    
    def save(self):
        f = open(self.args().source+os.path.sep+".buildrc","w")
        cPickle.dump(self.args(),f)
        f.close()
    
    def load(self):
        if os.path.exists(self.args().source+os.path.sep+".buildrc"):
            f = open(self.args().source+os.path.sep+".buildrc","r")
            self.setArgs(cPickle.load(f))
            f.close()
    
    @staticmethod
    def parseArgs(options):
        options.add_option("-n", "--no-external-build", action="store_false", dest="external", help="Don't build outside of the source")
        return options
    
    @staticmethod
    def canHandle(args):
        BuildContext.BuildContext.logging.debug("Checking if %s is a directory",args.source)
        return os.path.isdir(args.source)

BuildContext.register(DirectoryContext)