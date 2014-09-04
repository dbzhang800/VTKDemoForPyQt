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
 
        sphere1 = vtk.vtkSphere()
        sphere1.SetCenter(0.9, 0, 0)
        sphere2 = vtk.vtkSphere()
        sphere2.SetCenter(-0.9, 0, 0)

        implicitBoolean = vtk.vtkImplicitBoolean()
        implicitBoolean.AddFunction(sphere1)
        implicitBoolean.AddFunction(sphere2)
        implicitBoolean.SetOperationTypeToUnion()
        #implicitBoolean.SetOperationTypeToIntersection()

        # Sample the function
        sample = vtk.vtkSampleFunction()
        sample.SetSampleDimensions(50, 50, 50)
        sample.SetImplicitFunction(implicitBoolean)
        sample.SetModelBounds(-3, 3, -3, 3, -3, 3)

        # Create the 0 isosurface
        contours = vtk.vtkContourFilter()
        contours.SetInputConnection(sample.GetOutputPort())
        contours.GenerateValues(1, 1, 1)
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(contours.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
 
        self.ren.AddActor(actor)
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

        self.setWindowTitle("Implicit Boolean example")

    def categories(self):
        return ['Implicit Function', 'Filters']

    def mainClasses(self):
        return ['vtkSampleFunction', 'vtkContourFilter', 'vtkImplicitBoolean', 'vtkSphere']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
