import logging

registeredSystems = []

def factory(context):
  s = getSystem(context)
  if s == None:
    raise NotImplementedError, "No supported build system found for %s"%(context)
  return s(context)

def getSystem(context):
  for s in registeredSystems:
    logging.debug("Checking %s against %s"%(s, context))
    if s.canHandle(context):
      return s

def register(system):
  registeredSystems.append(system)

class BuildSystem:
  registeredSystems = []
  systemName = None

  def __init__(self, context):
    self.cxt = context
  
  def package(self):
    return self.cxt.package
  
  def srcDir(self):
    return self.cxt.source
  
  def buildDir(self):
    return self.cxt.build
  
  def setting(self,key):
    return self.cxt.s.get(key)
  
  @staticmethod
  def canHandle(context):
    return false
    
  def build(self):
    if self.configure():
      logging.info("Configure complete.")
      if self.make():
        logging.info("Build complete.")
        if self.install():
          logging.info("Installation complete.")
        else:
          logging.error("Installation failed.")
      else:
        logging.error("Build failed.")
    else:
      logging.error("Configuration failed.")
    
  def configure(self):
    pass
  
  def make(self):
    pass
  
  def install(self):
    pass