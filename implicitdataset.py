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
         
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(1, 1, 1)
        sphere.SetRadius(1)
        sphere.SetThetaResolution(100)
        sphere.SetPhiResolution(100)
        sphere.Update()
         
        cube = vtk.vtkCubeSource()
        cube.SetBounds(-1,1,-1,1,-1,1)
        cube.Update()
         
        # Create 3D cells so vtkImplicitDataSet evaluates inside vs outside correctly
        tri = vtk.vtkDelaunay3D()
        tri.SetInput(cube.GetOutput())
        tri.BoundingTriangulationOff()
         
        # vtkImplicitDataSet needs some scalars to interpolate to find inside/outside
        elev = vtk.vtkElevationFilter()
        elev.SetInputConnection(tri.GetOutputPort())
         
        implicit = vtk.vtkImplicitDataSet()
        implicit.SetDataSet(elev.GetOutput())
         
        clipper = vtk.vtkClipPolyData()
        clipper.SetClipFunction(implicit)
        clipper.SetInputConnection(sphere.GetOutputPort())
        clipper.InsideOutOn()
        clipper.Update()
         
        # Vis for clipped sphere
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(clipper.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
         
        # Vis for cube so can see it in relation to clipped sphere
        mapper2 = vtk.vtkDataSetMapper()
        mapper2.SetInputConnection(elev.GetOutputPort())
        actor2 = vtk.vtkActor()
        actor2.SetMapper(mapper2)
        #actor2.GetProperty().SetRepresentationToWireframe()
         
        #create renderers and add actors of plane and cube
        self.ren.AddActor(actor)
        self.ren.AddActor(actor2)
        self.ren.SetBackground(0.1, 0.2, 0.4)

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

        self.setWindowTitle("Implicit data set example")

    def categories(self):
        return ['Clipper', 'Implict Data Set']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
