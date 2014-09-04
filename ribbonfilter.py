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

        nV = 256 # No. of vertices
        rS = 2.0 # Spiral radius
        nCyc = 3 # No. of spiral cycles
        h = 10.0 # Height

        # Create points and cells for a spiral
        points = vtk.vtkPoints()
        for i in range(nV):
            vX = rS * math.cos(2 * math.pi * nCyc * i / (nV - 1))
            vY = rS * math.sin(2 * math.pi * nCyc * i / (nV - 1))
            vZ = h * i / nV
            points.InsertPoint(i, vX, vY, vZ)

        lines = vtk.vtkCellArray()
        lines.InsertNextCell(nV)
        for i in range(nV):
            lines.InsertCellPoint(i)

        polyData = vtk.vtkPolyData()
        polyData.SetPoints(points)
        polyData.SetLines(lines)

        # Create a mapper and actor
        lineMapper = vtk.vtkPolyDataMapper()
        lineMapper.SetInput(polyData)

        lineActor = vtk.vtkActor()
        lineActor.SetMapper(lineMapper)
        lineActor.GetProperty().SetColor(0.8, 0.4, 0.2)
        lineActor.GetProperty().SetLineWidth(3)

        # Cteate a ribbon around the line
        ribbonFilter = vtk.vtkRibbonFilter()
        ribbonFilter.SetInput(polyData)
        ribbonFilter.SetWidth(0.4)

        # Create a mapper and actor
        ribbonMapper = vtk.vtkPolyDataMapper()
        ribbonMapper.SetInputConnection(ribbonFilter.GetOutputPort())

        ribbonActor = vtk.vtkActor()
        ribbonActor.SetMapper(ribbonMapper)
 
        self.ren.AddActor(lineActor)
        self.ren.AddActor(ribbonActor)
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

        self.setWindowTitle("Ribbon Filter Example")

    def categories(self):
        return ['Simple', 'Filters']

    def mainClasses(self):
        return ['vtkRibbonFilter', 'vtkPoints', 'vtkLine', 'vtkCellArray']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
