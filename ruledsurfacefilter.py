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
        self.ren.SetBackground(0.3, 0.4, 0.5)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 
        # Create lines.
        points = vtk.vtkPoints()
        points.InsertPoint(0, 0, 0, 1)
        points.InsertPoint(1, 1, 0, 0)
        points.InsertPoint(2, 0, 1, 0)
        points.InsertPoint(3, 1, 1, 1)

        line1 = vtk.vtkLine()
        line1.GetPointIds().SetId(0, 0)
        line1.GetPointIds().SetId(1, 1)

        line2 = vtk.vtkLine()
        line2.GetPointIds().SetId(0, 2)
        line2.GetPointIds().SetId(1, 3)

        lines = vtk.vtkCellArray()
        lines.InsertNextCell(line1)
        lines.InsertNextCell(line2)

        polyData = vtk.vtkPolyData()
        polyData.SetPoints(points)
        polyData.SetLines(lines)

        ruledSurfaceFilter = vtk.vtkRuledSurfaceFilter()
        ruledSurfaceFilter.SetInputConnection(polyData.GetProducerPort())

        ruledSurfaceFilter.SetResolution(21, 21)
        ruledSurfaceFilter.SetRuledModeToResample()
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(ruledSurfaceFilter.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.89, 0.81, 0.34)
 
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

        self.setWindowTitle("Ruled Surface Filter example")

    def categories(self):
        return ['Filters']

    def mainClasses(self):
        return ['vtkRuledSurfaceFilter', 'vtkLine', 'vtkPoints', 'vtkCellArray']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
