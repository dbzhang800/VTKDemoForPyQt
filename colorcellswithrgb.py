#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
import sys
import os.path
import random

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
 
        # Provide some geometry
        resolution = 8
        aPlane = vtk.vtkPlaneSource()
        aPlane.SetXResolution(resolution)
        aPlane.SetYResolution(resolution)
        aPlane.Update()

        # Create cell data
        cellData = vtk.vtkUnsignedCharArray()
        cellData.SetNumberOfComponents(3)
        cellData.SetNumberOfTuples(aPlane.GetOutput().GetNumberOfCells())

        for i in range(aPlane.GetOutput().GetNumberOfCells()):
            rgb = random.randint(64, 255), random.randint(64, 255), random.randint(64, 255)
            cellData.InsertTuple(i, rgb)

        aPlane.GetOutput().GetCellData().SetScalars(cellData)

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(aPlane.GetOutputPort())
 
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

        self.setWindowTitle("Color Cells with RGB example")

    def categories(self):
        return ['Demo']

    def mainClasses(self):
        return ['vtkPlaneSource']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
