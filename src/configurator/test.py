import unittest
from configurator import Configurator
from configurator import Section
import os.path
import os
from prettylogger.prettylogger import PrettyLogger

class ConfiguratorTest(unittest.TestCase):

  gLogger = PrettyLogger(True, True, True)
  gConfig = None

  def setUp(self):
    self.gConfig = Configurator('/tmp/test-config.xml', aDebugOutput=True)

  def tearDown(self):
    self.gConfig = None
    os.remove('/tmp/test-config.xml')

  def test_createNewFile(self):
    fileExists = os.path.exists('/tmp/test-config.xml')
    self.assertTrue(fileExists)

  def test_add_section_by_path(self):
    newSection = self.gConfig.addSectionByPath('Something.SomethingElse')
    self.gLogger.debug("Options: " + str(newSection.getOptions()))
    self.assertEquals('SomethingElse', newSection.getName())

    self.assertFalse(newSection.hasOptions())
    self.assertFalse(newSection.hasSubSections())
    self.assertTrue(newSection.isEmpty())

  def test_get_section_by_path(self):
    newSection = self.gConfig.addSectionByPath('Something.SomethingElse')
    newSection.addSubSection('HelloWorld')
    hwSection = self.gConfig.getSectionByPath('Something.SomethingElse.HelloWorld')
    self.assertEquals('HelloWorld', hwSection.getName())
    self.assertEquals('Something.SomethingElse.HelloWorld', hwSection.getPath())

  def test_get_top_level_sections(self):
    newSection = self.gConfig.addSectionByPath('Something.SomethingElse')
    tlSections = self.gConfig.getTopLevelSections()
    self.assertEquals(1, len(tlSections))
    self.assertEquals('Something', tlSections[0].getName())
    firstTlSection = tlSections[0]

    tlSectionOne = self.gConfig.getTopLevelSection('Something')
    self.assertEquals(firstTlSection, tlSectionOne)

  def test_create_section_with_attributes(self):
    section = Section(self.gConfig, 'Pineapple', None, {'name' : 'Richard'})
    self.assertTrue(section.hasAttributes())
    self.assertEquals('name', section.getAttributes()[0].getName())
    self.assertEquals('Richard', section.getAttributes()[0].getValue())

  def test_section_trigger_xml_update(self):
    section = Section(self.gConfig, 'Grapefruit', None)
    section.triggerXMLUpdate()
    document = self.gConfig.getDocument()
    documentXml = document.toxml()
    self.assertEquals('<?xml version="1.0" ?><Configuration><Grapefruit/></Configuration>', documentXml)

  def test_section_get_element(self):
    section = Section(self.gConfig, 'Scott', None)
    element = section.getElement()
    self.assertTrue(section.isTopLevelSection())
    self.assertTrue(element)

    self.gLogger.debug("Section element: " + str(element))

    self.assertTrue(element.parentNode)
    self.assertEquals("Configuration", element.parentNode.tagName)

  def test_sections_different_attrs_not_equal(self):

    self.gConfig.addSectionByPath('Something.SomethingElse')
    parent = self.gConfig.getSectionByPath('Something')
    firstSection = Section(self.gConfig, 'Section', parent, {'some' : 'attr'})
    secondSection = Section(self.gConfig, 'Section', parent)

    self.assertNotEquals(firstSection, secondSection)

  def test_add_option_by_path(self):

    self.gConfig.addOptionByPath("MyOptionSection.SubSection.anOption", "true")
    option2 = self.gConfig.addOptionByPath("MyOptionSection.SubSection.anotherOption", "false")
    option = self.gConfig.getOptionByPath("MyOptionSection.SubSection.anOption")

    self.assertEquals("anOption", option.getName())
    self.assertEquals("true", option.getValue())
    self.assertNotEquals(option, option2)

  def test_add_attribute(self):

    section = self.gConfig.addSection("Person")
    section.addAttribute("name", "Scott")
    self.assertTrue(section.hasAttributes())

    document = self.gConfig.getDocument()
    self.gLogger.debug("XML: " + document.toxml())

  def test_complex_config(self):

    # We create a configuration file like the following:
    # <Binaries>
    #  <Binary name="someBinary">
    #    <option name="parameter">something</option>
    #    <option name="debug">true</option>
    #  </Binary>
    #  <Binary name="anotherBinary">
    #    <option name="parameter">something</option>
    #    <option name="debug">true</option>
    #  </Binary>
    # </Binaries>
    binarySectionOne = self.gConfig.addSectionByPath('Binaries.Binary')
    binarySectionOne.addAttribute('name', 'someBinary')
    binarySectionOne.setOption('parameter', 'something')
    binarySectionOne.setOption('debug', 'true')

    binariesSection = self.gConfig.getSectionByPath('Binaries')
    binarySectionTwo = binariesSection.addSubSection('Binary')
    binarySectionTwo.addAttribute('name', 'anotherBinary')
    binarySectionTwo.setOption('parameter', 'something')
    binarySectionTwo.setOption('debug', 'true')

    self.assertNotEquals(binarySectionOne, binarySectionTwo)

    #foundSection = self.gConfig.getSectionByPath('Binaries.Binary[name="someBinary"]')
    #self.assertEquals(binarySectionOne, foundSection)

  def test_section_contains_attributes(self):
    binarySectionOne = self.gConfig.addSectionByPath('Binaries.Binary')
    binarySectionOne.addAttribute('name', 'someBinary')
    binarySectionOne.addAttribute('Grape', 'true')
    self.assertTrue(binarySectionOne.containsAttributes({'name' : 'someBinary'}))
    self.assertTrue(binarySectionOne.containsAttributes({'Grape' : 'true'}))
    self.assertFalse(binarySectionOne.containsAttributes({'name' : 'jedi'}))
    self.assertTrue(binarySectionOne.containsAttributes({'name' : 'someBinary', 'Grape': 'true'}))

  def test_add_option_to_section(self):
    newSection = self.gConfig.addSection("UND")
    self.assertFalse(newSection.hasOptions())
    newSection.setOption('Hockey', 'true')
    self.assertTrue(newSection.hasOptions())
    opts = newSection.getOptions()
    singleOption = opts[0]
    self.assertTrue(singleOption in newSection)

  def test_add_section_to_section(self):
    newSection = self.gConfig.addSection("UND")
    subsect = newSection.addSubSection("Hockey")
    self.assertTrue(subsect)
    self.assertTrue(subsect in newSection)
    self.assertFalse(newSection in subsect)

    anotherSection = self.gConfig.addSection("UMN")
    self.assertFalse(anotherSection in newSection)

  def test_add_section(self):
    newSection = self.gConfig.addSection('Scott')
    tlSections = self.gConfig.getTopLevelSections()
    self.assertTrue(newSection in tlSections)
    self.assertTrue(newSection)

  def test_split_attributes_string(self):
    attributesString = '[Alpha=One,Beta="Two",Gamma=William Shakespeare]'
    attrs = Configurator.splitAttributesString(attributesString)
    self.assertTrue('Alpha' in attrs.keys())
    self.assertEquals('One', attrs['Alpha'])
    self.assertEquals('Two', attrs['Beta'])
    self.assertEquals('William Shakespeare', attrs['Gamma'])

  def test_split_section_and_attributes(self):
    sectionName = "SomeSection"
    attributes = '[AttributeA=something]'
    totalSection = sectionName + attributes
    (resultSection, resultAttributes) = Configurator.splitSectionAndAttributes(totalSection)
    self.assertEquals(sectionName, resultSection)
    self.assertEquals(attributes, resultAttributes)

  def test_add_subsection_with_attributes(self):
    section = Section(self.gConfig, 'Fruit', None)
    subsection = section.addSubSection('Banana[color="yellow"]')
    xmlString = '<?xml version="1.0" ?><Configuration><Fruit><Banana color="yellow"/></Fruit></Configuration>'

    self.assertTrue(subsection.hasAttributes())
    self.assertTrue(section.hasSubSections())
    self.assertFalse(subsection.hasSubSections())
    self.assertEquals('Banana', subsection.getName())
    self.assertEquals('yellow', subsection.getAttributeByName('color').getValue())
    self.assertEquals(xmlString, self.gConfig.getDocument().toxml())

if __name__ == '__main__':
  unittest.main()
