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
        # Create five points. 
        origin = [0.0, 0.0, 0.0]
        p0 = [1.0, 0.0, 0.0]
        p1 = [0.0, 1.0, 0.0]
        p2 = [0.0, 1.0, 2.0]
        p3 = [1.0, 2.0, 3.0]
        p4 = [1.0, 2.0, 8.0]
         
        # Create a vtkPoints object and store the points in it
        points = vtk.vtkPoints()
        points.InsertNextPoint(origin)
        points.InsertNextPoint(p0)
        points.InsertNextPoint(p1)
        points.InsertNextPoint(p2)
        points.InsertNextPoint(p3)
        points.InsertNextPoint(p4)
         
        # Create a cell array to store the lines in and add the lines to it
        lines = vtk.vtkCellArray()
         
        for i in range(4):
          line = vtk.vtkLine()
          line.GetPointIds().SetId(0,i)
          line.GetPointIds().SetId(1,i+1)
          lines.InsertNextCell(line)

        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("Colors")
        colors.InsertNextTupleValue([255, 0, 0])
        colors.InsertNextTupleValue([0, 255, 0])
        colors.InsertNextTupleValue([0, 0, 255])
        colors.InsertNextTupleValue([0, 255, 255])
         
        # Create a polydata to store everything in
        linesPolyData = vtk.vtkPolyData()
         
        # Add the points to the dataset
        linesPolyData.SetPoints(points)
         
        # Add the lines to the dataset
        linesPolyData.SetLines(lines)

        # Color the lines
        linesPolyData.GetCellData().SetScalars(colors) 

        # Setup actor and mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(linesPolyData)
         
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

        self.setWindowTitle("Colored lines example")

    def categories(self):
        return ['Simple']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
