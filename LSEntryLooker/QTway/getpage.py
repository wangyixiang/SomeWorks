#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *

import crawlerConfig

wrong_message = [r"Error loading player"]

SITE_TV_COUNTRY_THAILAND = r"%s/tv/country/Thailand" % crawlerConfig.site_address
STCT_RESULTS_SUMMARY = r"results-summary"
STCT_RESULTS_SUMMARY_PATTERN = r"(\d+).*TV Stations"
STCT_ITEMS_LIST = r"items-list"
STCT_ITEM = r"item"
STCT_ITEM_NAME = r"item-name"
STCT_ITEM_DATA_URL = "data-url"
STCT_ITEM_DATA_ROLE = "data-role"
STCT_ITEM_PLAYER_POPUP = r"player-popup"
STCT_ITEM_PLAYER_PROFILE = r"player-profile"
STCT_ITEM_PLAYER_CLASS = r"tv-profile-player"
STCT_ITEM_JW_PLAYER_ID = r"jw-player"
STCT_ITEM_FETCHING_TIMEOUT = r"fetching-timeout"


class PageRender(QWebPage):
    def __init__(self, url):
        self.app = QApplication(sys.argv)
        QWebPage.__init__(self)
        self.loadFinished.connect(self._load_finished)
        self.mainFrame().load(QUrl(url))
        self.app.exec_()

    def _load_finished(self, result):
        self.result = result
        self.frame = self.mainFrame()
        self.app.quit()

    def get_html_result(self):
        if self.result:
            return str(self.frame.toHtml().toAscii())
        return None
