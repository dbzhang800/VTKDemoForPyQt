#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
import sys
import os.path

from PyQt4 import QtCore, QtGui
QtCore.Signal = QtCore.pyqtSignal

import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class VTKFrame(QtGui.QFrame):
    def __init__(self, parent = None):
        super(VTKFrame, self).__init__(parent)

        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        vl = QtGui.QVBoxLayout(self)
        vl.addWidget(self.vtkWidget)
        vl.setContentsMargins(0, 0, 0, 0)
 
        # Create source
        source = vtk.vtkConeSource()
        source.SetHeight(3.0)
        source.SetRadius(1.0)
        source.SetResolution(20)
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
 
        self.ren1 = vtk.vtkRenderer()
        self.ren1.SetBackground(0.1, 0.2, 0.4)
        self.ren1.SetViewport(0.0, 0.0, 0.5, 1.0)
        self.ren1.AddActor(actor)

        self.ren2 = vtk.vtkRenderer()
        self.ren2.SetBackground(0.1, 0.2, 0.4)
        self.ren2.SetViewport(0.5, 0.0, 1.0, 1.0)
        self.ren2.AddActor(actor)

        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren1)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren2)
 
        self.ren1.ResetCamera()
        self.ren1.GetActiveCamera().Azimuth(90)

        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            self.startTimer(30)
            self._initialized = True

    def timerEvent(self, evt):
        self.ren1.GetActiveCamera().Azimuth(1)
        self.ren2.GetActiveCamera().Azimuth(1)
        self.vtkWidget.GetRenderWindow().Render()
 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Two render example")

    def categories(self):
        return ['Simple']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
