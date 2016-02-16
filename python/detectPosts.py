#!/usr/bin/python
# coding:utf-8

import getopt, sys, logging, ConfigParser
from common import py_logging
from selenium import webdriver
from selenium.webdriver.support import expected_conditions

__logger__ = py_logging.getLogger("main")


class Config(object):
    def __init__(self):
        self.debug = False
        self.dryRun = False
        self.logFile = "./detectPosts.log"
        self.configFile = "./detectPosts.ini"
        self.chromeDriverPath = "./chromedriver.exe"
        self.phantomJsPath = "./phantomjs.exe"
        self.entryUrl = ""
        self.userIds = []
        self.postsXPath = ""
        self.username = ""
        self.password = ""

        self.__load()

    def __load(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "d", ["debug", "dry", "config=", "logfile="])
        except getopt.GetoptError as err:
            print str(err)  # will print something like "option -a not recognized"
            sys.exit(2)

        if opts:
            for opt, arg in opts:
                if opt in ("-d", "--debug"):
                    self.debug = True
                if opt == "--dry":
                    self.dryRun = True
                if opt == "--config":
                    self.configFile = arg
                if opt == "--logfile":
                    self.logFile = arg
                else:
                    pass

        config_parser = ConfigParser.ConfigParser()
        config_parser.read(self.configFile, )

        self.entryUrl = config_parser.get("global", "entryUrl")
        self.userIds = config_parser.get("global", "users").split(",")
        self.username = config_parser.get("admin", "username")
        self.password = config_parser.get("admin", "password")
        self.chromeDriverPath = config_parser.get("chromedriver", "path")
        self.postsXPath = config_parser.get("element-descriptors", "postsXPath")
        self.deleteLinkXPath = config_parser.get("element-descriptors", "deleteLinkXPath")

        self.unicodeUserIds = []
        for user in self.userIds:
            self.unicodeUserIds.append(unicode(user, "utf-8"))

        py_logging.configure(self.logFile, logToConsoleLevel=logging.DEBUG, logFileLevel=logging.INFO)
        __logger__.debug("Config file: %s", self.configFile)
        __logger__.info("Entry url is %s", self.entryUrl)
        __logger__.info("UserId is %s", self.userIds)

    def contains_user(self, __user__):
        return __user__ in self.unicodeUserIds


class DetectPosts:
    def __init__(self, config):
        self.config = config
        self.browser = self.create_browser()

    def create_browser(self):
        if self.config.debug:
            return webdriver.Chrome(config.chromeDriverPath)

        return webdriver.PhantomJS(config.phantomJsPath)

    def auto_sign_in(self):
        if self.config.dryRun:
            return

        __sign_in_form__ = self.browser.find_element_by_id("login_form")
        __user_text__ = __sign_in_form__.find_element_by_name("username")
        __pwd_text__ = __sign_in_form__.find_element_by_name("password")

        __user_text__.send_keys(self.config.username)
        __pwd_text__.send_keys(self.config.password)

        __sign_in_form__.find_element_by_name("submit").click()

    def shutdown(self):
        self.browser.quit()

    def start(self):
        self.browser.get(self.config.entryUrl)
        self.auto_sign_in()

        __hrefElements__ = self.browser.find_elements_by_xpath(self.config.postsXPath)
        __postElements__ = __hrefElements__[::2]
        __userElements__ = __hrefElements__[1::2]

        __postList__ = []
        for index in range(len(__postElements__)):
            __postElement__ = __postElements__[index]
            __userElement__ = __userElements__[index]
            if config.contains_user(__userElement__.text):
                __postList__.append({
                    'user': __userElement__.text,
                    'title': __postElement__.text,
                    'link': __postElement__.get_attribute("href")
                })

        for post in __postList__:
            self.delete_post(post)

    def delete_post(self, __post__):
        __user__ = __post__['user']
        __title__ = __post__['title']
        __link__ = __post__['link']
        __logger__.info("Found user '%s' post link '%s' title:  %s", __user__, __link__, __title__)
        self.browser.get(__link__)
        if self.config.dryRun:
            return
        try:
            __hrefElements__ = self.browser.find_elements_by_xpath(self.config.deleteLinkXPath)
            for hrefElement in __hrefElements__:
                hrefElement.click()
                if expected_conditions.alert_is_present():
                    alert = self.browser.switch_to.alert()
                    if self.config.dryRun:
                        alert.dismiss()
                    else:
                        alert.accept()
        except Exception as e:
            if self.config.debug:
                print e
            __logger__.error("Cannot find delete href at link: %s", __link__)


if __name__ == "__main__":
    config = Config()
    detectPost = DetectPosts(config)
    detectPost.start()
    detectPost.shutdown()
    py_logging.shutdown()


