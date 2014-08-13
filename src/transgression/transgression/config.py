import json
import datetime

class PlatformConfiguration(object):
  def __init__(self, aProcessName, aFirstBinDateString):
    self.mProcessName = aProcessName
    self.mFirstBinaryDate = self.__processDate(aFirstBinDateString)

  def getProcessName(self):
    return self.mProcessName

  def getFirstBinaryDate(self):
    return self.mFirstBinaryDate

  def __processDate(self, aDateString):
    self.mFirstBinaryDate = datetime.strptime(aDateString, "%y-%m-%d")

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
      platConfigs[key] = PlatformConfiguration(aRawPlatformDict[key]['processName'], aRawPlatformDict[key]['firstBinaryDate'])

    return platConfigs

def config_decoder(aObject):
  if '__type__' in aObject and aObject['__type__'] == 'transgression-configuration':
        return Config(aObject['appName'], aObject['platformConfigurations'])

  return aObject
