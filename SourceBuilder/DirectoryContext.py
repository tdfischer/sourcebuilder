# -*- coding: utf-8 -*-
import os
import BuildContext
import logging

class DirectoryContext(BuildContext.BuildContext):
    contextName="Directory"
    def __init__(self, args):
        args.source = os.path.abspath(args.source)
        if args.name == None:
            args.name = os.path.basename(args.source)
        BuildContext.BuildContext.__init__(self,args)
    
    @staticmethod
    def parseArgs(options):
        options.add_option("-n", "--no-external-build", action="store_false", dest="external", help="Don't build outside of the source")
        return options
    
    @staticmethod
    def canHandle(args):
        logging.debug("Checking if %s is a directory",args.source)
        return os.path.isdir(args.source)

BuildContext.register(DirectoryContext)