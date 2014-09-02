#!/usr/bin/env python
# -*- coding: UTF-8 -*-

u'''
This example shows how to interpolate a set of points and generate tubes around the resulting polyline.
Scalars associated with the points are also interpolated and used to vary the radius of the tube.
'''

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
        self.ren.SetBackground(0.2, 0.3, 0.4)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        points = vtk.vtkPoints()
        points.InsertPoint(0, 1, 0, 0)
        points.InsertPoint(1, 2, 0, 0)
        points.InsertPoint(2, 3, 1, 0)
        points.InsertPoint(3, 4, 1, 0)
        points.InsertPoint(4, 5, 0, 0)
        points.InsertPoint(5, 6, 0, 0)

        # Fit a spline to the points
        spline = vtk.vtkParametricSpline()
        spline.SetPoints(points)
        functionSource = vtk.vtkParametricFunctionSource()
        functionSource.SetParametricFunction(spline)
        functionSource.SetUResolution(10 * points.GetNumberOfPoints())
        functionSource.Update()

        # Interpolate the scalars
        interpolatedRadius = vtk.vtkTupleInterpolator()
        interpolatedRadius.SetInterpolationTypeToLinear()
        interpolatedRadius.SetNumberOfComponents(1)
        #interpolatedRadius.AddTuple(0, [0.2,]) ### ??? Donesn't work for Python
        #interpolatedRadius.AddTuple(1, (0.2,))
        #interpolatedRadius.AddTuple(2, (0.2,))
        #interpolatedRadius.AddTuple(3, (0.1,))
        #interpolatedRadius.AddTuple(4, (0.1,))
        #interpolatedRadius.AddTuple(5, (0.1,))

        # Generate the radius scalars
        tubeRadius = vtk.vtkDoubleArray()
        n = functionSource.GetOutput().GetNumberOfPoints()
        tubeRadius.SetNumberOfTuples(n)
        tubeRadius.SetName("TubeRadius")

        tMin = interpolatedRadius.GetMinimumT()
        tMax = interpolatedRadius.GetMaximumT()
        for i in range(n):
            t = (tMax - tMin) / (n - 1) * i + tMin
            r = 1.0
            #interpolatedRadius.InterpolateTuple(t, r) ### ??? Donesn't work for Python
            tubeRadius.SetTuple1(i, r)

        # Add the scalars to the polydata
        tubePolyData = functionSource.GetOutput()
        tubePolyData.GetPointData().AddArray(tubeRadius)
        tubePolyData.GetPointData().SetActiveScalars("TubeRadius")

        # Create the tubes
        tuber = vtk.vtkTubeFilter()
        tuber.SetInput(tubePolyData)
        tuber.SetNumberOfSides(20)
        tuber.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
 
        # Setup actors and mappers
        lineMapper = vtk.vtkPolyDataMapper()
        lineMapper.SetInput(tubePolyData)
        lineMapper.SetScalarRange(tubePolyData.GetScalarRange())

        tubeMapper = vtk.vtkPolyDataMapper()
        tubeMapper.SetInputConnection(tuber.GetOutputPort())
        tubeMapper.SetScalarRange(tubePolyData.GetScalarRange())
 
        lineActor = vtk.vtkActor()
        lineActor.SetMapper(lineMapper)
        tubeActor = vtk.vtkActor()
        tubeActor.SetMapper(tubeMapper)
 
        self.ren.AddActor(tubeActor)
        self.ren.AddActor(lineActor)
        self.ren.ResetCamera()

        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            #self.startTimer(30)
            self._initialized = True

    def timerEvent(self, evt):
        self.ren.GetActiveCamera().Azimuth(1)
        self.vtkWidget.GetRenderWindow().Render()
 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Tube From Splines example")

    def categories(self):
        return ['Simple', 'Tube']

    def mainClasses(self):
        return ['vtkTubeFilter']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
