#class Transgression:
from configurator.configurator import Configurator
import os.path

def main():
  # Check to make sure we have a config file, or create one
  config = Configurator(os.path.join('.transgression', 'config.xml'))
  config.addSectionToConfig('GlobalOptions')
  config.addSectionToConfig('Targets')
  config.addSectionToConfig('Targets')

  globalOptionsSection = config.getTopLevelSection('GlobalOptions')
  globalOptionsSection.setOption('debug', 'on')
  globalOptionsSection.setOption('debug', 'off')

if __name__ == '__main__':
  main()
