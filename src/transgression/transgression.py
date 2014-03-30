#class Transgression:
from configurator.configurator import Configurator
import os.path

def main():
  # Check to make sure we have a config file, or create one
  gConfig = Configurator(os.path.join('.transgression', 'config.xml'))

if __name__ == '__main__':
  main()
