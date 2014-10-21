import os
import sys
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
import unittest
import json
from transgression.config import *

class ConfigTest(unittest.TestCase):
  def setUp(self):
    self.mJsonString = open(os.path.abspath(os.path.dirname(os.path.realpath(__file__))+"/data/testConfig.json"), 'r').read()

  def test_configuration_construction(self):
    configObj = json.loads(self.mJsonString, object_hook=config_decoder)
    self.assertTrue(configObj.hasApplication('Jingit'))
    self.assertEquals('Jingit', configObj.getApplication('Jingit').getAppName())
    self.assertEquals('air.com.jingit.mobile', configObj.getApplication('Jingit').getPlatformConfiguration('android').getProcessName())
    self.assertEquals(2009, configObj.getApplication('Jingit').getPlatformConfiguration('android').getFirstBinaryDate().year)
    self.assertEquals('sftp', configObj.getApplication('Jingit').getPlatformConfiguration('android').getBinaryRepository().getProtocol())

  def test_configuration_add_application(self):
    configObj = json.loads(self.mJsonString, object_hook=config_decoder)
    platformConfigDict = { 'windows' : { 'firstBinaryDate' : '2010-01-01', 'processName' : 'Jingit-bin', 'binaryRepository' : { 'protocol' : 'sftp', 'location': 'www.google.com'}}}
    configObj.addApplication('testApp', platformConfigDict)
    self.assertTrue(configObj.hasApplication('testApp'))
    self.assertEquals('testApp', configObj.getApplication('testApp').getAppName())
    self.assertEquals('Jingit-bin', configObj.getApplication('testApp').getPlatformConfiguration('windows').getProcessName())
    self.assertEquals(2010, configObj.getApplication('testApp').getPlatformConfiguration('windows').getFirstBinaryDate().year)
    self.assertEquals('sftp', configObj.getApplication('testApp').getPlatformConfiguration('windows').getBinaryRepository().getProtocol())

  # def test_add_application(self):
  #   configObj = json.loads(self.mJsonString, object_hook=config_decoder)
  #   platformConfigDict = { 'windows' : { 'firstBinaryDate' : '2010-01-01', 'processName' : 'Jingit-bin', 'binaryRepository' : { 'protocol' : 'sftp', 'location': 'www.google.com'}}}
  #   configObj.addApplication('WokkaWokka', platformConfigDict)

  def test_json_encoding(self):
    configObj = json.loads(self.mJsonString, object_hook=config_decoder)
    app = configObj.getApplication('Jingit')
    platConfig = app.getPlatformConfiguration('android')
    binRepo = platConfig.getBinaryRepository()

    expectedBinaryRepoOutput = "{ 'protocol' : 'sftp', 'location' : 'jenkinsmonkey.local/APKS/%year%-%month%-%day%/%time%/%commitid%/%appname%-debug-%buildnumber%.apk'}"

    self.assertEquals(expectedBinaryRepoOutput, BinaryRepositoryEncoder.encode(binRepo))
    self.assertEquals(expectedBinaryRepoOutput, json.dumps(binRepo, cls=BinaryRepositoryEncoder))

    expectedPlatConfigOutput = "{ 'processName' : 'air.com.jingit.mobile', 'firstBinaryDate' : '2009-01-01', 'binaryRepository' : " + expectedBinaryRepoOutput + "}"
    self.assertEquals(expectedPlatConfigOutput, PlatformConfigurationEncoder.encode(platConfig))
    self.assertEquals(expectedPlatConfigOutput, json.dumps(platConfig, cls=PlatformConfigurationEncoder))

    expectedAppConfigOutput = "{ 'Jingit': { 'platformConfigurations' : { " + expectedPlatConfigOutput + "}}}"
    self.assertEquals(expectedAppConfigOutput, ApplicationConfigEncoder.encode(app))
    self.assertEquals(expectedAppConfigOutput, json.dumps(app, cls=ApplicationConfigEncoder))

    expectedConfigOutput = "{ '__type__' : 'transgression-configuration', 'applications' : " + expectedAppConfigOutput + "}}"
    self.assertEquals(expectedConfigOutput, ConfigEncoder.encode(configObj))
    self.assertEquals(expectedConfigOutput, json.dumps(configObj, cls=ConfigEncoder, indent=2))

  def test_config_mozilla(self):
      mozJsonString = open(os.path.abspath(os.path.dirname(os.path.realpath(__file__))+"/data/testConfigMozillaMac.json"), 'r').read()
      configObj = json.loads(mozJsonString, object_hook=config_decoder)
      app = configObj.getApplication("FirefoxMac")
      platConfig = app.getPlatformConfiguration('osx')
      binRepo = platConfig.getBinaryRepository()

      self.assertEquals("ftp.mozilla.org", binRepo.getHost())
      self.assertEquals("pub/firefox/2013/08/2013-08-14-mozilla-central-debug/*.dmg", binRepo.getFormattedDirectory(2013, 8, 14))
      
if __name__ == '__main__':
  unittest.main()
