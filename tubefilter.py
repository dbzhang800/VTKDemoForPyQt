#!/usr/bin/env python
# -*- coding: UTF-8 -*-

u'''
This example creates a tube around a line.
This is helpful because when you zoom the camera,
the thickness of the a line remains constant,
while the thickness of a tube varies.
'''

import sys
import os.path
import math

from PyQt4 import QtCore, QtGui
QtCore.Signal = QtCore.pyqtSignal

import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class VTKFrame(QtGui.QFrame):
    def __init__(self, parent = None):
        super(VTKFrame, self).__init__(parent)

        self.vtkWidget = QVTKRenderWindowInteractor(self)
        vl = QtGui.QVBoxLayout(self)
        vl.addWidget(self.vtkWidget)
        vl.setContentsMargins(0, 0, 0, 0)
 
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.2, 0.3, 0.4)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 
        # Create a line
        lineSource = vtk.vtkLineSource()
        lineSource.SetPoint1(1, 0, 0)
        lineSource.SetPoint2(0, 1, 0)

        # Create a mapper and actor
        lineMapper = vtk.vtkPolyDataMapper()
        lineMapper.SetInputConnection(lineSource.GetOutputPort())
        lineActor = vtk.vtkActor()
        lineActor.GetProperty().SetColor(0, 0, 0.1)
        lineActor.SetMapper(lineMapper)

        #Create a tube around the line
        tubeFilter = vtk.vtkTubeFilter()
        tubeFilter.SetInputConnection(lineSource.GetOutputPort())
        tubeFilter.SetRadius(0.025) #Default is 0.5
        tubeFilter.SetNumberOfSides(50)
        tubeFilter.Update()
 
        # Create a mapper
        tubeMapper = vtk.vtkPolyDataMapper()
        tubeMapper.SetInputConnection(tubeFilter.GetOutputPort())
 
        # Create an actor
        tubeActor = vtk.vtkActor()
        tubeActor.SetMapper(tubeMapper)
 
        self.ren.AddActor(tubeActor)
        self.ren.AddActor(lineActor)
        self.ren.ResetCamera()

        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            #self.startTimer(30)
            self._initialized = True

    def timerEvent(self, evt):
        self.ren.GetActiveCamera().Azimuth(1)
        self.vtkWidget.GetRenderWindow().Render()
 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Tube Filter example")

    def categories(self):
        return ['Simple', 'Tube']

    def mainClasses(self):
        return ['vtkLineSource', 'vtkTubeFilter']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
