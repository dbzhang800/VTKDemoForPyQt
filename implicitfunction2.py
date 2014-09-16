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
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # Construct a Cylinder from (x1, y1, z1) to (x2, y2, z2), the inner and outer radius r1, r2
        x1, y1, z1 = 10, 2, 3
        x2, y2, z2 = 10, 20, 30
        r1, r2 = 3, 8

        dx, dy, dz = x2-x1, y2-y1, z2-z1

        # create axis object
        axisSource = vtk.vtkLineSource()
        axisSource = vtk.vtkLineSource()
        axisSource.SetPoint1(x1, y1, z1)
        axisSource.SetPoint2(x2, y2, z2)
        axisMapper = vtk.vtkPolyDataMapper()
        axisMapper.SetInputConnection(axisSource.GetOutputPort())
        axisActor = vtk.vtkActor()
        axisActor.GetProperty().SetColor(0, 0, 1)
        axisActor.SetMapper(axisMapper)
        self.ren.AddActor(axisActor)

        # Create planes
        plane1 = vtk.vtkPlane()
        plane1.SetOrigin(x1, y1, z1)
        plane1.SetNormal(-dx, -dy, -dz)

        plane2 = vtk.vtkPlane()
        plane2.SetOrigin(x2, y2, z2)
        plane2.SetNormal(dx, dy, dz)
 
        # Create cylinders
        out_cylinder = vtk.vtkCylinder()
        out_cylinder.SetCenter(0, 0, 0)
        out_cylinder.SetRadius(r2)

        in_cylinder = vtk.vtkCylinder()
        in_cylinder.SetCenter(0, 0, 0)
        in_cylinder.SetRadius(r1)

        # The rotation axis of cylinder is along the y-axis
        # What we need is the axis (x2-x1, y2-y1, z2-z1)
        angle = math.acos(dy/math.sqrt(dx**2 + dy**2 + dz**2)) * 180.0 / math.pi
        transform = vtk.vtkTransform()
        transform.RotateWXYZ(-angle, dz, 1, -dx)
        transform.Translate(-x1, -y1, -z1)

        out_cylinder.SetTransform(transform)
        in_cylinder.SetTransform(transform)

        # Cutted object
        cuted = vtk.vtkImplicitBoolean()
        cuted.SetOperationTypeToIntersection()
        cuted.AddFunction(out_cylinder)
        cuted.AddFunction(plane1)
        cuted.AddFunction(plane2)

        cuted2 = vtk.vtkImplicitBoolean()
        cuted2.SetOperationTypeToDifference()
        cuted2.AddFunction(cuted)
        cuted2.AddFunction(in_cylinder)

        # Sample 
        sample = vtk.vtkSampleFunction()
        sample.SetImplicitFunction(cuted2)
        sample.SetModelBounds(-100 , 100 , -100 , 100 , -100 , 100)
        sample.SetSampleDimensions(300, 300, 300)
        sample.SetComputeNormals(0)

        # Filter
        surface = vtk.vtkContourFilter()
        surface.SetInputConnection(sample.GetOutputPort())
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(surface.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
 
        self.ren.AddActor(actor)
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

        self.setWindowTitle("Implicitfunction Example")

    def categories(self):
        return ['Demo', 'Implicit Function', 'Filters']

    def mainClasses(self):
        return ['vtkCylinder', 'vtkPlane', 'vtkImplicitBoolean', 'vtkSampleFunction', 'vtkContourFilter']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
