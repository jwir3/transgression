from setuptools import setup
import os

progName = 'transgression'
progVersion = '0.0.2'
progDescription='Generic binary regression finding utility based off of mozregression'
progAuthor = 'Scott Johnson'
progEmail = 'jaywir3@gmail.com'
progUrl = 'http://github.com/jwir3/transgression'
entry_points = { 'console_scripts': [
  'transgression = transgression.transgression:main',
]}

setup(name=progName,
      version=progVersion,
      description=progDescription,
      author=progAuthor,
      author_email=progEmail,
      url=progUrl,
      packages=['transgression', 'configurator'],
      entry_points=entry_points,
      install_requires=['argparse', 'ansicolors', 'httplib2', 'mozfile',
                        'mozprofile', 'mozrunner', 'BeautifulSoup']
)
