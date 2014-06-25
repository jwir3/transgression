from setuptools import setup
import os

setup(name='configurator',
      version='0.0.1',
      description='Configuration utility designed to simplify XML configuration',
      author='Scott Johnson',
      author_email='jaywir3@gmail.com',
      url='http://github.com/jwir3/transgression',
      py_modules=['configurator.core'],
      install_requires=['argparse', 'ansicolors', 'httplib2', 'mozfile',
                        'mozprofile', 'mozrunner', 'BeautifulSoup', 'paramiko',
                        'prettylogger']
)
