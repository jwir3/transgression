#class Transgression:
from configurator.configurator import Configurator
import os.path

def main():
  # Check to make sure we have a config file, or create one
  config = Configurator(os.path.join('.transgression', 'config.xml'))
  config.addSectionToConfig('GlobalOptions')
  config.addSectionToConfig('Targets')
  config.addSectionToConfig('Targets')

  topLevelSections = config.getTopLevelSections()
  for section in topLevelSections:
    print(section)

if __name__ == '__main__':
  main()
