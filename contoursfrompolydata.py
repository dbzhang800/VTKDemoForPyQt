#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
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
        self.ren.SetBackground(0.1, 0.2, 0.4)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 
        # Create source
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetThetaResolution(30)
        sphereSource.SetPhiResolution(15)
        sphereSource.Update()
        inputPolyData = sphereSource.GetOutput()

        inputMapper = vtk.vtkPolyDataMapper()
        inputMapper.SetInput(inputPolyData)

        # Create a plane to cut
        plane = vtk.vtkPlane()
        plane.SetOrigin(inputPolyData.GetCenter())
        plane.SetNormal(1, 1, 1)

        bound = inputPolyData.GetBounds()
        center = inputPolyData.GetCenter()

        distanceMin = math.sqrt((bound[0]-center[0])**2 + (bound[2]-center[1])**2 + (bound[4]-center[2])**2)
        distanceMax = math.sqrt((bound[1]-center[0])**2 + (bound[3]-center[1])**2 + (bound[5]-center[2])**2)

        # Create cutter
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInput(inputPolyData)
        cutter.GenerateValues(20, -distanceMin, distanceMax)
        cutterMapper = vtk.vtkPolyDataMapper()
        cutterMapper.SetInputConnection(cutter.GetOutputPort())
        cutterMapper.ScalarVisibilityOff()

        # Create plane actor
        planeActor = vtk.vtkActor()
        planeActor.GetProperty().SetColor(1.0, 1.0, 0)
        planeActor.GetProperty().SetLineWidth(3)
        planeActor.SetMapper(cutterMapper)

        # Create input actor
        inputActor = vtk.vtkActor()
        inputActor.GetProperty().SetColor(1.0, 0.8941, 0.7686)
        inputActor.SetMapper(inputMapper)
 
        self.ren.AddActor(planeActor)
        self.ren.AddActor(inputActor)
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

        self.setWindowTitle("Contours From Poly Data")

    def categories(self):
        return ['Cutter']

    def mainClasses(self):
        return ['vtkSphereSource', 'vtkPlane', 'vtkCutter']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
