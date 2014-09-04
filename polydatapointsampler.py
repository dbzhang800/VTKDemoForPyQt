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
 
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.1, 0.2, 0.4)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 
        # Create source
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetPhiResolution(50)
        sphereSource.SetThetaResolution(50)
        sphereSource.Update()

        # Sample the sphere
        pointSampler = vtk.vtkPolyDataPointSampler()
        pointSampler.SetDistance(0.01)
        pointSampler.SetInputConnection(sphereSource.GetOutputPort())
        pointSampler.Update()

        # Visualize
        sphereMapper = vtk.vtkPolyDataMapper()
        sphereMapper.SetInputConnection(sphereSource.GetOutputPort())

        sphereActor = vtk.vtkActor()
        sphereActor.SetMapper(sphereMapper)
        
        sampleMapper = vtk.vtkPolyDataMapper()
        sampleMapper.SetInputConnection(pointSampler.GetOutputPort())

        sampleActor = vtk.vtkActor()
        sampleActor.SetMapper(sampleMapper)
        sampleActor.GetProperty().SetColor(1, 0, 0)
 
        self.ren.AddActor(sphereActor)
        self.ren.AddActor(sampleActor)
        self.ren.ResetCamera()

        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            self.startTimer(30)
            self._initialized = True

    def timerEvent(self, evt):
        self.ren.GetActiveCamera().Azimuth(1)
        self.vtkWidget.GetRenderWindow().Render()
 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Polydata Point Sampler example")

    def categories(self):
        return ['Simple']

    def mainClasses(self):
        return ['vtkPolyDataPointSampler']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
