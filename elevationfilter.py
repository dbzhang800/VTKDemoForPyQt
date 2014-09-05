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
 
        # Created a grid of points
        points = vtk.vtkPoints()
        gridSize = 10
        for x in range(10):
            for y in range(10):
                points.InsertNextPoint(x, y, (x+y) / (y+1))

        bounds = [1] * 6
        points.GetBounds(bounds)

        # Add the grid points to a polydata object
        inputPolyData = vtk.vtkPolyData()
        inputPolyData.SetPoints(points)

        # Triangulate the grid points
        delaunay = vtk.vtkDelaunay2D()
        delaunay.SetInput(inputPolyData)
        delaunay.Update()

        elevationFilter = vtk.vtkElevationFilter()
        elevationFilter.SetInputConnection(delaunay.GetOutputPort())
        elevationFilter.SetLowPoint(0, 0, bounds[4])
        elevationFilter.SetHighPoint(0, 0, bounds[5])
        elevationFilter.Update()

        output = vtk.vtkPolyData()
        output.ShallowCopy(vtk.vtkPolyData.SafeDownCast(elevationFilter.GetOutput()))

        elevation = vtk.vtkFloatArray.SafeDownCast(output.GetPointData().GetArray("Elevation"))

        # Create the color map
        colorLookupTable = vtk.vtkLookupTable()
        colorLookupTable.SetTableRange(bounds[4], bounds[5])
        colorLookupTable.Build()

        # Generate the colors for each point based on the color map
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("Colors")

        for i in range(output.GetNumberOfPoints()):
            val = elevation.GetValue(i)
            dcolor = [1.0] * 3
            colorLookupTable.GetColor(val, dcolor)
            color = [1] * 3
            for j in range(3):
                color[j] = 255 * dcolor[j]

            colors.InsertNextTupleValue(color)

        output.GetPointData().AddArray(colors)

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(output.GetProducerPort())
 
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

        self.setWindowTitle("Elevation Filter example")

    def categories(self):
        return ['Filters']

    def mainClasses(self):
        return ['vtkElevationFilter', 'vtkDelaunay2D', 'vtkLookupTable']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
