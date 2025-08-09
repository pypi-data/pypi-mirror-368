#########################################################################
#     please keep this notification at the beginning of this file       #
#                                                                       #
#                  Developed by Seyed Alireza Jalali                    #
#                 please visit: www.OpenSeesHouse.com                   #
#                                                                       #
#      DISTRIBUTION OF THIS CODE WITHOUT WRITTEN PERMISSION FROM        #
#                THE DEVELOPER IS HEREBY RESTRICTED                     #
#########################################################################

import OpenSeesHpy.OpenSeesH as oph


class OpenSeesHpy:
  cmndsLog = None
  echoCommands = False
  BlockStarted = False
  format = 'python'
  
  @staticmethod
  def logLine(command, args = [], hasBlock = False, inBlock = False):
    """Log command to the command log file."""
    if not OpenSeesHpy.cmndsLog:
      return
    def is_number(s):
      try:
        float(s)
        return True
      except ValueError:
        return False

    formatted_args = []
    if not isinstance(args, list) and not isinstance(args, tuple):
      args = [args]
    for arg in args:
      if isinstance(arg, str) and not is_number(arg):
        formatted_args.append(f"'{arg}'")
      else:
        if isinstance(arg, float):
          formatted_args.append(f"{arg:.5f}")
        else:
          formatted_args.append(str(arg))
    if OpenSeesHpy.format == 'tcl':
      line = f"{command} {' '.join(map(str, formatted_args))}"
    else:
      line = f"oph.{command}({', '.join(formatted_args)})"
    if (not inBlock) and OpenSeesHpy.BlockStarted:
      if OpenSeesHpy.format == 'tcl':
        OpenSeesHpy.cmndsLog.write('}' + "\n")
        if OpenSeesHpy.echoCommands:
          print('}'+'\n')
      OpenSeesHpy.BlockStarted = False
    if OpenSeesHpy.BlockStarted and OpenSeesHpy.format == 'tcl':
      line = f'\t{line}'
    OpenSeesHpy.cmndsLog.write(line)
    if OpenSeesHpy.echoCommands:
      print(line)
    if hasBlock and not OpenSeesHpy.BlockStarted:
      # Start a new block
      OpenSeesHpy.BlockStarted = True
      if OpenSeesHpy.format == 'tcl':
        OpenSeesHpy.cmndsLog.write(' {' + "\n")
        if OpenSeesHpy.echoCommands:
          print(' {' + "\n")
    OpenSeesHpy.cmndsLog.write('\n')
    if OpenSeesHpy.echoCommands:
      print('\n')
    OpenSeesHpy.cmndsLog.flush()

  @staticmethod
  def logCommands(filename=None, comment=None, echo=False, format = None):
    """Set up command logging for OpenSeesHpy commands.
    Args:
      filename (str): Name of the file to activate logging commands to.
      comment (str): Comment to write at the log file.
      echo (bool): If True, echo commands to the console.
    """
    if echo:
      OpenSeesHpy.echoCommands = True
    if filename or comment:
      if not filename:
        filename = 'commandsLog.oph'
      OpenSeesHpy.cmndsLog = open(filename, 'w')
      OpenSeesHpy.cmndsLog.write("from OpenSeesH.OpenSeesHpy import OpenSeesHpy as oph\n")
      OpenSeesHpy.cmndsLog.flush()
    if comment:
      OpenSeesHpy.cmndsLog.write(f"#{comment}\n")
      OpenSeesHpy.cmndsLog.flush()
    if format:
      OpenSeesHpy.format = format

  @staticmethod
  def units(unit_string):
    OpenSeesHpy.logLine("units", unit_string)
    return

  @staticmethod
  def model(*args):
    OpenSeesHpy.logLine("model", args)
    return oph.model(*args)

  @staticmethod
  def node(tag, *args):
    OpenSeesHpy.logLine("node", [tag, *args])
    return oph.node(tag, *args)

  @staticmethod
  def uniaxialMaterial(type, tag, *params):
    OpenSeesHpy.logLine("uniaxialMaterial", [type, tag, *params])
    return oph.uniaxialMaterial(type, tag, *params)

  @staticmethod
  def section(type, tag, *params):
    hasBlock = False
    if type == 'fiber' or type == 'Fiber':
      hasBlock = True
    OpenSeesHpy.logLine("section", [type, tag, *params], hasBlock, False)
    return oph.section(type, tag, *params)

  @staticmethod
  def patch(type, *params):
    OpenSeesHpy.logLine("patch", [type, *params], False, True)
    return oph.patch(type, *params)

  @staticmethod
  def layer(type, *params):
    OpenSeesHpy.logLine("layer", [type, *params], False, True)
    return oph.layer(type, *params)

  @staticmethod
  def fiber(type, *params):
    OpenSeesHpy.logLine("fiber", [type, *params], False, True)
    return oph.fiber(type, *params)

  @staticmethod
  def geomTransf(type, tag, *args):
    OpenSeesHpy.logLine("geomTransf", [type, tag, *args])
    return oph.geomTransf(type, tag, *args)

  @staticmethod
  def element(type, tag, *args):
    OpenSeesHpy.logLine("element", [type, tag, *args])
    return oph.element(type, tag, *args)

  @staticmethod
  def beamIntegration(type, tag, *args):
    OpenSeesHpy.logLine("beamIntegration", [type, tag, *args])
    return oph.beamIntegration(type, tag, *args)

  @staticmethod
  def region(tag, *args):
    OpenSeesHpy.logLine("region", [tag, *args])
    return oph.region(tag, *args)

  @staticmethod
  def rayleigh(*args):
    OpenSeesHpy.logLine("rayleigh", args)
    return oph.rayleigh(*args)

  @staticmethod
  def fix(nodeTag, *args):
    OpenSeesHpy.logLine("fix", [nodeTag, *args])
    return oph.fix(nodeTag, *args)

  @staticmethod
  def fixX(*args):
    OpenSeesHpy.logLine("fixX", args)
    return oph.fixX(*args)

  @staticmethod
  def fixY(*args):
    OpenSeesHpy.logLine("fixY", args)
    return oph.fixY(*args)

  @staticmethod
  def fixZ(*args):
    OpenSeesHpy.logLine("fixZ", args)
    return oph.fixZ(*args)

  @staticmethod
  def frictionModel(*args):
    OpenSeesHpy.logLine("frictionModel", args)
    return oph.frictionModel(*args)

  @staticmethod
  def equalDOF(*args):
    OpenSeesHpy.logLine("equalDOF", args)
    return oph.equalDOF(*args)

  @staticmethod
  def rigidDiaphragm(*args):
    OpenSeesHpy.logLine("rigidDiaphragm", args)
    return oph.rigidDiaphragm(*args)

  @staticmethod
  def rigidLink(*args):
    OpenSeesHpy.logLine("rigidLink", args)
    return oph.rigidLink(*args)

  @staticmethod
  def timeSeries(type, tag, *args):
    OpenSeesHpy.logLine("timeSeries", [type, tag, *args])
    return oph.timeSeries(type, tag, *args)

  @staticmethod
  def pattern(type, tag, *args):
    hasBlock = False
    if type == 'Plain':
      hasBlock = True
    OpenSeesHpy.logLine("pattern", [type, tag, *args], hasBlock, False)
    return oph.pattern(type, tag, *args)

  @staticmethod
  def load(nodeTag, *args):
    OpenSeesHpy.logLine("load", [nodeTag, *args], False, True)
    return oph.load(nodeTag, *args)

  @staticmethod
  def sp(nodeTag, *args):
    OpenSeesHpy.logLine("sp", [nodeTag, *args], False, True)
    return oph.sp(nodeTag, *args)

  @staticmethod
  def eleLoad(tag, *args):
    OpenSeesHpy.logLine("eleLoad", [tag, *args], False, True)
    return oph.eleLoad(tag, *args)

  @staticmethod
  def groundMotion(tag, *args):
    OpenSeesHpy.logLine("groundMotion", [tag, *args])
    return oph.groundMotion(tag, *args)

  @staticmethod
  def imposedMotion(*args):
    OpenSeesHpy.logLine("imposedMotion", args)
    return oph.imposedMotion(*args)

  @staticmethod
  def recorder(type, *args):
    OpenSeesHpy.logLine("recorder", [type, *args])
    return oph.recorder(type, *args)

  @staticmethod
  def record(*args):
    OpenSeesHpy.logLine("record", args)
    if args:
      return oph.recordSingle(*args)
    return oph.record()

  @staticmethod
  def flushRecorders():
    OpenSeesHpy.logLine("flushRecorders")
    return oph.flushRecorders()

  @staticmethod
  def numberer(*args):
    OpenSeesHpy.logLine("numberer", args)
    oph.numberer(*args)

  @staticmethod
  def wipeAnalysis():
    OpenSeesHpy.logLine("wipeAnalysis")
    oph.wipeAnalysis()

  @staticmethod
  def constraints(*args):
    OpenSeesHpy.logLine("constraints", args)
    oph.constraints(*args)

  @staticmethod
  def system(*args):
    OpenSeesHpy.logLine("system", args)
    oph.system(*args)

  @staticmethod
  def test(*args):
    OpenSeesHpy.logLine("test", args)
    oph.test(*args)

  @staticmethod
  def algorithm(*args):
    OpenSeesHpy.logLine("algorithm", args)
    oph.algorithm(*args)

  @staticmethod
  def integrator(*args):
    OpenSeesHpy.logLine("integrator", args)
    oph.integrator(*args)

  @staticmethod
  def analysis(*args):
    OpenSeesHpy.logLine("analysis", args)
    oph.analysis(*args)

  @staticmethod
  def loadConst(*args):
    OpenSeesHpy.logLine("loadConst", args)
    oph.loadConst(*args)

  @staticmethod
  def analyze(*args):
    OpenSeesHpy.logLine("analyze", args)
    return oph.analyze(*args)

  @staticmethod
  def eigen(*args):
    OpenSeesHpy.logLine("eigen", args)
    return oph.eigen(*args)

  @staticmethod
  def nodeCoord(tag):
    # OpenSeesHpy.logLine(f"nodeCoord {tag}")
    return oph.nodeCoord(tag)

  @staticmethod
  def nodeDisp(tag, dof):
    # OpenSeesHpy.logLine(f"nodeDisp {tag} {dof}")
    return oph.nodeDisp(tag, dof)

  @staticmethod
  def recorderValue(recorderTag, *args):
    # OpenSeesHpy.logLine(f"recorderValue {recorderTag} {' '.join(map(str, args))}")
    return oph.recorderValue(recorderTag, *args)

  @staticmethod
  def getTime():
    # OpenSeesHpy.logLine("getTime")
    return oph.getTime()

  @staticmethod
  def remove(*params):
    OpenSeesHpy.logLine("remove", params)
    return oph.remove(*params)

  @staticmethod
  def wipe():
    OpenSeesHpy.logLine("wipe")
    oph.wipe()

  @staticmethod
  def reset():
    OpenSeesHpy.logLine("reset")
    oph.reset()

  @staticmethod
  def vup(*params):
    OpenSeesHpy.logLine("vup", params)
    oph.vup(*params)

  @staticmethod
  def prp(*params):
    OpenSeesHpy.logLine("prp", params)
    oph.prp(*params)

  @staticmethod
  def display(*params):
    OpenSeesHpy.logLine("display", params)
    oph.display(*params)
