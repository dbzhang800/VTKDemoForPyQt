#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
import sys
import os.path
import importlib

from PyQt4 import QtCore, QtGui
QtCore.Signal = QtCore.pyqtSignal

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        centralWidget = QtGui.QTabWidget(self)
        self.setCentralWidget(centralWidget)

        self.loadPages()

    def loadPages(self):
        with file('pluginslist') as f:
            lines = f.read().splitlines()

        for line in lines:
            line = line.strip()
            if line:
                try:
                    m = importlib.import_module(line)
                except ImportError:
                    continue
                page = m.MainPage()
                self.centralWidget().addTab(page, line)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
