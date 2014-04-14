#TEST
from colors import *

# This is a class that allows us to print prettier output to the command line.
# It's designed so that you can create a single object of type PrettyLogger,
# then use that printer throughout your script.
class PrettyLogger:

  # These are colors that can be modified to better suit tastes when using this
  # class.
  INFO = '\033[92m'
  DEBUG = '\033[94m'
  WARNING = '\033[93m'
  ERROR = '\033[91m'
  ENDCOLOR = '\033[0m'

  def __init__(self, aEnableColor=False, aDebugEnabled=False, aVerboseEnabled=False):
    self.mColorEnabled = aEnableColor
    self.mDebugEnabled = aDebugEnabled
    self.mVerboseEnabled = aVerboseEnabled

  # Print debug output to the console, if debug output is enabled, or do
  # nothing. Most verbose.
  def debug(self, aMessage):
    self.printLogColor('debug', aMessage)

  # Print informative output to the console, if info output is enabled, or do
  # nothing. More verbose than warning output, but less than debug output.
  def info(self, aMessage):
    self.printLogColor('info', aMessage)

  # Print warning output to the console, if warning output is enabled, or do
  # nothing. More verbose than error output, but less than info output.
  def warn(self, aMessage):
    self.printLogColor('warn', aMessage)

  # Print error output to the console. Error output is always enabled, so this
  # will always print to the console. Least verbose output mechanism.
  def error(self, aMessage):
    self.printLogColor('error', aMessage)

  # Determine if color printing is enabled or disabled.
  #
  # @returns True, if color output is disabled for this PrettyLogger; False,
  #          otherwise.
  def isColorDisabled(self):
    return not self.mColorEnabled

  # Print log output without color to the console using this PrettyLogger object.
  #
  # @param aType The type of message to print - one of debug, info, warn, or
  #        error.
  # @param aMessage The string message to print. Each message is printed on a
  #        separate line.
  def printLogNoColor(self, aType, aMessage):
    if aType == 'warn':
        print ("WARNING: " + str(aMessage))
    elif aType == 'error':
        print ("ERROR: " + str(aMessage))
    elif aType == 'info':
        if self.mVerboseEnabled:
          print ("INFO: " + str(aMessage))
    elif aType == 'debug':
      if self.mDebugEnabled:
        print ("DEBUG: " + str(aMessage))
    else:
      # just print the message verbatim then, with no additions
      print(aMessage)

  # Print log output with color to the console using this PrettyLogger object.
  #
  # @param aType The type of message to print - one of debug, info, warn, or
  #        error.
  # @param aMessage The string message to print. Each message is printed on a
  #        separate line.
  def printLogColor(self, aType, aMessage):
    if self.isColorDisabled():
      self.printLogNoColor(aType, aMessage)
      return

    if aType == 'warn':
      print (yellow("WARNING: ") + str(aMessage))
    elif aType == 'error':
      print (red("ERROR: ") + str(aMessage))
    elif aType == 'info':
      if (self.mVerboseEnabled):
        print (green("INFO: ") + str(aMessage))
    else:
      # we assume that the type was 'debug' then
      if self.mDebugEnabled:
        print (blue("DEBUG: ") + str(aMessage))
