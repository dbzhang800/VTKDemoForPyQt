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
        self.ren.SetBackground(0.2, 0.3, 0.4)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 
        # Create Spiral tube
        nV = 256 #No. of vertices
        nCyc = 5 #No. of spiral cycles
        rS = 2.0   #Spiral radius
        h = 10.0
        nTv = 8 #No. of surface elements for each tube vertex

        points = vtk.vtkPoints()
        for i in range(nV):
            vX = rS * math.cos(2 * math.pi * nCyc * i / (nV-1))
            vY = rS * math.sin(2 * math.pi * nCyc * i / (nV-1))
            vZ = h * i / nV
            points.InsertPoint(i, vX, vY, vZ)

        lines = vtk.vtkCellArray()
        lines.InsertNextCell(nV)
        for i in range(nV):
            lines.InsertCellPoint(i)

        polyData = vtk.vtkPolyData()
        polyData.SetPoints(points)
        polyData.SetLines(lines)

        tube = vtk.vtkTubeFilter()
        tube.SetInput(polyData)
        tube.SetNumberOfSides(nTv)
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tube.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
 
        self.ren.AddActor(actor)
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

        self.setWindowTitle("Tube example")

    def categories(self):
        return ['Simple', 'Tube']

    def mainClasses(self):
        return ['vtkPoints', 'vtkCellArray', 'vtkTubeFilter', 'vtkPolyData']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
