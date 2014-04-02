#class Transgression:
from configurator.configurator import Configurator
import os.path

def promptUserForProgram():
  response = raw_input("transgression didn't find any binaries configured. Would you like to configure one now? ")
  if response.lower() == 'y':
    pass
  else:
    return

def main():
  # Check to make sure we have a config file, or create one
  config = Configurator(os.path.join('.transgression', 'config.xml'), aDebugOutput=True)

  # Configuration should include at least one binary
  try:
    section = config.getSectionByPath('Binaries')
  except:
    # We don't have any binaries listed, so perhaps we should prompt the user
    # for one?
    promptUserForProgram()

if __name__ == '__main__':
  main()
