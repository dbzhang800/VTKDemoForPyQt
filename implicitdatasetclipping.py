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
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
         
        resolution = 10
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(0.75, 0, 0)
        sphere.SetThetaResolution(resolution)
        sphere.SetPhiResolution(resolution)
        sphere.Update()

        # Add ids to the points and cells of the sphere
        cellIdFilter = vtk.vtkIdFilter()
        cellIdFilter.SetInputConnection(sphere.GetOutputPort())
        cellIdFilter.SetCellIds(True)
        cellIdFilter.SetPointIds(False)
        cellIdFilter.SetIdsArrayName("CellIds")
        cellIdFilter.Update()

        pointIdFilter = vtk.vtkIdFilter()
        pointIdFilter.SetInputConnection(cellIdFilter.GetOutputPort())
        pointIdFilter.SetCellIds(False)
        pointIdFilter.SetPointIds(True)
        pointIdFilter.SetIdsArrayName("PointIds")
        pointIdFilter.Update()

        sphereWithIds = pointIdFilter.GetOutput()
         
        cube = vtk.vtkCubeSource()
        cube.Update()

        implicitCube = vtk.vtkBox()
        implicitCube.SetBounds(cube.GetOutput().GetBounds())

        clipper = vtk.vtkClipPolyData()
        clipper.SetClipFunction(implicitCube)
        clipper.SetInput(sphereWithIds)
        clipper.InsideOutOn()
        clipper.Update()
         
        # Create a mapper and actor for clipped sphere
        clippedMapper = vtk.vtkPolyDataMapper()
        clippedMapper.SetInputConnection(clipper.GetOutputPort())
        clippedMapper.ScalarVisibilityOff()
        clippedActor = vtk.vtkActor()
        clippedActor.SetMapper(clippedMapper)
        clippedActor.GetProperty().SetRepresentationToWireframe()

        # Create a mapper and actor for the cube
        cubeMapper = vtk.vtkPolyDataMapper()
        cubeMapper.SetInputConnection(cube.GetOutputPort())
        cubeActor = vtk.vtkActor()
        cubeActor.SetMapper(cubeMapper)
        cubeActor.GetProperty().SetRepresentationToWireframe()
        cubeActor.GetProperty().SetOpacity(0.5)
         
        #create renderers and add actors of plane and cube
        self.ren.AddActor(clippedActor)
        self.ren.AddActor(cubeActor)
        self.ren.SetBackground(0.2, 0.3, 0.4)

        self.ren.ResetCamera()
        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            self._initialized = True
 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Implicit dataset clipping example")

    def categories(self):
        return ['Clipper', 'Implict Data Set', 'Filters']

    def mainClasses(self):
        return ['vtkSphereSource', 'vtkIdFilter', 'vtkBox', 'vtkClipPolyData']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
