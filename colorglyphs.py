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
        self.ren.SetBackground(1, 1, 1)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 
        # Create points
        points = vtk.vtkPoints()
        points.InsertNextPoint(0, 0, 0)
        points.InsertNextPoint(5, 0, 0)
        points.InsertNextPoint(10, 0, 0)

        # Setup scales. This can also be an Int array
        # char is used since it takes the least memory
        colors = vtk.vtkUnsignedCharArray()
        colors.SetName("colors")
        colors.SetNumberOfComponents(3)
        colors.InsertNextTupleValue((255, 0, 0))
        colors.InsertNextTupleValue((0, 255, 0))
        colors.InsertNextTupleValue((0, 0, 255))

        # Combine into a polydata
        polyData = vtk.vtkPolyData()
        polyData.SetPoints(points)
        polyData.GetPointData().SetScalars(colors)

        # Create anything you want here, we will use a cube for the demo.
        cubeSource = vtk.vtkCubeSource()
        
        glyph3D = vtk.vtkGlyph3D()
        glyph3D.SetColorModeToColorByScalar()
        glyph3D.SetSourceConnection(cubeSource.GetOutputPort())
        glyph3D.SetInput(polyData)
        glyph3D.ScalingOff() #Needed, otherwise only the red cube is visible
        glyph3D.Update()

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(glyph3D.GetOutputPort())
 
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

        self.setWindowTitle("Color Glyphs Example")

    def categories(self):
        return ['glyph3d']

    def mainClasses(self):
        return ['vtkGlyph3D', 'vtkPoints']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
