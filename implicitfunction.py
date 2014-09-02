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
 
        # Create cylinder
        cylinder = vtk.vtkCylinder()
        cylinder.SetCenter(0, 0, 0)
        cylinder.SetRadius(1.0)
        
        # Create plane
        plane = vtk.vtkPlane()
        plane.SetOrigin(0, 0, 0)
        plane.SetNormal(0, -1, 0)

        # Cut the cylinder
        cuted_cylinder = vtk.vtkImplicitBoolean()
        cuted_cylinder.SetOperationTypeToIntersection()
        #cuted_cylinder.SetOperationTypeToUnion()
        cuted_cylinder.AddFunction(cylinder)
        cuted_cylinder.AddFunction(plane)

        # Sample 
        sample = vtk.vtkSampleFunction()
        sample.SetImplicitFunction(cuted_cylinder)
        sample.SetModelBounds(-1.5 , 1.5 , -1.5 , 1.5 , -1.5 , 1.5)
        sample.SetSampleDimensions(60, 60, 60)
        sample.SetComputeNormals(0)

        #
        surface = vtk.vtkContourFilter()
        #surface.SetInput(sample.GetOutput())
        surface.SetInputConnection(sample.GetOutputPort())
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        #mapper.SetInput(surface.GetOutput())
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

        self.setWindowTitle("Simple Implicitfunction Example")

    def categories(self):
        return ['Simple', 'Implicit Function']

    def mainClasses(self):
        return ['vtkCylinder', 'vtkPlane', 'vtkImplicitBoolean', 'vtkSampleFunction', 'vtkContourFilter']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
