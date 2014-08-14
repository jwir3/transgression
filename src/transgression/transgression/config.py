import json
import datetime

class BinaryRepositoryEncoder(json.JSONEncoder):

  @staticmethod
  def encode(aObject):
    return "{ 'protocol' : '" + aObject.mProtocol + "', 'location' : " + "'" + aObject.mLocationString + "'}"

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

class PlatformConfigurationEncoder(json.JSONEncoder):
  @staticmethod
  def encode(aObject):
    encodedObject = "{ 'processName' : '" + aObject.getProcessName() + "', 'firstBinaryDate' : '" + aObject.getFirstBinaryDateString() + "', 'binaryRepository' : " + BinaryRepositoryEncoder.encode(aObject.getBinaryRepository()) + "}"
    return encodedObject

class PlatformConfiguration(json.JSONEncoder):
  def __init__(self, aProcessName, aFirstBinDateString, aBinaryRepo):
    self.mProcessName = aProcessName
    self.mFirstBinaryDateString = aFirstBinDateString
    self.mFirstBinaryDate = self.__processDate(aFirstBinDateString)
    self.mBinaryRepo = aBinaryRepo

  def getBinaryRepository(self):
    return self.mBinaryRepo

  def getProcessName(self):
    return self.mProcessName

  def getFirstBinaryDate(self):
    return self.mFirstBinaryDate

  def getFirstBinaryDateString(self):
    return self.mFirstBinaryDateString

  def __processDate(self, aDateString):
    firstBinaryDate = datetime.datetime.strptime(aDateString, "%Y-%m-%d")
    return firstBinaryDate

class ApplicationConfigEncoder(json.JSONEncoder):
  @staticmethod
  def encode(aObject):
    encodedObject = "{ '" + aObject.getAppName() + "': { 'platformConfigurations' : { ";
    platConfigs = aObject.getPlatformConfigurations()
    lastPCString = ""
    for platConfigKey in platConfigs.keys():
        if len(lastPCString) != 0:
          encodedObject = encodedObject + ", "
        lastPCString = PlatformConfigurationEncoder.encode(platConfigs[platConfigKey])
        encodedObject = encodedObject + lastPCString

    encodedObject = encodedObject + "}}}"
    return encodedObject

class ApplicationConfig(object):
  def __init__(self, aAppName, aPlatformConfigurationDict=None):
    self.mAppName = aAppName
    self.mPlatformConfigurations = self.__processPlatformConfigurations(aPlatformConfigurationDict)

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

class ConfigEncoder(json.JSONEncoder):
  @staticmethod
  def encode(aObject):
    encodedString = "{ '__type__' : 'transgression-configuration', 'applications' : "
    apps = aObject.getAllApplications()
    appString = ""
    for appKey in apps.keys():
      if len(appString) != 0:
        encodedString = encodedString + ", "

      appString = ApplicationConfigEncoder.encode(apps[appKey])
      encodedString = encodedString + appString

    encodedString = encodedString + "}}"

    return encodedString

class Config(object):
  def __init__(self, aConfigurationDict):
    self.mApps = dict()
    for key in aConfigurationDict.keys():
      self.mApps[key] = ApplicationConfig(key, aConfigurationDict[key]['platformConfigurations'])

  def getApplication(self, aName):
    return self.mApps[aName]

  def hasApplication(self, aName):
    return aName in self.mApps.keys()

  def getAllApplications(self):
    return self.mApps

  def getNumApplications(self):
    return len(self.mApps)

  def addApplication(self, aApplicationName, aPlatformConfigurationDict):
    platConfigDict = dict()
    platConfigDict['platformConfigurations'] = aPlatformConfigurationDict
    self.mApps[aApplicationName] = ApplicationConfig(aApplicationName, platConfigDict['platformConfigurations'])

def config_decoder(aObject):
  if '__type__' in aObject and aObject['__type__'] == 'transgression-configuration':
        return Config(aObject['applications'])

  return aObject
