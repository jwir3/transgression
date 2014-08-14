import os
import sys
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
import unittest
import json
from transgression import config

class ConfigTest(unittest.TestCase):
  def setUp(self):
    self.mJsonString = open(os.path.abspath(os.path.dirname(os.path.realpath(__file__))+"/data/testConfig.json"), 'r').read()

  def test_configuration_construction(self):
    configObj = json.loads(self.mJsonString, object_hook=config.config_decoder)
    self.assertEquals('Jingit', configObj.getAppName())
    self.assertEquals('air.com.jingit.mobile', configObj.getPlatformConfiguration('android').getProcessName())
    self.assertEquals(2009, configObj.getPlatformConfiguration('android').getFirstBinaryDate().year)
    self.assertEquals('sftp', configObj.getPlatformConfiguration('android').getBinaryRepository().getProtocol())
    self.assertEquals('jenkinsmonkey.local/APKS/%year%-%month%-%day%/%time%/%commitid%/%appname%-debug-%buildnumber%.apk', configObj.getPlatformConfiguration('android').getBinaryRepository().getLocationFormatString())

if __name__ == '__main__':
  unittest.main()
