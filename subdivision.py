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
        sphereSource = vtk.vtkSphereSource()
        sphereSource.Update()
        originalMesh = sphereSource.GetOutput()

        numberOfViewports = 3
        self.vtkWidget.GetRenderWindow().SetSize(200*numberOfViewports, 200)

        numberOfSubdivisions = 2
        for i in range(numberOfViewports):
            if i == 0:
                subdivisionFilter = vtk.vtkLinearSubdivisionFilter()
            elif i == 1:
                subdivisionFilter = vtk.vtkLoopSubdivisionFilter()
            else:
                subdivisionFilter = vtk.vtkButterflySubdivisionFilter()

            subdivisionFilter.SetNumberOfSubdivisions(numberOfSubdivisions)
            subdivisionFilter.SetInputConnection(originalMesh.GetProducerPort())
            subdivisionFilter.Update()

            renderer = vtk.vtkRenderer()
            self.vtkWidget.GetRenderWindow().AddRenderer(renderer)
            renderer.SetViewport(float(i)/numberOfViewports, 0, (i+1.0)/numberOfViewports, 1)

            # Create a mapper and actor
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(subdivisionFilter.GetOutputPort())
 
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            renderer.AddActor(actor)
            renderer.ResetCamera()
 
        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            self._initialized = True
 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Simple VTK example")

    def categories(self):
        return ['Simple']

    def mainClasses(self):
        return ['vtkConeSource']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
