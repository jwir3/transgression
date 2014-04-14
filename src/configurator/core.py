'''
configurator.py
Configuration utilites

Based off of JMozConfig, from github.com/jwir3/JMozTools

@author: Scott Johnson <jaywir3@gmail.com>
'''

import os.path;
import sys
import time

from xml.dom.minidom import parseString
from xml.dom.minidom import getDOMImplementation
from prettylogger.core import PrettyLogger
from xml.parsers.expat import ExpatError

gLogger = PrettyLogger(True, False, False)

class Attribute:
  """
     A unique attribute on a section. The concatenation of all attributes
     of a section is essentially the same as a unique identifier for a
     section.
  """
  __mName = None
  __mValue = None
  __mSection = None

  def __init__(self, aSection, aName, aValue):
    self.__mName = aName
    self.__mValue = aValue
    self.__mSection = aSection

  def __eq__(self, aOther):
    # We only compare name and value, because the section eq() method
    # compares these, so comparing sections would result in infinite
    # regression.
    return self.getName() == aOther.getName() and self.getValue() == aOther.getValue()

  def getName(self):
    return self.__mName

  def getValue(self):
    return self.__mValue

class Option:
  """
     An option within the configuration file. Has a Section as a parent.
     Note that the value can be updated, but the name must remain the same once
     created.
  """
  __mName = None
  __mValue = None
  __mParentSection = None
  __mElement = None

  def __init__(self, aName, aValue, aParentSection):
    self.__mName = aName
    self.__mValue = aValue
    self.__mParentSection = aParentSection

  def __str__(self):
    return "[Option: " + self.__mName + "=" + self.__mValue + "]"

  def __eq__(self, aOther):
    namesEqual = self.__mName == aOther.getName()
    valuesEqual = self.__mValue == aOther.getValue()
    return namesEqual and valuesEqual

  def getName(self):
    return self.__mName

  def getSection(self):
    return self.__mParentSection

  def getValue(self):
    return self.__mValue

  def setValue(self, aValue):
    self.__mValue = aValue
    self.updateXML()

  def createNewXMLElement(self):
    document = self.__mParentSection.getElement().ownerDocument
    newElement = document.createElement('option')
    newElement.setAttribute('name', self.__mName)
    newValue = document.createTextNode(self.__mValue)
    newElement.appendChild(newValue)
    return newElement

