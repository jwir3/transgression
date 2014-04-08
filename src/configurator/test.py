import unittest
from configurator import Configurator
import os.path
import os

class ConfiguratorTest(unittest.TestCase):

  def setUp(self):
    global gConfig
    gConfig = Configurator('/tmp/test-config.xml', aDebugOutput=True)

  def tearDown(self):
    pass
    #os.remove('/tmp/test-config.xml')

  def test_createNewFile(self):
    fileExists = os.path.exists('/tmp/test-config.xml')
    self.assertTrue(fileExists)

  def test_sections(self):
    global gConfig
    gConfig.addSectionByPath('Something.SomethingElse')
    newSection = gConfig.getSectionByPath('Something.SomethingElse')
    self.assertEquals('SomethingElse', newSection.getName())
    self.assertFalse(newSection.hasOptions())
    self.assertFalse(newSection.hasSubSections())
    self.assertTrue(newSection.isEmpty())

    newSection.addSubSection('HelloWorld')
    hwSection = gConfig.getSectionByPath('Something.SomethingElse.HelloWorld')
    self.assertEquals('HelloWorld', hwSection.getName())

if __name__ == '__main__':
  unittest.main()
