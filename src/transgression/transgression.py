#class Transgression:
from configurator.configurator import Configurator
import os.path
import paramiko
from time import sleep
import getpass
from prettylogger.prettylogger import PrettyLogger
from ui import showMenu

gLogger = None
gBinTypeSelected = None
gProgramChoice = None

def setTypeToSFTP():
  global gBinTypeSelected
  gBinTypeSelected = 'sftp'

# def setProgramChoice(aChoice):
#   global gProgramChoice
#   gProgramChoice = aChoice

gSupportedLocations = [('Secure FTP', setTypeToSFTP)]

class BinaryConfiguration:
  _mRepository = None
  _mProgramName = ''

  def __init__(self, aProgramName, aRepository):
    self._mRepository = aRepository
    self._mProgramName = aProgramName

  def __str__(self):
    return "[" + self._mProgramName + "]: " + str(self._mRepository)

  def getName(self):
    return self._mProgramName

  def writeToConfig(self, aConfigurator):
    aConfigurator.addOptionByPath("Binaries.Binary.binaryName", self._mProgramName)
    aConfigurator.addOptionByPath("Binaries.Binary.Repository.type", self._mRepository.getType())
    aConfigurator.addOptionByPath("Binaries.Binary.Repository.host", self._mRepository.getHostname())
    aConfigurator.addOptionByPath("Binaries.Binary.Repository.user", self._mRepository.getUsername())
    aConfigurator.addOptionByPath("Binaries.Binary.Repository.path", self._mRepository.getPath())

class BinaryRepository:
  _mType = ''

  def __init__(self, aType):
    self._mType = aType

  def connect(self):
    pass

class SFTPRepository(BinaryRepository):
  _mHostname = ''
  _mUsername = ''
  _mPath = ''
  __mPassword = None

  def __init__(self, aHostname, aUsername, aPath):
    self._mType = 'sftp'
    self._mUsername = aUsername
    self._mHostname = aHostname
    self._mPath = aPath

  def __str__(self):
    return "sftp://" + self._mUsername + "@" + self._mHostname + "/" + self._mPath

  def connect(self):
    global gLogger
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
      ssh.connect(aHost, username=self._mUserName)
    except Exception as e:
      self.__mPassword = None
      raise e

  def getType(self):
    return self._mType

  def getHostname(self):
    return self._mHostname

  def getPath(self):
    return self._mPath

  def getUsername(self):
    return self._mUsername

  def checkHost(self, aHost):
    try:
      self.connect()
      return True
    except Exception:
      return False

def getProgramNameFromUser():
  return raw_input("Please enter the name of this program: ")

def getBinaryTypeFromUser(progName):
  global gSupportedLocations
  global gBinTypeSelected
  # showMenu(gSupportedLocations)
  # return gBinTypeSelected

  # We only have one possible option right now.
  return 'sftp'

def configureBinaryLocation(aLocationType):
  if aLocationType == 'sftp':
    host = raw_input("SFTP Hostname: ")
    user = raw_input("SFTP Username: ")
    sftpPath = raw_input("SFTP Remote Path: ")
    good = raw_input("SFTP: " + user + "@" + host + ":" + sftpPath + " - Is this correct? [Y/n] ")
    if good.lower() != 'n':
      return SFTPRepository(host, user, sftpPath)

def getInputForNewProgram():
  programName = getProgramNameFromUser()
  programBinaryLocationType = getBinaryTypeFromUser(programName)
  repo = configureBinaryLocation(programBinaryLocationType)
  if repo:
    return BinaryConfiguration(programName, repo)
  return None

def promptUserForProgram():
  response = raw_input("transgression didn't find any binaries configured. Would you like to configure one now? [Y/n] ")
  if response.lower() != 'n':
    return getInputForNewProgram()
  return None

def getListOfBinaries(aConfigurator):
  global gLogger
  binariesList = []
#try:
  binariesSection = aConfigurator.getSectionByPath('Binaries')
  gLogger.debug("binaries section: " + str(binariesSection))
  allBinSections = binariesSection.getSubSections()
  for binSection in allBinSections:
    gLogger.debug("binSection: " + str(binSection))
    progName = binSection.getOption('binaryName').getValue()
    repoSection = binSection.getSubSection('Repository')
    repoType = repoSection.getOption('type')
    gLogger.debug("repo type: " + str(repoType))
    if repoType.getValue() == 'sftp':
      repoPath = repoSection.getOption('path')
      repoUser = repoSection.getOption('user')
      repoHost = repoSection.getOption('host')
      newRepo = SFTPRepository(repoHost, repoUser, repoPath)
      binariesList.append(BinaryConfiguration(progName, newRepo))
#except Exception as e:
#  binariesList = []

  return binariesList

def setupRegressionTest(aProgramConfig):
  print("About to regression test " + aProgramConfig.getName())

def main():
  global gLogger

  DEBUG = True
  VERBOSE = False

  # If we were run with debug mode on, then configure our logger
  gLogger = PrettyLogger(True, DEBUG, VERBOSE)

  try:
    # Check to make sure we have a config file, or create one
    config = Configurator(os.path.join('.transgression', 'config.xml'), aDebugOutput=DEBUG)

    # Configuration should include at least one binary
    try:
      gLogger.debug("About to try and retrieve binaries section...")
      section = config.getSectionByPath('Binaries')
      gLogger.debug("Section found: " + str(section))
      binaries = getListOfBinaries(config)
      print("Binaries: " + str(binaries))
      allPrograms = []
      programChoice = None
      for program in binaries:
        programListItem = (program.getName(), program)
        allPrograms.append(programListItem)
      allPrograms.append(('Create New Binary', None))
      programChoice = showMenu(allPrograms)
      if not programChoice:
        gLogger.debug("Program choice was None")
        programConfig = getInputForNewProgram()
        if programConfig:
          programConfig.writeToConfig(config)
          programChoice = programConfig
    except Exception as e:
      gLogger.debug("Exception occurred: " + str(e))

      # We don't have any binaries listed, so perhaps we should prompt the user
      # for one?

      programConfig = promptUserForProgram()

      if programConfig:
        programConfig.writeToConfig(config)
        programChoice = programConfig

    # We can now use programChoice as the one to regression test
    setupRegressionTest(programChoice)
  except KeyboardInterrupt:
    # We just want to exit normally in this circumstance.
    print("")
    exit(0)

if __name__ == '__main__':
  main()
