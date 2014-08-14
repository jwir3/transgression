import json
import datetime

class BinaryRepository(object):
  def __init__(self, aBinaryRepositoryDict):
    self.initialize(aBinaryRepositoryDict['protocol'], aBinaryRepositoryDict['location'])

  def initialize(self, aProtocol, aLocationString):
    self.mLocationString = aLocationString
    self.mProtocol = aProtocol

  def getProtocol(self):
    return self.mProtocol

  def getLocationFormatString(self):
    return self.mLocationString

class PlatformConfiguration(object):
  def __init__(self, aProcessName, aFirstBinDateString, aBinaryRepo):
    self.mProcessName = aProcessName
    self.mFirstBinaryDate = self.__processDate(aFirstBinDateString)
    self.mBinaryRepo = aBinaryRepo

  def getBinaryRepository(self):
    return self.mBinaryRepo

  def getProcessName(self):
    return self.mProcessName

  def getFirstBinaryDate(self):
    return self.mFirstBinaryDate

  def __processDate(self, aDateString):
    firstBinaryDate = datetime.datetime.strptime(aDateString, "%Y-%m-%d")
    return firstBinaryDate

class Config(object):
  def __init__(self, aAppName, aPlatformConfigurations=None):
    self.mAppName = aAppName
    self.mPlatformConfigurations = self.__processPlatformConfigurations(aPlatformConfigurations)

  def getAppName(self):
    return self.mAppName

  def getPlatformConfiguration(self, aPlatformName):
    return self.getPlatformConfigurations()[aPlatformName]

  def getPlatformConfigurations(self):
    return self.mPlatformConfigurations

  def __processPlatformConfigurations(self, aRawPlatformDict):
    platConfigs = dict()
    for key in aRawPlatformDict.keys():
      binaryRepo = BinaryRepository(aRawPlatformDict[key]['binaryRepository'])
      platConfigs[key] = PlatformConfiguration(aRawPlatformDict[key]['processName'], aRawPlatformDict[key]['firstBinaryDate'], binaryRepo)

    return platConfigs

def config_decoder(aObject):
  if '__type__' in aObject and aObject['__type__'] == 'transgression-configuration':
        return Config(aObject['appName'], aObject['platformConfigurations'])

  return aObject
