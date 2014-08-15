#!/usr/bin/env python
# -*- coding: UTF-8 -*-

u"""
VTK demo for PyQt4

Copyright (C) 2014 Debao Zhang <hello@debao.me>
All rights reserved.
"""

import sys
import os.path
import importlib
import weakref

from PyQt4 import QtCore, QtGui
QtCore.Signal = QtCore.pyqtSignal

class PageTreeWidget(QtGui.QTreeWidget):
    CATEGORY_ITEM = 1
    PAGE_ITEM = 2

    pageItemActivated = QtCore.Signal(object)

    def __init__(self, parent = None):
        super(PageTreeWidget, self).__init__(parent)
        self.header().hide()
        self._categoryDict = {}

        self.itemActivated.connect(self.onItemActived)

    def addPage(self, page):
        pageName = page.windowTitle()
        try:
            categories = page.categories()
        except:
            categories = ['Ungrouped']

        for category in categories:
            try:
                categoryItem = self._categoryDict[category]
            except KeyError:
                categoryItem = QtGui.QTreeWidgetItem(self, [category,], self.CATEGORY_ITEM)
                self._categoryDict[category] = categoryItem

            pageItem = QtGui.QTreeWidgetItem(categoryItem, [pageName,], self.PAGE_ITEM)
            pageItem._page = page

    def onItemActived(self, item, column):
        if item.type() == self.PAGE_ITEM:
            self.pageItemActivated.emit(item._page)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("VTK Demo for PyQt4")
        self.setCentralWidget(QtGui.QStackedWidget(self))

        self._pageTreeWidget = PageTreeWidget()
        dockWidget = QtGui.QDockWidget()
        dockWidget.setWidget(self._pageTreeWidget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockWidget)

        self.loadPages()

        self._pageTreeWidget.pageItemActivated.connect(self.onPageItemActivated)

    def loadPages(self):
        with file('pluginslist') as f:
            lines = f.read().splitlines()

        for line in lines:
            line = line.strip()
            if line and not line.startswith(('#', '//')):
                try:
                    m = importlib.import_module(line)
                except ImportError:
                    continue
                page = m.MainPage()
                if not page.windowTitle():
                    page.setWindowTitle(line)
                self.centralWidget().addWidget(page)
                self._pageTreeWidget.addPage(page)

    def onPageItemActivated(self, page):
        self.centralWidget().setCurrentWidget(page)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
