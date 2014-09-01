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

        self.itemActivated.connect(self.onItemActived)

    def setCategoryDict(self, categoryDict):
        keys = categoryDict.keys()
        keys.sort()

        for key in keys:
            categoryItem = QtGui.QTreeWidgetItem(self, [key,], self.CATEGORY_ITEM)
            pages = categoryDict[key]
            pages.sort(key=lambda page:page.windowTitle())
            for page in pages:
                pageItem = QtGui.QTreeWidgetItem(categoryItem, [page.windowTitle(),], self.PAGE_ITEM)
                pageItem._page = page

    def onItemActived(self, item, column):
        if item.type() == self.PAGE_ITEM:
            self.pageItemActivated.emit(item._page)

class LineNumberArea(QtGui.QWidget):
    u"""Line Number Area for CodeEdit"""
    def __init__(self, parent=None):
        super(LineNumberArea, self).__init__(parent)
        
    def sizeHint(self):
        return QtCore.QSize(self.parent().lineNumberAreaWidth(), 0)
        
    def paintEvent(self, event):
        self.parent().lineNumberAreaPaintEvent(event)
        
class CodeEdit(QtGui.QPlainTextEdit):
    u"""PlainTextEdit with LineNumber"""
    def __init__(self, parent=None):
        super(CodeEdit, self).__init__(parent)
        self.lineNumberArea = LineNumberArea(self)
        self.setLineWrapMode(self.NoWrap)
        
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

        #Set proper selection color
        p = self.palette();
        p.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight
                , p.color(QtGui.QPalette.Normal, QtGui.QPalette.Highlight))
        p.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.HighlightedText
                , p.color(QtGui.QPalette.Normal, QtGui.QPalette.HighlightedText))
        self.setPalette(p);
        
    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QtCore.Qt.lightGray)
        
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = "{}".format(blockNumber+1)
                painter.setPen(QtCore.Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(), 
                                 QtCore.Qt.AlignRight, number)
                                 
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
        
    def lineNumberAreaWidth(self):
        if self.lineNumberArea.isHidden():
            return 0
            
        digits = 1
        m = max(1, self.blockCount())
        while (m >= 10):
            m /= 10
            digits += 1
            
        space = 3 + self.fontMetrics().width('9') * digits

        return space
        
    def resizeEvent(self, event):
        super(CodeEdit, self).resizeEvent(event)
        
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
        
    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
        
    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QtGui.QTextEdit.ExtraSelection()
            lineColor = QtGui.QColor(QtCore.Qt.lightGray).lighter(120)
            
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
            
        self.setExtraSelections(extraSelections)
        
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
            
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

class PythonHighlighter(QtGui.QSyntaxHighlighter):
    u"""A simple hightlighter for python source code"""
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)
        self.highlightRules = []

        self._setupKeyWorksPattern()
        self._setupCommentsPattern()

    def _setupKeyWorksPattern(self):
        keywords = ['and', 'del', 'from', 'not', 'while', 'as', 'elif', 'global', 'or', 
                'with', 'assert', 'else', 'if', 'pass', 'yield', 'break', 'except',
                'import', 'print' , 'class', 'exec', 'in', 'raise' , 'continue',
                'finally', 'is', 'return' , 'def', 'for', 'lambda', 'try']
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.darkRed)
        keywordFormat.setFontWeight(QtGui.QFont.Bold)
        for keyword in keywords:
            re_pattern = QtCore.QRegExp(r'\b{}\b'.format(keyword))
            self.highlightRules.append((re_pattern, keywordFormat))
        
    def _setupCommentsPattern(self):
        commentsFormat = QtGui.QTextCharFormat()
        commentsFormat.setForeground(QtCore.Qt.blue)

        self.highlightRules.append((QtCore.QRegExp("#[^\n]*"), commentsFormat))
                
    def highlightBlock(self, text):
        for pattern, format in self.highlightRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("VTK Demo for PyQt4")
        self.setCorner(QtCore.Qt.BottomLeftCorner, QtCore.Qt.LeftDockWidgetArea)
        self.setCentralWidget(QtGui.QStackedWidget(self))

        self._textView = CodeEdit()
        self._textView.setReadOnly(True)
        self._pythonHighlighter = PythonHighlighter(self._textView.document())

        dockWidget = QtGui.QDockWidget("Source code")
        dockWidget.setWidget(self._textView)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dockWidget)

        self._pageTreeWidget = PageTreeWidget()
        dockWidget = QtGui.QDockWidget("Examples")
        dockWidget.setWidget(self._pageTreeWidget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockWidget)

        self._pageTreeWidget.pageItemActivated.connect(self.onPageItemActivated)
        self.loadPages()

    def loadPages(self):
        with file('pluginslist') as f:
            lines = f.read().splitlines()

        categoryDict = {}
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
                page._filePath = line+'.py'

                try:
                    categories = page.categories()
                except:
                    categories = ['Ungrouped']

                for category in categories:
                    try:
                        pages = categoryDict[category]
                    except KeyError:
                        pages = []
                        categoryDict[category] = pages
                    pages.append(page)

        self._pageTreeWidget.setCategoryDict(categoryDict)

        self._currentPage = None
        self.onPageItemActivated(self.centralWidget().currentWidget())

    def onPageItemActivated(self, page):
        if page != self._currentPage:
            self.centralWidget().setCurrentWidget(page)
            self.showSourceFile(page._filePath)
            self.setWindowTitle(u"VTK Demo for PyQt4 - {}".format(page._filePath))

    def showSourceFile(self, filePath):
        try:
            with file(filePath) as f:
                contents = f.read()
        except IOError:
            self._textView.setPlainText(u"Can not open file {}".format(filePath))
            return

        try:
            contents = contents.decode('utf8')
        except UnicodeDecodeError:
            contents = contents.decode('latin1')

        self._textView.setPlainText(contents)

if __name__ == '__main__':
    import vtk
    fileOutputWindow = vtk.vtkFileOutputWindow()
    fileOutputWindow.SetFileName('vtk-PyQt4.log')
    vtk.vtkOutputWindow.SetInstance(fileOutputWindow)

    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
