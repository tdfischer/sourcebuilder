# -*- coding: utf-8 -*-
import os
import subprocess
import BuildContext
import logging

class TarballContext(BuildContext.BuildContext):
    contextName="Tarball"
    def __init__(self, args):
        args.source = os.path.abspath(args.source)
        filename = os.path.basename(args.source)
        if args.name == None:
            args.name = filename.split('.')[0].split('-')[0]
        BuildContext.BuildContext.__init__(self, args)
        
        if not os.path.exists(args.build):
            os.mkdir(args.build)
        os.chdir(args.build)
        ret = subprocess.call(["tar","xf",args.source])
        files = os.listdir(args.build)
        if len(files) == 1:
            args.build+=os.path.sep+files[0]
        args.source = args.build
        logging.info("Building in "+args.build)

    @staticmethod
    def canHandle(args):
        filename = os.path.basename(args.source)
        return os.path.isfile(args.source) and ("tar" in filename.split('.'))
        
BuildContext.register(TarballContext)