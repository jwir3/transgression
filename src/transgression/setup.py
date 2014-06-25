from setuptools import setup
import os

setup(name='transgression',
      version='0.0.1',
      description='Generic binary regression finding utility based off of mozregression',
      author='Scott Johnson',
      author_email='jaywir3@gmail.com',
      url='http://github.com/jwir3/transgression',
      packages=['transgression'],
      entry_points={ 'console_scripts': [
        'transgression = transgression.core:main'] },
      install_requires=['argparse', 'ansicolors', 'httplib2', 'mozfile',
                        'mozprofile', 'mozrunner', 'BeautifulSoup', 'paramiko',
                        'configurator', 'prettylogger']
)
