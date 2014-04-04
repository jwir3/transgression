#class Transgression:
from configurator.configurator import Configurator
import os.path
import curses

# Map from 'identifier' -> 'user-readable text'
gSupportedLocations = [{'Secure FTP' : "sftp"}]

class BinaryConfiguration:
  _mRepository = None
  _mProgramName = ''

  def __init__(self, aProgramName, aRepository):
    self._mRepository = aRepository
    self._mProgramName = aProgramName

  def __str__(self):
    return "[" + self._mProgramName + "]: " + str(self._mRepository)

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

class SFTPRepository(BinaryRepository):
  _mHostname = ''
  _mUsername = ''
  _mPath = ''

  def __init__(self, aHostname, aUsername, aPath):
    self._mType = 'sftp'
    self._mHostname = aHostname
    self._mPath = aPath
    self._mUsername = aUsername

  def __str__(self):
    return "sftp://" + self._mUsername + "@" + self._mHostname + "/" + self._mPath

  def getType(self):
    return self._mType

  def getHostname(self):
    return self._mHostname

  def getPath(self):
    return self._mPath

  def getUsername(self):
    return self._mUsername

def getProgramNameFromUser():
  return raw_input("Please enter the name of this program: ")

def getBinaryTypeFromUser(progName):
  from ui import cmenu
  global gSupportedLocations
  menu = cmenu(gSupportedLocations, progName, 'Where are the binaries stored?')
  return menu.display()

def configureBinaryLocation(aLocationType):
  if aLocationType == 'sftp':
    host = raw_input("SFTP Hostname: ")
    user = raw_input("SFTP Username: ")
    sftpPath = raw_input("SFTP Remote Path: ")
    good = raw_input("SFTP: " + user + "@" + host + ":" + sftpPath + " - Is this correct? [Y/n] ")
    if good.lower() != 'n':
      return SFTPRepository(host, user, sftpPath)

def promptUserForProgram():
  response = raw_input("transgression didn't find any binaries configured. Would you like to configure one now? [Y/n] ")
  if response.lower() != 'n':
    programName = getProgramNameFromUser()
    programBinaryLocationType = getBinaryTypeFromUser(programName)
    repo = configureBinaryLocation(programBinaryLocationType)
    if repo:
      return BinaryConfiguration(programName, repo)
    else:
      return None
  else:
    return None

def main():
  # Check to make sure we have a config file, or create one
  config = Configurator(os.path.join('.transgression', 'config.xml'), aDebugOutput=True)

  # Configuration should include at least one binary
  try:
    section = config.getSectionByPath('Binaries')
  except:
    # We don't have any binaries listed, so perhaps we should prompt the user
    # for one?
    programConfig = promptUserForProgram()
    if programConfig:
      programConfig.writeToConfig(config)

if __name__ == '__main__':
  main()
