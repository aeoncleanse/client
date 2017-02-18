from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.QtCore import Qt

import webbrowser
import util
import client
import re
from .newsitem import NewsItem, NewsItemDelegate
from .newsmanager import NewsManager

import base64

import logging

logger = logging.getLogger(__name__)

class Hider(QtCore.QObject):
    """
    Hides a widget by blocking its paint event. This is useful if a
    widget is in a layout that you do not want to change when the
    widget is hidden.
    """
    def __init__(self, parent=None):
        super(Hider, self).__init__(parent)

    def eventFilter(self, obj, ev):
        return ev.type() == QtCore.QEvent.Paint

    def hide(self, widget):
        widget.installEventFilter(self)
        widget.update()

    def unhide(self, widget):
        widget.removeEventFilter(self)
        widget.update()

    def hideWidget(self, sender):
        if sender.isWidgetType():
            self.hide(sender)

FormClass, BaseClass = util.loadUiType("news/news.ui")

class NewsWidget(FormClass, BaseClass):
    CSS = """
    img { display: block; max-width: 100%; height: auto !important; }
    body {
        font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 15px;
        line-height: 1.4;
        color: #222222;
        padding-top: 20px;
    }
    h1 {
        font-family: 'Yanone Kaffeesatz', sans-serif;
        font-size: 50px;
        text-align: center;
        margin-bottom: 20px;
        margin-top: 0px;
    }
    hr {
        display: block;
        margin-top: -10px;
        margin-bottom: 20px;
        margin-left: auto;
        margin-right: auto;
        border-style: solid;
        border-width: 3px;
    }
    """

    HTML = u"""
    <head>
    <link href="https://fonts.googleapis.com/css?family=Yanone+Kaffeesatz" rel="stylesheet" type="text/css">
    </head>
    <body>
    <h1>{title}</h1>
    <hr>
    <div id="container">
    {content}
    </div>
    </body>
    """

    def __init__(self, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)

        self.setupUi(self)

        client.instance.whatNewTab.layout().addWidget(self)

        self.newsManager = NewsManager(self)

        self.newsWebView.settings().setUserStyleSheetUrl(QtCore.QUrl(
                'data:text/css;charset=utf-8;base64,' + base64.b64encode(self.CSS)
            ))
        # open all links in external browser
        self.newsWebView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.newsWebView.page().linkClicked.connect(self.linkClicked)

        # hide webview until loaded to avoid FOUC
        self.hider = Hider()
        self.hider.hide(self.newsWebView)
        self.newsWebView.loadFinished.connect(self.loadFinished)

        self.newsList.setIconSize(QtCore.QSize(0,0))
        self.newsList.setItemDelegate(NewsItemDelegate(self))
        self.newsList.currentItemChanged.connect(self.itemChanged)

    def addNews(self, newsPost):
        newsItem = NewsItem(newsPost, self.newsList)

    def itemChanged(self, current, previous):
        self.newsWebView.setHtml(self.HTML.format(
            title = current.newsPost['title'],
            content = current.newsPost['body'],
        ))

    def linkClicked(self, url):
        webbrowser.open(url.toString())

    def loadFinished(self, ok):
        self.hider.unhide(self.newsWebView)
        self.newsWebView.loadFinished.disconnect(self.loadFinished)
