import unittest
from configurator import Configurator
from configurator import Section
import os.path
import os
from prettylogger.prettylogger import PrettyLogger

class ConfiguratorTest(unittest.TestCase):

  gLogger = PrettyLogger(True, True, True)

  def setUp(self):
    global gConfig
    gConfig = Configurator('/tmp/test-config.xml', aDebugOutput=True)

  def tearDown(self):
    os.remove('/tmp/test-config.xml')

  def test_createNewFile(self):
    fileExists = os.path.exists('/tmp/test-config.xml')
    self.assertTrue(fileExists)

  # def test_sections(self):
  #   global gConfig
  #   gConfig.addSectionByPath('Something.SomethingElse')
  #   newSection = gConfig.getSectionByPath('Something.SomethingElse')
  #   self.assertEquals('SomethingElse', newSection.getName())
  #   self.assertFalse(newSection.hasOptions())
  #   self.assertFalse(newSection.hasSubSections())
  #   self.assertTrue(newSection.isEmpty())
  #
  #   newSection.addSubSection('HelloWorld')
  #   hwSection = gConfig.getSectionByPath('Something.SomethingElse.HelloWorld')
  #   self.assertEquals('HelloWorld', hwSection.getName())
  #   self.assertEquals('Something.SomethingElse.HelloWorld', hwSection.getPath())
  #
  #   tlSections = gConfig.getTopLevelSections()
  #   self.assertEquals(1, len(tlSections))
  #   self.assertEquals('Something', tlSections[0].getName())
  #   firstTlSection = tlSections[0]
  #
  #   tlSectionOne = gConfig.getTopLevelSection('Something')
  #   self.assertEquals(firstTlSection, tlSectionOne)
  #

  def test_section_trigger_xml_update(self):
    global gConfig
    section = Section(gConfig, 'Scott', None)
    section.triggerXMLUpdate()
    document = gConfig.getDocument()
    documentXml = document.toxml()
    self.assertEquals('<?xml version="1.0" ?><Configuration><Scott/></Configuration>', documentXml)
    
  def test_section_get_element(self):
    global gConfig
    section = Section(gConfig, 'Scott', None)
    element = section.getElement()
    self.assertTrue(section.isTopLevelSection())
    self.assertTrue(element)

    self.gLogger.debug("Section element: " + str(element))

    self.assertTrue(element.parentNode)
    self.assertEquals("Configuration", element.parentNode.tagName)

  #
  # def test_sections_different_attrs_not_equal(self):
  #   global gConfig
  #   gConfig.addSectionByPath('Something.SomethingElse')
  #   parent = gConfig.getSectionByPath('Something')
  #   firstSection = Section(gConfig, 'Section', parent, None, {'some' : 'attr'})
  #   secondSection = Section(gConfig, 'Section', parent, None)
  #
  #   self.assertNotEquals(firstSection, secondSection)
  #
  # def test_options(self):
  #   global gConfig
  #   gConfig.addOptionByPath("MyOptionSection.SubSection.anOption", "true")
  #   gConfig.addOptionByPath("MyOptionSection.SubSection.anotherOption", "false")
  #   option = gConfig.getOptionByPath("MyOptionSection.SubSection.anOption")
  #   option2 = gConfig.getOptionByPath("MyOptionSection.SubSection.anOption")
  #
  #   self.assertEquals("anOption", option.getName())
  #   self.assertEquals("true", option.getValue())
  #   self.assertNotEquals(option, option2)
  #
  # def test_complex_config(self):
  #   global gConfig
  #   # We create a configuration file like the following:
  #   # <Binaries>
  #   #  <Binary name="someBinary">
  #   #    <option name="parameter">something</option>
  #   #    <option name="debug">true</option>
  #   #  </Binary>
  #   #  <Binary name="anotherBinary">
  #   #    <option name="parameter">something</option>
  #   #    <option name="debug">true</option>
  #   #  </Binary>
  #   # </Binaries>
  #   gConfig.addSectionByPath('Binaries.Binary');
  #   binarySectionOne = gConfig.getSectionByPath('Binaries.Binary')
  #   binarySectionOne.setOption('parameter', 'something')
  #   binarySectionOne.setOption('debug', 'true')

  def test_add_option_to_section(self):
    global gConfig
    newSection = gConfig.addSection("UND")
    self.assertFalse(newSection.hasOptions())
    newSection.setOption('Hockey', 'true')
    self.assertTrue(newSection.hasOptions())
    opts = newSection.getOptions()
    singleOption = opts[0]
    self.assertTrue(singleOption in newSection)

  def test_add_section_to_section(self):
    global gConfig
    newSection = gConfig.addSection("UND")
    subsect = newSection.addSubSection("Hockey")
    self.assertTrue(subsect)
    self.assertTrue(subsect in newSection)
    self.assertFalse(newSection in subsect)

    anotherSection = gConfig.addSection("UMN")
    self.assertFalse(anotherSection in newSection)

  def test_add_section(self):
    global gConfig
    newSection = gConfig.addSection('Scott')
    tlSections = gConfig.getTopLevelSections()
    self.assertTrue(newSection in tlSections)
    self.assertTrue(newSection)


if __name__ == '__main__':
  unittest.main()
