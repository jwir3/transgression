import unittest
from configurator import Configurator
import os.path
import os

class ConfiguratorTest(unittest.TestCase):

  def setUp(self):
    global gConfig
    gConfig = Configurator('/tmp/test-config.xml', aDebugOutput=True)

  def tearDown(self):
    os.remove('/tmp/test-config.xml')

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
    self.assertEquals('Something.SomethingElse.HelloWorld', hwSection.getPath())

    tlSections = gConfig.getTopLevelSections()
    self.assertEquals(1, len(tlSections))
    self.assertEquals('Something', tlSections[0].getName())
    firstTlSection = tlSections[0]

    tlSectionOne = gConfig.getTopLevelSection('Something')
    self.assertEquals(firstTlSection, tlSectionOne)

  def test_options(self):
    global gConfig
    gConfig.addOptionByPath("MyOptionSection.SubSection.anOption", "true")
    gConfig.addOptionByPath("MyOptionSection.SubSection.anotherOption", "false")
    option = gConfig.getOptionByPath("MyOptionSection.SubSection.anOption")
    option2 = gConfig.getOptionByPath("MyOptionSection.SubSection.anOption")

    self.assertEquals("anOption", option.getName())
    self.assertEquals("true", option.getValue())
    self.assertNotEquals(option, option2)

if __name__ == '__main__':
  unittest.main()