class Section:
  """
     A section within the configuration file. Sections can have options
     associated with them directly, or can have subsections underneath them.
  """
  __mName = None
  __mElement = None
  __mParentConfigurator = None
  __mParentSection = None
  __mOptionsList = []
  __mSubSectionList = []
  __mAttrList = []

  def __init__(self, aParentConfigurator, aName, aParent, aAttrs={}):
    global gLogger
    self.__mName = aName
    self.__mParentSection = aParent
    self.__mParentConfigurator = aParentConfigurator
    self.__mOptionsList = []
    self.__mSubSectionList = []
    self.__mAttrList = []

    for attributeName in aAttrs.keys():
      self.__mAttrList.append(Attribute(self, attributeName, aAttrs[attributeName]))

  def __str__(self):
    return "Section: <" + self.__mName + ">"

  def __eq__(self, aOther):
    namesEqual = self.__mName == aOther.getName()
    parentsEqual = self.__mParentConfigurator == aOther.getConfigurator()
    pathsEqual = self.getPath() == aOther.getPath()

    optionsEqual = self.optionsEqual(aOther)
    attrsEqual = self.attributesEqual(aOther)

    return namesEqual and parentsEqual and pathsEqual and optionsEqual and attrsEqual

  def __contains__(self, aThing):
    if isinstance(aThing, Attribute):
      return aThing in self.getAttributes()
    elif isinstance(aThing, Section):
      return aThing in self.getSubSections()
    elif isinstance(aThing, Option):
      return aThing in self.getOptions()

    return False

  # TODO: Make private.
  def attributesEqual(self, aOther):
    numAttrsEqual = len(self.getAttributes()) == len(aOther.getAttributes())
    return numAttrsEqual

  # TODO: Make private.
  def subSectionsEqual(self, aOther):
    subSectionsSelf = self.getSubSections()
    subSectionsOther = aOther.getSubSections()
    numSubSectionsEqual = len(subSectionsSelf) == len(subSectionsOther)
    subSectionsEqual = numSubSectionsEqual
    i = 0
    for subSection in subSectionsSelf:
      if subSectionsEqual:
        subSectionsEqual = subSectionsEqual and (subSection == subSectionsOther[i])
        i = i + 1
    return subSectionsEqual

  # TODO: Make private.
  def optionsEqual(self, aOther):
    optionsSelf = self.getOptions()
    optionsOther = aOther.getOptions()
    optionsEqual = len(optionsSelf) == len(optionsOther)
    j = 0
    for option in optionsSelf:
      if optionsEqual:
        optionsEqual = optionsEqual and (option == optionsOther[j])
      j = j + 1
    return optionsEqual

  def getAttributes(self):
    return self.__mAttrList

  def getPath(self):
    if self.isTopLevelSection():
      return self.getName()

    return self.getParentSection().getPath() + "." + self.getName()

  def getParentSection(self):
    return self.__mParentSection

  def isTopLevelSection(self):
    if not self.__mParentSection:
      return True
    return False

  def getConfigurator(self):
    return self.__mParentConfigurator

  def getName(self):
    return self.__mName

  def getElement(self):
    global gLogger
    gLogger.debug("Section: " + str(self))
    if not self.__mElement:
      parentSection = self.getParentSection()
      gLogger.debug("Parent section: " + str(parentSection))
      if not parentSection:
        # This is a top-level section.
        parentElement = self.getConfigurator().getTopElement()
      else:
        parentElement = parentSection.getElement()

      gLogger.debug("getElement(): parentElement - " + str(parentElement))
      document = self.getConfigurator().getDocument()
      newSectionElement = document.createElement(self.getName())
      for attribute in self.getAttributes():
        newSectionElement.setAttribute(attribute.getName(), attribute.getValue())
      parentElement.appendChild(newSectionElement)
      gLogger.debug("getElement(): element - " + str(newSectionElement))

      # Add our attributes to the XML
      for attribute in self.getAttributes():
        newSectionElement.setAttribute(attribute.getName(), attribute.getValue())

      self.__mElement = newSectionElement

    return self.__mElement

  def invalidateElement(self):
    self.__mElement = None

  def hasOptions(self):
    global gLogger
    return len(self.__mOptionsList) != 0

  def hasSubSections(self):
    #self.repopulateSubSectionList()
    return len(self.__mSubSectionList) != 0

  def hasAttributes(self):
    return len(self.getAttributes()) != 0

  def isEmpty(self):
    return not self.hasOptions() and not self.hasSubSections()

  def addSubSection(self, aSubSectionName):
    global gLogger
    # Split out the attributes and section name
    (sectionName, attribString) = Configurator.splitSectionAndAttributes(aSubSectionName)
    attribDict = Configurator.splitAttributesString(attribString)
    newSection = Section(self.__mParentConfigurator, sectionName, self, attribDict)
    self.getSubSections().append(newSection)
    self.triggerXMLUpdate()
    return newSection

  def containsAttributes(self, aAttrs):
    global gLogger
    allAttributes = self.getAttributes()
    gLogger.debug("Type of aAttrs: " + str(type(aAttrs)))
    for needleAttr in aAttrs.keys():
      foundAttributeName = False
      foundAttributeValue = False
      for attribute in allAttributes:
        if attribute.getName() == needleAttr:
          foundAttributeName = True
          if attribute.getValue() == aAttrs[needleAttr]:
            foundAttributeValue = True
            break
      if not (foundAttributeValue and foundAttributeName):
        return False
    return True

  def findSubSectionsByNameWithAttributes(self, aSectionName, aAttrs):
    foundSections = []
    for nextSubSection in self.getSubSections():
      if nextSubSection.containsAttributes(aAttrs):
        foundSections.append(nextSubSection)
    return foundSections

  def createSubSectionByPath(self, aPath):
    global gLogger
    splitPath = aPath.split(".")
    nextSection = self
    for nextSectionName in splitPath:
      gLogger.debug("Adding new subsection: " + nextSectionName)
      nextSection = nextSection.addSubSection(nextSectionName)
      gLogger.debug("Next section has options? " + str(nextSection.hasOptions()))
    self.triggerXMLUpdate()

  def getAttributeByName(self, aAttributeName):
    for attribute in self.getAttributes():
      if attribute.getName() == aAttributeName:
        return attribute
    return None

  def addAttributes(self, aAttribDict):
    for attribKey in aAttribDict:
      self.addAttribute(attribKey, aAttribDict[attribKey])

  def addAttribute(self, aAttributeName, aAttributeValue):
    attribute = Attribute(self, aAttributeName, aAttributeValue)
    self.getAttributes().append(attribute)
    self.triggerXMLUpdate()

  def setOption(self, aOptionName, aOptionValue):
    newOption = Option(aOptionName, aOptionValue, self)
    for option in self.getOptions():
      if newOption == option:
        return option
    self.getOptions().append(newOption)
    return newOption

  def triggerXMLUpdate(self):
    # Update our XML document to contain this particular section.
    element = self.getElement()

    for section in self.getSubSections():
      section.triggerXMLUpdate()

  def getOptions(self):
    return self.__mOptionsList

  def getSubSections(self):
    return self.__mSubSectionList

  def getSubSection(self, aSectionName):
    global gLogger

    # Split the section name out from the attributes
    (sectionName, attributesString) = Configurator.splitSectionAndAttributes(aSectionName)
    gLogger.debug("***** DEBUG_jwir3: Section Name: " + sectionName + ", attributesString: " + str(attributesString))
    attribDict = Configurator.splitAttributesString(attributesString)
    gLogger.debug("***** DEBUG_jwir3: AttribDict: " + str(attribDict))
    gLogger.debug("***** DEBUG_jwir3: Subsections: " + str(self.getSubSections()))
    for section in self.getSubSections():
      if not attribDict:
        if section.getName() == sectionName:
          return section
      else:
        if section.getName() == sectionName and section.containsAttributes(attribDict):
          return section
    return None

  def getOption(self, aOptionName):
    for option in self.__mOptionsList:
      if option.getName() == aOptionName:
        return option
    return None

  def createOption(self, aOptionName, aOptionValue):
    newOption = Option(aOptionName, aOptionValue, self)
    self.__mOptionsList.append(newOption)

