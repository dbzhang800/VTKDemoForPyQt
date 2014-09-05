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

        points = vtk.vtkPoints()
        points.InsertNextPoint(0.0, 0.0, 0.0)
        points.InsertNextPoint(1.0, 0.0, 0.0)
        points.InsertNextPoint(0.0, 1.0, 0.0)

        pointsPolydata = vtk.vtkPolyData()
        pointsPolydata.SetPoints(points)

        vertexFilter = vtk.vtkVertexGlyphFilter()
        vertexFilter.SetInputConnection(pointsPolydata.GetProducerPort())
        vertexFilter.Update()

        polydata = vtk.vtkPolyData()
        polydata.ShallowCopy(vertexFilter.GetOutput())

        # Setup colors
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("Colors")
        colors.InsertNextTupleValue((255, 0, 0))
        colors.InsertNextTupleValue((0, 255, 0))
        colors.InsertNextTupleValue((0, 0, 255))

        polydata.GetPointData().SetScalars(colors)
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(polydata.GetProducerPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetPointSize(5)
 
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

        self.setWindowTitle("Colored Points example")

    def categories(self):
        return ['Simple']

    def mainClasses(self):
        return ['vtkPoints', 'vtkVertexGlyphFilter']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
