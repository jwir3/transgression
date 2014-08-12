#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime
import os
import httplib2
import platform
import re
import subprocess
import sys

from mozfile import rmtree
from mozprofile import FirefoxProfile
from mozprofile import ThunderbirdProfile
from mozrunner import Runner
from optparse import OptionParser
from ConfigParser import ConfigParser
from BeautifulSoup import BeautifulSoup

from mozInstall import MozInstaller
from utils import strsplit, download_url, get_date, get_platform

class DebugBuild(object):
    def __init__(self, repo_name=None, aBinaryNameConvention=None, aProcessNameConvention=None):
        self.mBinaryNameConvention = aBinaryNameConvention
        self.mProcessNameConvention = aProcessNameConvention
        self.mRepoName = aRepoName
        self.buildRegex = aBinaryNameConvention

        platform=get_platform()
        # if platform['name'] == "Windows":
        #     if platform['bits'] == '64':
        #         print "No debug builds available for 64 bit Windows"
        #         sys.exit()
        #     self.buildRegex = ".*win32.zip"
        #     self.processName = self.name + ".exe"
        #     self.binary = "transgressiondebugapp/" + self.name + "/" + self.name + ".exe"
        # elif platform['name'] == "Linux":
        #     self.processName = self.name + "-bin"
        #     self.binary = "transgressiondebugapp/" + self.name + "/" + self.name
        #     if platform['bits'] == '64':
        #         self.buildRegex = ".*linux-x86_64.tar.bz2"
        #     else:
        #         self.buildRegex = ".*linux-i686.tar.bz2"
        # if platform['name'] == "Mac":
        #     self.buildRegex = ".*mac.*\.dmg"
        #     self.processName = self.name + "-bin"
        #     # Firefox on Mac would have the following build regex:
        #     # Contents/Mozilla.app/MacOS/firefox-bin
        #     self.binary = "transgressiondebugapp/Contents/MacOS/" + self.name
        self.repo_name = repo_name
        self._monthlinks = {}
        self.lastdest = None

    def cleanup(self):
        rmtree('transgressiondebugapp')
        if self.lastdest:
            os.remove(self.lastdest)

    __del__ = cleanup

    # def download(self, date=datetime.date.today(), dest=None):
    #     url = self.getBuildUrl(date)
    #     if url:
    #         if not dest:
    #             dest = os.path.basename(url)
    #         print "Downloading nightly from %s" % date
    #         if self.lastdest:
    #             os.remove(self.lastdest)
    #         download_url(url, dest)
    #         self.dest = self.lastdest = dest
    #         return True
    #     else:
    #         return False
    #
    # def install(self):
    #     rmtree("moznightlyapp")
    #     subprocess._cleanup = lambda : None # mikeal's fix for subprocess threading bug
    #     MozInstaller(src=self.dest, dest="moznightlyapp", dest_app="Mozilla.app")
    #     return True
    #
    # @staticmethod
    # def urlLinks(url):
    #     res = [] # do not return a generator but an array, so we can store it for later use
    #
    #     h = httplib2.Http();
    #     resp, content = h.request(url, "GET")
    #     if resp.status != 200:
    #         return res
    #
    #     soup = BeautifulSoup(content)
    #     for link in soup.findAll('a'):
    #         res.append(link)
    #     return res

    def constructBuildUrlFromData(self, aBaseUrl, aYear, aMonth, aDay, aApplicationName=None, aBuildId=None):
      # What information do we need here?
      # Base site (Given, with formatString content)
      # Name of application (if not already given in above) - %name%
      # Month(%month%), Day(%day%), Year of Application Build (%year%)
      # Build Identifier String (%buildid%)
      constructedUrl = aBaseUrl.replace("%year%", aYear)
      constructedUrl = constructedUrl.replace("%day%", aDay)
      constructedUrl = constructedUrl.replace("%month%", aMonth)
      if aApplicationName:
        constructedUrl = constructedUrl.replace("%name%", aApplicationName)
      if aBuildId:
        constructedUrl = constructedUrl.replace("%buildid%", aBuildId)
      return constructedUrl

    def getBuildUrl(self, date, aBaseLocation):
        # url = "http://ftp.mozilla.org/pub/mozilla.org/" + self.appName + "/nightly/"
        url = aBaseLocation
        year = str(date.year)
        month = "%02d" % date.month
        day = "%02d" % date.day
        repo_name = self.repo_name or self.getRepoName(date)
        url += year + "/" + month + "/"

        linkRegex = '^' + year + '-' + month + '-' + day + '-' + '[\d-]+' + repo_name + '/$'
        cachekey = year + '-' + month
        if cachekey in self._monthlinks:
            monthlinks = self._monthlinks[cachekey]
        else:
            monthlinks = self.urlLinks(url)
            self._monthlinks[cachekey] = monthlinks

        # first parse monthly list to get correct directory
        for dirlink in monthlinks:
            dirhref = dirlink.get("href")
            if re.match(linkRegex, dirhref):
                # now parse the page for the correct build url
                for link in self.urlLinks(url + dirhref):
                    href = link.get("href")
                    if re.match(self.buildRegex, href):
                        return url + dirhref + href

        return False

    def getAppInfo(self):
        parser = ConfigParser()
        ini_file = os.path.join(os.path.dirname(self.binary), "application.ini")
        parser.read(ini_file)
        try:
            changeset = parser.get('App', 'SourceStamp')
            repo = parser.get('App', 'SourceRepository')
            return (repo, changeset)
        except:
            return ("", "")

    def start(self, profile, addons, cmdargs):
        if profile:
            profile = self.profileClass(profile=profile, addons=addons)
        elif len(addons):
            profile = self.profileClass(addons=addons)
        else:
            profile = self.profileClass()

        self.runner = Runner(binary=self.binary, cmdargs=cmdargs, profile=profile)
        self.runner.names = [self.processName]
        self.runner.start()
        return True

    def stop(self):
        self.runner.stop()

    def wait(self):
        self.runner.wait()

