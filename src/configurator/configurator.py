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
from prettylogger import PrettyLogger

gLogger = PrettyLogger(True, False, False)

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
    if not self.findXMLElement():
      self.addElementToDocument()

  def getName(self):
    return self.__mName

  def getValue(self):
    return self.__mValue

  def setValue(self, aValue):
    self.__mValue = aValue
    self.updateXML()

  def findXMLElement(self):
    parentElement = self.__mParentSection.getElement()
    for childNode in parentElement.childNodes:
      if childNode.tagName == 'option' and childNode.getAttribute('name') == self.__mName:
        self.__mElement = childNode

    return self.__mElement

  def updateXML(self):
    newElement = self.createNewXMLElement()
    self.__mElement.parentNode.replaceChild(newElement, self.__mElement)
    self.__mElement = newElement
    self.__mParentSection.triggerXMLUpdate()

  def addElementToDocument(self):
    newElement = self.createNewXMLElement()
    self.__mElement = newElement
    self.__mParentSection.getElement().appendChild(self.__mElement)
    self.__mParentSection.triggerXMLUpdate()

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
  __mOptionsList = []
  __mSubSectionList = []

  def __init__(self, aParentConfigurator, aName, aConfigXMLElement):
    self.__mName = aName
    self.__mElement = aConfigXMLElement
    self.__mParentConfigurator = aParentConfigurator
    self.repopulateOptionsList()
    self.repopulateSubSectionList()

  def __str__(self):
    return "Section: <" + self.__mName + ">"

  def getConfigurator(self):
    return self.__mParentConfigurator

  def getName(self):
    return self.__mName

  def getElement(self):
    return self.__mElement

  def hasOptions(self):
    self.repopulateOptionsList()
    return len(self.__mOptionsList) == 0

  def hasSubSections(self):
    self.repopulateSubSectionList()
    return len(self.__mSubSectionList) == 0

  def isEmpty(self):
    return not self.hasOptions() and not self.hasSubSections()

  def createSubSectionByPath(self, aPath):
    splitPath = aPath.split(".")
    nextSection = self
    for nextSectionName in splitPath:
      nextSection = nextSection.addSubSection(nextSectionName)
    self.triggerXMLUpdate()

  def setOption(self, aOptionName, aOptionValue):
    global gLogger
    document = self.__mElement.ownerDocument
    madeChange = False
    foundOption = False

    # First, make sure that the option doesn't already exist
    for option in self.__mOptionsList:
      if option.getName() == aOptionName:
        foundOption = True
        gLogger.debug("Found option. Updating.")
        if option.getValue() != aOptionValue:
          option.setValue(aOptionValue)
          break

    if not foundOption:
      gLogger.debug("Didn't find option, so creating new one.")
      self.createOption(aOptionName, aOptionValue)
      madeChange = True

    if madeChange:
      gLogger.debug("Made change, so outputting configuration file.")
      self.triggerXMLUpdate()

  def triggerXMLUpdate(self):
    self.__mParentConfigurator.writeDocumentToConfigFile()

  def addSubSection(self, aSubSectionName):
    self.repopulateSubSectionList()

    # Make sure we don't already have a subsection with this name
    foundSection = False
    for section in self.__mSubSectionList:
      if section.getName() == aSubSectionName:
        foundSection = True

    if not foundSection:
      # Create the new section XML element
      document = self.__mElement.ownerDocument
      sectionElement = document.createElement(aSubSectionName)
      self.__mElement.appendChild(sectionElement)
      newSection = Section(self.__mParentConfigurator, aSubSectionName, sectionElement)
      self.triggerXMLUpdate()
      return newSection

    return None

  def getOptionsList(self):
    self.repopulateOptionsList()
    return self.__mOptionsList

  def getSubSections(self):
    return self.__mSubSectionList

  def repopulateSubSectionList(self):
    self.__mSubSectionList = []
    for childNode in self.__mElement.childNodes:
      if childNode.tagName != 'option':
        sectionName = childNode.tagName
        newSection = Section(self.__mParentConfigurator, sectionName, childNode)
        self.__mSubSectionList.append(newSection)

  def repopulateOptionsList(self):
    self.__mOptionsList = []
    for childNode in self.__mElement.childNodes:
      if childNode.tagName == 'option':
        optionName = childNode.getAttribute('name')
        optionValue = childNode.firstChild.data
        newOption = Option(optionName, optionValue, self)
        self.__mOptionsList.append(newOption)

  def getSubSection(self, aSectionName):
    for section in self.__mSubSectionList:
      if section.getName() == aSectionName:
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

  #def createOptionElement(self, aOptionName, aOptionValue, aDocument):
  #  optionElement = aDocument.createElement('option')
  #  optionElement.setAttribute('name', aOptionName)
  #  textNode = aDocument.createTextNode(aOptionValue)
  #  optionElement.appendChild(textNode)
  #  return optionElement

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
      #createNewOptionsSection()
      self.writeDocumentToConfigFile()

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

  def createOptionByPath(self, aOptionPath, aOptionValue):
    splitPath = aOptionPath.split(".")
    optionName = splitPath[len(splitPath) - 1]
    sectionPath = ".".join(splitPath[:len(splitPath)-1])
    self.createSectionByPath(sectionPath)
    section = self.getSectionByPath(sectionPath)
    section.setOption(optionName, aOptionValue)

  def createSectionByPath(self, aPath):
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
        tlSection = self.addSectionToConfig(splitPath[0])
        tlSection.createSubSectionByPath(".".join(splitPath[1:len(splitPath)]))

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

  def getSectionByPath(self, aSectionPath):
    global gLogger
    splitPath = aSectionPath.split('.')
    gLogger.debug("splitPath: " + str(splitPath))
    if len(splitPath) == 0:
      raise ValueError("Cannot have an empty path")
    i = 0
    nextSectionName = splitPath[i]
    gLogger.debug("Saw next section named: " + nextSectionName)
    nextSection = self.getTopLevelSection(nextSectionName)
    if not nextSection:
      raise InvalidPathException('section', '', aSectionPath)
    i = i + 1
    totalPath = nextSectionName
    while i < len(splitPath):
      nextSectionName = splitPath[i]
      nextSection = nextSection.getSubSection(nextSectionName)
      if not nextSection:
        raise InvalidPathException('section', totalPath, ".".join(splitPath[i:]))
      totalPath = totalPath + "." + nextSectionName
      i = i + 1

    return nextSection

  def addSectionToConfig(self, aSectionName, aSectionParentName='Configuration'):
   document = self.getDocument()
   allElementsWithParentName = document.getElementsByTagName(aSectionParentName)

   for element in allElementsWithParentName:
     childrenWithTag = element.getElementsByTagName(aSectionName)
     if childrenWithTag.length > 0:
       # Cowardly refuse to add another duplicate child element
       continue

     newSectionElement = document.createElement(aSectionName)
     element.appendChild(newSectionElement)

   self.writeDocumentToConfigFile()
   self.repopulateTopLevelSections()
   return self.getTopLevelSection(aSectionName)

  def getTopLevelSections(self):
    return self.__mTopLevelSections

  def getTopLevelSection(self, aSectionName):
    for topSection in self.getTopLevelSections():
      if topSection.getName() == aSectionName:
        return topSection
    return None

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

  def repopulateTopLevelSections(self):
    self.__mTopLevelSections= []
    rootElement = self.mConfigDocument.documentElement
    for child in rootElement.childNodes:
      childSection = Section(self, child.tagName, child)
      self.__mTopLevelSections.append(childSection)

  def getDocument(self):
    if not self.mConfigDocument:
      configFile = self.getConfigFile()
      configFileHandle = open(configFile, 'r')

      # Strip all newlines
      documentXml = ''.join(l.rstrip().lstrip() for l in configFileHandle)

      configFileHandle.close()
      self.mConfigDocument = parseString(documentXml)
      self.repopulateTopLevelSections()

    return self.mConfigDocument

