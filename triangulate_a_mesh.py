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
        vl = QtGui.QVBoxLayout(self)
        vl.addWidget(self.vtkWidget)
        vl.setContentsMargins(0, 0, 0, 0)
 
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 
        # Create source
        polygonSource = vtk.vtkRegularPolygonSource()
        polygonSource.Update()

        triangleFilter = vtk.vtkTriangleFilter()
        triangleFilter.SetInputConnection(polygonSource.GetOutputPort())
        triangleFilter.Update()

        inputMapper = vtk.vtkPolyDataMapper()
        inputMapper.SetInputConnection(polygonSource.GetOutputPort())
        inputActor = vtk.vtkActor()
        inputActor.SetMapper(inputMapper)
        inputActor.GetProperty().SetRepresentationToWireframe()

        triangleMapper = vtk.vtkPolyDataMapper()
        triangleMapper.SetInputConnection(triangleFilter.GetOutputPort())
        triangleActor = vtk.vtkActor()
        triangleActor.SetMapper(triangleMapper)
        triangleActor.GetProperty().SetRepresentationToWireframe()
 
        # Setup renderers
        leftRenderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(leftRenderer)
        leftRenderer.SetViewport(0, 0, 0.5, 1)
        leftRenderer.SetBackground(0.6, 0.5, 0.4)
        leftRenderer.AddActor(inputActor)

        rightRenderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(rightRenderer)
        rightRenderer.SetViewport(0.5, 0, 1, 1)
        rightRenderer.SetBackground(0.4, 0.5, 0.6)
        rightRenderer.AddActor(triangleActor)

        leftRenderer.ResetCamera()
        rightRenderer.ResetCamera()

        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            self._initialized = True

 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Triangulate mesh example")

    def categories(self):
        return ['Simple']

    def mainClasses(self):
        return ['vtkTriangleFilter', 'vtkRegularPolygonSource']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