class Application(DebugBuild):
  # What each of the above specific versions provides is a way
  # to specify:
  # a) binary naming convention
  # b) process name/application naming convention

  def __init__(self, aRepoName=None, aBinaryNameConvention=None, aProcessNameConvention=None):
    DebugBuild.__init__(aRepoName, aNameConvention)

class ThunderbirdDebugBuild(DebugBuild):
    appName = 'thunderbird'
    name = 'thunderbird'
    profileClass = ThunderbirdProfile

    def getRepoName(self, date):
        # sneaking this in here
        if get_platform()['name'] == "Windows" and date < datetime.date(2010, 03, 18):
           # no .zip package for Windows, can't use the installer
           print "Can't run Windows builds before 2010-03-18"
           sys.exit()

        if date < datetime.date(2008, 7, 26):
            return "trunk"
        elif date < datetime.date(2009, 1, 9):
            return "comm-central"
        elif date < datetime.date(2010, 8, 21):
            return "comm-central-trunk"
        else:
            return "comm-central"


class FirefoxDebugBuild(DebugBuild):
    appName = 'firefox'
    name = 'firefox'
    profileClass = FirefoxProfile

    def getRepoName(self, date):
        if date < datetime.date(2008, 6, 17):
            return "trunk"
        else:
            return "mozilla-central"

class FennecDebugBuild(DebugBuild):
    appName = 'mobile'
    name = 'fennec'
    profileClass = FirefoxProfile

    def __init__(self, repo_name=None):
        DebugBuild.__init__(self, repo_name)
        self.buildRegex = 'fennec-.*\.apk'
        self.processName = 'org.mozilla.fennec'
        self.binary = 'org.mozilla.fennec/.App'
        if "y" != raw_input("WARNING: bisecting nightly fennec builds will clobber your existing nightly profile. Continue? (y or n)"):
            raise Exception("Aborting!")

    def getRepoName(self, date):
        return "mozilla-central-android"

    def install(self):
        subprocess.check_call(["adb", "uninstall", "org.mozilla.fennec"])
        subprocess.check_call(["adb", "install", self.dest])
        return True

    def start(self, profile, addons, cmdargs):
        subprocess.check_call(["adb", "shell", "am start -n %s" % self.binary])
        return True

    def stop(self):
        # TODO: kill fennec (don't really care though since uninstalling it kills it)
        # PID = $(adb shell ps | grep org.mozilla.fennec | awk '{ print $2 }')
        # adb shell run-as org.mozilla.fennec kill $PID
        return True

class TransgressionRunner(object):
    apps = {'thunderbird': ThunderbirdDebugBuild,
            'fennec': FennecDebugBuild,
            'firefox': FirefoxDebugBuild}

    def __init__(self, appname="firefox", repo_name=None, cmdargs=()):
        self.app = self.apps[appname](repo_name=repo_name)
        self.cmdargs = list(cmdargs)

    def install(self, date=datetime.date.today()):
        if not self.app.download(date=date):
            print "Could not find application from %s" % date
            return False # download failed
        print "Installing application"
        return self.app.install()

    def start(self, date=datetime.date.today()):
        if not self.install(date):
            return False
        print "Starting nightly"
        if not self.app.start(self.profile, self.addons, self.cmdargs):
            return False
        return True

    def stop(self):
        self.app.stop()

    def wait(self):
        self.app.wait()

    def cleanup(self):
        self.app.cleanup()

    def getAppInfo(self):
        return self.app.getAppInfo()

def cli(args=sys.argv[1:]):
    """transgression command line entry point"""

    # parse command line options
    parser = OptionParser()
    parser.add_option("-d", "--date", dest="date", help="date of the application",
                      metavar="YYYY-MM-DD", default=str(datetime.date.today()))
    # parser.add_option("-a", "--addons", dest="addons",
    #                   help="list of addons to install",
    #                   metavar="PATH1,PATH2")
    # parser.add_option("-p", "--profile", dest="profile", help="path to profile to user", metavar="PATH")
    # parser.add_option("-n", "--app", dest="app", help="application name",
    #                   type="choice",
    #                   metavar="[%s]" % "|".join(TransgressionRunner.apps.keys()),
    #                   choices=TransgressionRunner.apps.keys(),
    #                   default="firefox")
    parser.add_option("-r", "--repo", dest="repo_name", help="binary repository location",
                      metavar="[repo location]", default=None)
    options, args = parser.parse_args(args)
    # XXX https://github.com/mozilla/mozregression/issues/50
    addons = strsplit(options.addons or "", ",")

    # run application
    runner = TransgressionRunner(appname=options.app, repo_name=options.repo_name)
    runner.start(get_date(options.date))
    try:
        runner.wait()
    except KeyboardInterrupt:
        runner.stop()


if __name__ == "__main__":
    cli()
