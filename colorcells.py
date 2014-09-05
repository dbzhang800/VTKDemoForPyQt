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
 
        # Provide some geometry
        resolution = 8
        aPlane = vtk.vtkPlaneSource()
        aPlane.SetXResolution(resolution)
        aPlane.SetYResolution(resolution)

        # Create cell data
        cellData = vtk.vtkFloatArray()
        for i in range(resolution * resolution):
            cellData.InsertNextValue(i+1)

        # Create a lookup table to map cell data to colors
        lut = vtk.vtkLookupTable()
        tableSize = max(resolution*resolution+1, 10)
        lut.SetNumberOfTableValues(tableSize)
        lut.Build()

        # Fill in a few known colors, the rest will be generated if needed
        lut.SetTableValue(0     , 0     , 0     , 0, 1)# Black
        lut.SetTableValue(1, 0.8900, 0.8100, 0.3400, 1)# Banana
        lut.SetTableValue(2, 1.0000, 0.3882, 0.2784, 1)# Tomato
        lut.SetTableValue(3, 0.9608, 0.8706, 0.7020, 1)# Wheat
        lut.SetTableValue(4, 0.9020, 0.9020, 0.9804, 1)# Lavender
        lut.SetTableValue(5, 1.0000, 0.4900, 0.2500, 1)# Flesh
        lut.SetTableValue(6, 0.5300, 0.1500, 0.3400, 1)# Raspberry
        lut.SetTableValue(7, 0.9804, 0.5020, 0.4471, 1)# Salmon
        lut.SetTableValue(8, 0.7400, 0.9900, 0.7900, 1)# Mint
        lut.SetTableValue(9, 0.2000, 0.6300, 0.7900, 1)# Peacock

        aPlane.Update() #Force an update so we can set cell data
        aPlane.GetOutput().GetCellData().SetScalars(cellData)

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(aPlane.GetOutputPort())
        mapper.SetScalarRange(0, tableSize - 1)
        mapper.SetLookupTable(lut)
 
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

        self.setWindowTitle("Color Cells example")

    def categories(self):
        return ['Demo']

    def mainClasses(self):
        return ['vtkPlaneSource', 'vtkLookupTable']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