class InvalidPathException(Exception):
  __mInvalidPath = None
  __mValidPath = None
  __mType = None

  def __init__(self, aType, aValidPath, aInvalidPath):
    self.__mInvalidPath = aInvalidPath
    self.__mValidPath = aValidPath
    self.__mType = aType

  def __str__(self):
    return "v(" + self.__mValidPath + "), iv(" + self.__mInvalidPath + ")"

  def getType(self):
    return self.__mType

  def getValidPath(self):
    return self.__mValidPath

  def getInvalidPath(self):
    return self.__mInvalidPath

# An object representing a config file with the following XML structure:
#
# <Configuration>
#   <SectionName>
#     <option name="...">value</option>
#   </SectionName>
# </Configuration>
class Configurator:
  # === [ Public API ] =========================================================

  def __init__(self, aConfigFilePath, aGlobal=False, aDebugOutput=False):
    global gLogger
    if aDebugOutput:
      gLogger = PrettyLogger(True, True, True)
    # Some member variable declarations so we don't forget to init them.
    self.mConfigDocument = None
    self.mConfigFilePath = None
    self.mConfigDirPath = None
    self.mIsGlobal = aGlobal
    self.__mTopLevelSections = []

    if (self.mIsGlobal):
      self.mConfigFilePath = aConfigFilePath
    else:
      self.mConfigFilePath = os.path.join('~', aConfigFilePath)

    self.mConfigFilePath = os.path.expanduser(self.mConfigFilePath)

    gLogger.debug("Searching for config file at: " + self.mConfigFilePath)
    self.ensureConfigFileCreated(self.mConfigFilePath)

  def __eq__(self, aOther):
    return self.mConfigFilePath == aOther.getConfigFilePath()

  def __contains__(self, aSection):
    if isinstance(aSection, Section):
      for section in self.getTopLevelSections():
        if aSection == section:
          return True
        if aSection in section:
          return True

    return False

  def ensureConfigDirCreated(self, aConfigFilePath):
    # TODO: If we intend to support msys at some later date, we should re-enable
    #       this old code from JMozTools
    #if isMsys():
    #    # If we're on msys, then the config dir path
    #    # should be C:\Users\<user>\...
    #    appData = os.environ['APPDATA']
    #    homeDir = os.path.split(appData)[0]
    #    homeDir = os.path.split(homeDir)[0]
    #    self.mConfigDirPath = os.path.join(homeDir, self.mConfigDirPath)

    self.mConfigDirPath = os.path.dirname(aConfigFilePath)

    if not os.path.exists(self.mConfigDirPath):
        os.mkdir(self.mConfigDirPath);

  def ensureConfigFileCreated(self, aConfigFilePath):
    self.ensureConfigDirCreated(aConfigFilePath)
    if not os.path.exists(self.mConfigFilePath):
      domImpl = getDOMImplementation()
      self.mConfigDocument = domImpl.createDocument('', 'Configuration', None)
      self.writeDocumentToConfigFile()

  def getConfigFilePath(self):
    return self.mConfigFilePath

  def addOptionByPath(self, aOptionPath, aOptionValue):
    global gLogger
    splitPath = aOptionPath.split(".")
    optionName = splitPath[len(splitPath) - 1]
    sectionPath = ".".join(splitPath[:len(splitPath)-1])
    gLogger.debug("Section path: " + sectionPath)
    self.addSectionByPath(sectionPath)
    section = self.getSectionByPath(sectionPath)
    return section.setOption(optionName, aOptionValue)

  def addSectionByPath(self, aPath):
    global gLogger
    gLogger.debug("Creating section by path for path: " + aPath)
    try:
      self.getSectionByPath(aPath)
    except InvalidPathException as ivpException:
      validPath = ivpException.getValidPath()
      invalidPath = ivpException.getInvalidPath()
      gLogger.debug("Valid path: " + validPath)
      gLogger.debug("Invalid path: " + invalidPath)
      if validPath != '':
        validSection = self.getSectionByPath(validPath)
        validSection.createSubSectionByPath(invalidPath)
      else:
        splitPath = invalidPath.split(".")
        tlSection = self.addSection(splitPath[0])
        tlSection.createSubSectionByPath(".".join(splitPath[1:len(splitPath)]))
    return self.getSectionByPath(aPath)

  def getOptionByPath(self, aOptionPath):
    global gLogger
    splitPath = aOptionPath.split(".")
    gLogger.debug("Split path is: " + str(splitPath))
    optionName = splitPath[len(splitPath)-1]
    gLogger.debug("Option name is: " + optionName)
    sectionPath = ".".join(splitPath[:len(splitPath)-1])
    gLogger.debug("Section path is: " + sectionPath)
    section = self.getSectionByPath(sectionPath)
    gLogger.debug("Found: " + str(section))
    return section.getOption(optionName)

  # TODO: We should rename this to findSectionByPath
  def getSectionByPath(self, aSectionPath):
    global gLogger

    gLogger.debug("Top level sections: ")
    for sec in self.getTopLevelSections():
      gLogger.debug(str(sec))
    splitPath = aSectionPath.split('.')
    gLogger.debug("splitPath: " + str(splitPath))
    if len(splitPath) == 0:
      raise ValueError("Cannot have an empty path")
    i = 0
    nextSectionName = splitPath[i]
    (nextSectionName, attributes) = Configurator.splitSectionAndAttributes(nextSectionName)
    attribDict = Configurator.splitAttributesString(attributes)
    gLogger.debug("Next path to search for: " + nextSectionName)
    nextSection = self.getTopLevelSection(nextSectionName, attribDict)
    gLogger.debug("Found nextSection: " + str(nextSection))
    if not nextSection:
      raise InvalidPathException('section', '', aSectionPath)
    i = i + 1
    totalPath = nextSectionName
    while i < len(splitPath):
      nextSectionName = splitPath[i]
      gLogger.debug("Next section(before update): " + str(nextSection))
      nextSection = nextSection.getSubSection(nextSectionName)
      gLogger.debug("Got next section: " + str(nextSection))
      if not nextSection:
        raise InvalidPathException('section', totalPath, ".".join(splitPath[i:]))
      totalPath = totalPath + "." + nextSectionName
      i = i + 1

    return nextSection

  @staticmethod
  def splitSectionAndAttributes(aSectionName):
    # If we don't have a set of enclosing brackets, then the
    # section name is just what was given.
    if "[" in aSectionName and "]" in aSectionName:
      firstIndex = aSectionName.find("[")
      secondIndex = aSectionName.find("]")
      return (aSectionName[0:firstIndex], aSectionName[firstIndex:secondIndex+1])

    return (aSectionName, None)

  @staticmethod
  def splitAttributesString(aAttributesString):
    if not aAttributesString:
      # Nothing to do
      return {}

    finalAttributesDict = {}

    # Remove braces
    workingAttributes = aAttributesString[1:len(aAttributesString)-1]

    # Each attribute should be delimited by a comma
    attributePairs = workingAttributes.split(",")

    for singleAttributeKeyValue in attributePairs:
      # Remove any quotes
      singleAttributeKeyValue = singleAttributeKeyValue.replace('"', '')

      # Split each of the pairs based on the equals sign
      equalsPosition = singleAttributeKeyValue.find('=')
      key = singleAttributeKeyValue[0:equalsPosition]
      value = singleAttributeKeyValue[equalsPosition+1:len(singleAttributeKeyValue)]
      finalAttributesDict[key] = value

    return finalAttributesDict

  def getTopElement(self):
    document = self.getDocument()
    configElements = document.getElementsByTagName('Configuration')
    return configElements[0]

  def addSection(self, aSectionName, aParentSection=None):
    global gLogger
    parentElement = None
    if not aParentSection:
      # Then this is a top-level section, and so it's xml parent
      # should be the '<Configuration>' element.
      parentElement = self.getTopElement()
    else:
      parentElement = aParentSection.getElement()

    gLogger.debug("Parent element: " + str(parentElement))

    # We split out any potential attributes from this section
    # string, and use them later.
    (sectionName, attribString) = Configurator.splitSectionAndAttributes(aSectionName)
    gLogger.debug("***** DEBUG_jwir3: Saw sectionName: " + sectionName + " and attribString: " + str(attribString))
    newSection = Section(self, sectionName, aParentSection)

    # Add the attributes to the new section
    attribDict = Configurator.splitAttributesString(attribString)
    newSection.addAttributes(attribDict)

    newSection.invalidateElement()
    newSectionElement = newSection.getElement()
    gLogger.debug("New Section Element: " + str(newSectionElement))
    parentElement.appendChild(newSectionElement)
    gLogger.debug("New section's parent element: " + newSectionElement.parentNode.tagName)
    self.__mTopLevelSections.append(newSection)
    self.writeDocumentToConfigFile()
    return newSection

  def getTopLevelSections(self):
    return self.__mTopLevelSections

  def getTopLevelSection(self, aSectionName, aAttributes=None):
    for topSection in self.getTopLevelSections():
      if aAttributes:
        if topSection.getName() == aSectionName and topSection.containsAttributes(aAttributes):
          return topSection
      else:
        if topSection.getName() == aSectionName:
          return topSection
    return None

  # TODO: This probably needs to be reworked to be in line with new logic
  #       of how we construct our XML documents.
  def writeDocumentToConfigFile(self):
    document = self.mConfigDocument
    configFilePath = self.mConfigFilePath

    documentXml = document.toxml()
    documentXml = documentXml.replace("\n", "")
    document = parseString(documentXml)
    documentPrettyXml = document.toprettyxml()
    basicConfigFile = open(configFilePath, 'w');
    basicConfigFile.write(documentPrettyXml);
    basicConfigFile.flush();
    basicConfigFile.close();

  # === [ Private API ] =======================================================

  def getDocument(self):
    if not self.mConfigDocument:
      configFile = self.getConfigFile()
      configFileHandle = open(configFile, 'r')

      # Strip all newlines
      documentXml = ''.join(l.rstrip().lstrip() for l in configFileHandle)

      configFileHandle.close()
      try:
        self.mConfigDocument = parseString(documentXml)
      except ExpatError:
        # This would likely indicate that the configuration file is
        # corrupt, so let's remove it and start over.
        os.remove(configFile)
        return self.getDocument()

    return self.mConfigDocument

  def isWindows(self):
    if os.name == 'nt':
      return True

    return False

  def isUnix(self):
    if os.name == 'posix':
      return True

    return False

  def isMsys(self):
    try:
      ostype = os.environ['OSTYPE']
      if ostype == 'msys':
        return True
    except KeyError:
      if 'MSYSTEM' in os.environ.keys():
        return True
    return False