## =============== USER INTERFACE SECTION ===============

  def getConfigFile(self):
    self.ensureConfigFileCreated(self.mConfigFilePath)
    return self.mConfigFilePath

#def getMainElement():
#    global gMainElement
#    if gMainElement == '':
#        document = getDocument()
#        mainElements = document.getElementsByTagName("JMozTools")
#    
#        if len(mainElements) > 1 :
#            sys.stderr.write("There was more than one JMozTools element detected.\n")
#            return ''
#    
#        gMainElement = mainElements[0]
#    
#    return gMainElement
#
## Retrieves the <cache> element of the xml document for JMozTools.
#def getCacheElement():
#    global gCacheElement
#    if gCacheElement:
#        return gCacheElement
#    
#    mainElement = getMainElement()
#    caches = mainElement.getElementsByTagName("Cache")
#    # There should only be a single cache
#    if len(caches) == 0:
#        gCacheElement = createCacheInConfig()
#        
#    elif len(caches) > 1:
#        print("Warning: JMozConfig detected multiple <cache> elements in " + getConfigFile())
#        gCacheElement = caches[0]
#    else:
#        gCacheElement = caches[0]
#
#    return gCacheElement
#
## Get all of the aliases known from the configuration file.
##
## @return A dictionary of aliases, with keys as the alias name, and
##         the value the name of the project to which it points.
#def getAliases():
#  allAliases = {}
#  mainElement = getMainElement()
#  aliasesElement = mainElement.getElementsByTagName("Aliases")
#  if (len(aliasesElement) == 0):
#    return allAliases
#
#  aliasElements = aliasesElement[0].getElementsByTagName("Alias")
#  if (len(aliasElements) == 0):
#    return allAliases
#
#  for ele in aliasElements:
#    aliasName = ele.getAttribute('name')
#    aliasFor = ele.getAttribute('for')
#    # We need to verify that the project to which the alias is pointing actually
#    # exists.
#    if not findProject(aliasFor):
#      aliasFor = ''
#
#    if aliasFor and aliasName:
#      allAliases[aliasName] = aliasFor
#
#  return allAliases
#
#def getAliasTarget(aliasName):
#  aliases = getAliases()
#  if not aliasName in aliases.keys():
#    raise Exception('Alias "' + aliasName + '" is not an alias')
#  return aliases[aliasName]
#
## Determine if an alias already exists
##
## @return True, if the alias already exists in the config file,
##         False, otherwise.
#def doesAliasExist(aliasName):
#  aliases = getAliases()
#  if aliasName in aliases.keys():
#    return True
#  return False
#
#def getCacheForUtility(aUtility):
#    global gPossibleUtilities
#    
#    if not aUtility in gPossibleUtilities:
#        raise StandardError("ERROR: " + aUtility + " not in list of approved JMozTools utilities. Refusing to create cache storage.")
#    
#    cacheElement = getCacheElement()
#    utils = cacheElement.getElementsByTagName(aUtility)
#    if len(utils) == 0:
#        return createCacheForUtility(aUtility)
#    else:
#        return utils[0]
#    
#def findProject(projName):
#    mainElement = getMainElement()
#    projects = mainElement.getElementsByTagName("Project");
#    for project in projects :
#        nameAttr = project.getAttribute('name')
#        if nameAttr == projName : 
#            return project
#    
#    # Try to find it as an alias of another project
#    aliases = getAliases()
#    if (projName in aliases.keys()):
#      return findProject(aliases[projName])
#    return ''
#
#def getTrackedProjectNames():
#    mainElement = getMainElement()
#    projects = mainElement.getElementsByTagName("Project")
#    allProjNames = []
#
#    for project in projects:
#        nameAttr = project.getAttribute('name')
#        allProjNames.append(nameAttr)
#    
#    return allProjNames
#
#def getTrackedObjDirectories():
#    projects = getTrackedProjectNames()
#    trackedObjDirs = []
#    for projName in projects:
#        objDir = getObjDirectoryFor(projName)
#        trackedObjDirs.append(objDir)
#    
#    return trackedObjDirs
#
#def getObjDirectoryFor(projName):
#    project = findProject(projName)
#    if project == '' :
#        # Project doesn't exist yet.
#        sys.stderr.write("Project name: '" + projName + "' not recognized.\n")
#        if not promptCreateProject(projName):
#            return False
#        
#    projectElement = findProject(projName)
#    if projectElement == '' :
#        return False
#    
#    directories = projectElement.getElementsByTagName('Directory')
#    for directory in directories :
#        nameAttr = directory.getAttribute('name')
#        if nameAttr == 'obj' :
#            dirPath = directory.firstChild
#            return dirPath.data.rstrip().lstrip()
#    return False
#
#def getSrcDirectoryFor(projName):
#    project = findProject(projName)
#    if project == '' :
#        # Project doesn't exist yet.
#        sys.stderr.write("Project name: '" + str(projName) + "' not recognized.\n")
#        if not promptCreateProject(projName):
#            return False
#        
#    projectElement = findProject(projName)
#    if projectElement == '' :
#        return False
#    
#    directories = projectElement.getElementsByTagName('Directory')
#    for directory in directories :
#        nameAttr = directory.getAttribute('name')
#        if nameAttr == 'src' :
#            dirPath = directory.firstChild
#            return dirPath.data.rstrip().lstrip()
#    return False
#
#def setLastProject(projName):
#    mainElement = getMainElement()
#    optionsElement = mainElement.getElementsByTagName('Options')[0]
#    lastProjectElement = optionsElement.getElementsByTagName('LastProject')[0]
#    lastProjectElement.setAttribute('name', projName)
#    writeDocumentToConfigFile()
#    return
#
#def resetLastProjectToKnownGood():
#    mainElement = getMainElement()
#    firstProjectElement = mainElement.getElementsByTagName('Project')[0]
#    setLastProject(firstProjectElement.getAttribute('name'))
#
#def getAllProjectElements():
#  mainElement = getMainElement()
#  projects = mainElement.getElementsByTagName('Project')
#  return projects
#
#def getLastProject():
#    mainElement = getMainElement()
#    optionsElement = mainElement.getElementsByTagName('Options')[0]
#    lastProjectElement = optionsElement.getElementsByTagName('LastProject')[0]
#    return lastProjectElement.getAttribute('name')
#
#def isMobile(projName):
#    proj = findProject(projName)
#    mobile = proj.getAttribute('isMobile')
#    if mobile == 'y' or mobile == 'Y':
#        return True
#    
#    return False
#
## Removes all <TempFile> elements that are children of a particular <Cache>
## <Utility-Name> entry from the XML configuration file. Note that this does
## not actually remove the temporary file if it exists on the hard disk.
##
## @param aUtility: The utility for which to remove temp file entries.
#def removeTempFilePathsForUtilityFromConfig(aUtility):
#    global gPossibleUtilities
#    
#    if not aUtility in gPossibleUtilities:
#        raise StandardError("ERROR: " + aUtility + " not in list of approved JMozTools utilities. Refusing to remove cache storage.")
#  
#    cache = getCacheForUtility(aUtility)
#    
#    for tempFile in cache.getElementsByTagName("TempFile"):
#        cache.removeChild(tempFile)
#        
#    writeDocumentToConfigFile()
#
## Writes a temporary file name to the XML configuration file that a particular
## utility uses.
##
## @param aUtility: The name of the utility that is using this temporary file.
## @param aTempFilename: The name of a temporary file being written to by JMozTools.
##
## @return: True, if the function wrote a new TempFile entry to the config cache,
##          False, otherwise.
##
#def writeTempFilePathToConfigCache(aUtility, aTempFilename):
#    # Temporary file entries are of the form:
#    # <Cache>
#    #   <Utility-Name>
#    #     <TempFile date="DOW MON DD HH:MM:SS YYYY" path="/path/to/file/" />
#    #  </Utility-Name>
#    # </Cache>
#    try:
#        cache = getCacheForUtility(aUtility)
#    except:
#        print(sys.exc_info()[0])
#        print("A fatal error was detected. Terminating.")
#        sys.exit(1)
#    
#    document = getDocument()
#    tempFilePath = os.path.abspath(aTempFilename)
#    
#    # Verify that a temporary file path doesn't already exist for this element
#    for existingElement in getTempFilePathsForUtility(aUtility):
#        if existingElement.getAttribute("path") == tempFilePath:
#            return False
#
#    tempFileElement = document.createElement("TempFile")
#    
#    if not os.path.exists(aTempFilename):
#        raise StandardError("ERROR: " + tempFilePath + " does not exist.")
#    
#    creationTime = time.ctime(os.path.getctime(tempFilePath))
#    tempFileElement.setAttribute("date", creationTime)
#    tempFileElement.setAttribute("path", tempFilePath)
#    
#    cache.appendChild(tempFileElement)
#    
#    writeDocumentToConfigFile()
#    
#    return True
#
#def getTempFilePathsForUtility(aUtility):
#    global gPossibleUtilities
#    
#    if not aUtility in gPossibleUtilities:
#        raise StandardError("ERROR: " + aUtility + " not in list of approved JMozTools utilities. Refusing to retrieve cache storage.")
#
#    cache = getCacheForUtility(aUtility)
#    
#    return cache.getElementsByTagName("TempFile")
#
## ============ DOCUMENT CONSTRUCTION SECTION =============
#
#def deleteProjectFromConfig(projName):
#    mainElement = getMainElement()
#    project = findProject(projName)
#    mainElement.removeChild(project)
#
## Creates the <cache> element of the XML configuration file for JMozTools.
## This also adds an XML comment explaining the use of the <cache> element.
#def createCacheInConfig():
#    cacheCommentLine1 = "The cache is used to store temporary data for individual JMozTools utilities."
#    cacheCommentLine2 = "Any data in here is subject to removal at any time, without notice."
#    cacheCommentLine3 = "DO NOT PUT HAND-EDITED DATA IN THIS SECTION."
#    
#    document = getDocument()
#    mainElement = getMainElement()
#    commentElement1 = document.createComment(cacheCommentLine1)
#    commentElement2 = document.createComment(cacheCommentLine2)
#    commentElement3 = document.createComment(cacheCommentLine3)
#
#    cacheElement = document.createElement('Cache')
#    mainElement.appendChild(commentElement1)
#    mainElement.appendChild(commentElement2)
#    mainElement.appendChild(commentElement3)
#    mainElement.appendChild(cacheElement)
#    writeDocumentToConfigFile()
#    
#    return cacheElement
#
#def createCacheForUtility(aUtility):
#    global gPossibleUtilities
#    
#    if not aUtility in gPossibleUtilities:
#        raise StandardError("ERROR: " + aUtility + " not in list of approved JMozTools utilities. Refusing to create cache storage.")
#    
#    document = getDocument()
#    cacheElement = getCacheElement()
#    utilityElement = document.createElement(aUtility)
#    cacheElement.appendChild(utilityElement)
#    
#    writeDocumentToConfigFile()
#    
#    return utilityElement
#
#def createAliasInConfig(aliasName, projName, force=False):
#  if (doesAliasExist(aliasName)):
#    raise LookupError('Alias name "' + aliasName + '" already exists')
#
#  if (doesAliasExist(projName) and not force):
#    raise KeyError('Project "' + projName + "' exists, and is an alias to another project.")
#
#  aliasProj = findProject(aliasName)
#  if aliasProj:
#    raise LookupError('A project already exists named "' + aliasName + '"')
#
#  proj = findProject(projName)
#  if not proj:
#    raise LookupError('Project "' + projName + '" does not exist.')
#
#  document = getDocument()
#  mainElement = getMainElement()
#  aliasElement = document.createElement('Alias')
#  aliasElement.setAttribute('for', projName)
#  aliasElement.setAttribute('name', aliasName)
#
#  aliasesContainers = mainElement.getElementsByTagName('Aliases')
#  if len(aliasesContainers) == 0:
#    aliasesContainerElement = document.createElement('Aliases')
#    mainElement.appendChild(aliasesContainerElement)
#  else:
#    aliasesContainerElement = aliasesContainers[0]
#  aliasesContainerElement.appendChild(aliasElement)
#
#  writeDocumentToConfigFile()
#
#  return
#
#def createProjectInConfig(projName, srcDir, objDir, isAndroid='no'):
#    document = getDocument()
#    mainElement = getMainElement()
#    
#    projectElement = document.createElement('Project')
#    projectElement.setAttribute('name', projName)
#    projectElement.setAttribute('isMobile', isAndroid)
#    
#    srcDirElement = document.createElement('Directory')
#    srcDirElement.setAttribute('name', 'src')
#    
#    srcDirText = document.createTextNode(srcDir)
#    srcDirElement.appendChild(srcDirText)
#    projectElement.appendChild(srcDirElement)
#    
#    objDirElement = document.createElement('Directory')
#    objDirElement.setAttribute('name', 'obj')
#    
#    objDirText = document.createTextNode(objDir)
#    objDirElement.appendChild(objDirText)
#    projectElement.appendChild(objDirElement)
#    
#    mainElement.appendChild(projectElement)
#    
#    setLastProject(projName)
#    
#    writeDocumentToConfigFile()
#    
#    return
#
#def setDocumentGlobal(document):
#    global gDocument
#    gDocument = document
#    return
#
## ================== CONFIG FILE SECTION ==================
#        
#def createProject(projName, isAndroid='no'):
#    
#    srcDir = '';
#    while srcDir == '':
#        srcDir = promptForSourceDirectory(projName)
#    
#    objDir = '';
#    while objDir == '':
#        objDir = promptForObjectDirectory(projName)
#    
#    createProjectInConfig(projName, srcDir, objDir, isAndroid)
#
#    return
#
#    
#
#def promptForSourceDirectory(projName):
#    directory = "/home/" + JMozUtilities.getUserName() + "/Source/mozilla-" + projName + "/mozilla"
#    sys.stderr.write("Source directory for project '" + projName + "' [" + directory + "]: ")
#    effectiveDir = raw_input()
#    if effectiveDir == '' :
#        effectiveDir = directory
#    if not os.path.isdir(effectiveDir):
#        return ''
#    
#    return effectiveDir
#    
#def promptForObjectDirectory(projName):
#    directory = "/home/" + JMozUtilities.getUserName() + "/Source/mozilla-" + projName + "/obj"
#    sys.stderr.write("Object directory for project '" + projName + "' [" + directory + "]: ")
#    effectiveDir = raw_input()
#    if effectiveDir == '' :
#        effectiveDir = directory
#    if not os.path.isdir(effectiveDir):
#        return ''
#    
#    return effectiveDir
#
#def getListOfProjectNames():
#  allProjectNames = []
#  projectElements = getAllProjectElements()
#  for proj in projectElements:
#    allProjectNames.append(proj.getAttribute('name'))
#
#  return allProjectNames
#
#def promptCreateAlias(aliasName):
#  allProjects = getListOfProjectNames()
#  correct = False
#  while not correct:
#    print('Create "' + aliasName + '" as an alias to which of the following projects?')
#    for projName in allProjects:
#      print("\t(" + str(allProjects.index(projName)) + ") " + projName)
#    choice = int(raw_input("Project: "))
#    if choice >= len(allProjects):
#      correct = False
#      continue
#    projectName = allProjects[choice]
#    correctChoice = raw_input('Creating "' + aliasName + '" as an alias to "' + projName +'". Is this correct? [y/N] ')
#    print(correctChoice)
#    if correctChoice == 'y' or correctChoice == 'Y':
#      correct = True
#    else:
#      correct = False
#
#  try:
#    createAliasInConfig(aliasName, projectName)
#  except LookupError as e:
#    print("Error: " + e.message)
#  except KeyError:
#    projTarget = getAliasTarget(projectName)
#    choice = raw_input("Warning: '" + projectName + '" is an alias already. This will make "' + aliasName + '" an alias to "' + projTarget + '". Proceed? [y/N]')
#    if choice == 'y' or choice == 'Y':
#      createAliasInConfig(aliasName, projectName, True)
#
#def promptCreateProject(projName):
#    # We need to intercept SIGINT so that we don't fail unnecessarily with
#    # all kinds of weird errors.
#    try:
#        # Get required information
#        sys.stderr.write("Create new project '" + projName + "' [y/N]? ")
#        query = raw_input()
#        if not (query == 'y' or query == 'Y') :
#            sys.stderr.write("Project '" + projName + "' not created.\n")
#            raise IOError(1,"Unable to use project: " + projName)
#        
#        sys.stderr.write("Is this project a mobile project [y/N]? ")
#        isAndroid = 'n';
#        query = raw_input()
#        if (query == 'y' or query == 'Y'):
#            isAndroid = 'y';
#               
#        createProject(projName, isAndroid)
#        
#        sys.stderr.write("Project '" + projName + "' created.\n")
#    except KeyboardInterrupt:
#        # Let's clean up the already (possibly created) project in the XML
#        # file.
#        project = findProject(projName)
#        if project != '' :
#            # We need to clean it up, because it didn't exist before.
#            sys.stderr.write("Cleaning up configuration file...\n")
#            deleteProjectFromConfig(projName)
#        resetLastProjectToKnownGood()
#        writeDocumentToConfigFile()
#        sys.stderr.write("Exiting...\n")
#        sys.exit(0);
#        
#    return True
