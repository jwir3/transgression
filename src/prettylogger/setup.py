from setuptools import setup
import os

setup(name='prettylogger',
      version='0.0.2',
      description='A logging utility package designed for command line use',
      author='Scott Johnson',
      author_email='jaywir3@gmail.com',
      url='http://github.com/jwir3/transgression',
      py_modules=['prettylogger.core'],
      install_requires=['argparse', 'ansicolors', 'httplib2', 'mozfile',
                        'mozprofile', 'mozrunner', 'BeautifulSoup', 'paramiko']
)
