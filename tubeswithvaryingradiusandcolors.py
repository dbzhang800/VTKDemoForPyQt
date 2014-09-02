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
        rT1, rT2 = 0.1, 0.5 #Start/end tube radii
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

        # Varying tube radius using sine-function
        tubeRadius = vtk.vtkDoubleArray()
        tubeRadius.SetName("TubeRadius")
        tubeRadius.SetNumberOfTuples(nV)
        for i in range(nV):
            tubeRadius.SetTuple1(i, rT1 + (rT2-rT1) * math.sin(math.pi * i / (nV - 1)))

        polyData.GetPointData().AddArray(tubeRadius)
        polyData.GetPointData().SetActiveScalars("TubeRadius")

        # RGB array, Varying from blue to red
        colors = vtk.vtkUnsignedCharArray()
        colors.SetName("Colors")
        colors.SetNumberOfComponents(3)
        colors.SetNumberOfTuples(nV)
        for i in range(nV):
            colors.InsertTuple3(i,
                    int(255 * i / (nV - 1)),
                    0,
                    int(255 * (nV - 1 - i) / (nV - 1)))

        polyData.GetPointData().AddArray(colors)

        tube = vtk.vtkTubeFilter()
        tube.SetInput(polyData)
        tube.SetNumberOfSides(nTv)
        tube.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tube.GetOutputPort())
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointFieldData()
        mapper.SelectColorArray("Colors")
 
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

        self.setWindowTitle("Spiral tube example")

    def categories(self):
        return ['Demo', 'Tube']

    def mainClasses(self):
        return ['vtkPoints', 'vtkCellArray', 'vtkTubeFilter', 'vtkPolyData']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
