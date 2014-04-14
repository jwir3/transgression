from setuptools import setup, find_packages
import os

setup(name='prettylogger',
      version='0.0.1',
      description='A logging utility package designed for command line use',
      author='Scott Johnson',
      author_email='jaywir3@gmail.com',
      url='http://github.com/jwir3/transgression',
      packages=['prettylogger'],
      install_requires=['argparse', 'ansicolors', 'httplib2', 'mozfile',
                        'mozprofile', 'mozrunner', 'BeautifulSoup', 'paramiko']
)

setup(name='configurator',
      version='0.0.1',
      description='Configuration utility designed to simplify XML configuration',
      author='Scott Johnson',
      author_email='jaywir3@gmail.com',
      url='http://github.com/jwir3/transgression',
      packages=['configurator'],
      install_requires=['argparse', 'ansicolors', 'httplib2', 'mozfile',
                        'mozprofile', 'mozrunner', 'BeautifulSoup', 'paramiko',
                        'prettylogger']
)

setup(name='transgression',
      version='0.0.1',
      description='Generic binary regression finding utility based off of mozregression',
      author='Scott Johnson',
      author_email='jaywir3@gmail.com',
      url='http://github.com/jwir3/transgression',
      packages=['transgression'],
      entry_points={ 'console_scripts': [
        'transgression = transgression.transgression:main'] },
      install_requires=['argparse', 'ansicolors', 'httplib2', 'mozfile',
                        'mozprofile', 'mozrunner', 'BeautifulSoup', 'paramiko',
                        'configurator', 'prettylogger']
)
