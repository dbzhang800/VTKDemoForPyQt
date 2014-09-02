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
        sphereSource = vtk.vtkSphereSource()
        sphereSource.Update()

        input_ = vtk.vtkPolyData()
        input_.ShallowCopy(sphereSource.GetOutput())

        arrowSource = vtk.vtkArrowSource()

        glyph3D = vtk.vtkGlyph3D()
        glyph3D.SetSourceConnection(arrowSource.GetOutputPort())
        glyph3D.SetVectorModeToUseNormal()
        glyph3D.SetInput(input_)
        glyph3D.SetScaleFactor(0.2)
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

        self.setWindowTitle("Oriented Glyphs example")

    def categories(self):
        return ['glyph3d']

    def mainClasses(self):
        return ['vtkGlyph3D', 'vtkSphereSource', 'vtkArrowSource']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
