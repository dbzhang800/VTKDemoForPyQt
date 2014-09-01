#!/usr/bin/env python
# -*- coding: UTF-8 -*-

u"""
This example produces two arrows whose scale stays fixed with respect to the
distance from the camera (i.e. as you zoom in and out). Standard spheres are
drawn for comparison. 
"""

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
 
        # Create a set of points
        fixedPointSource = vtk.vtkPointSource()
        fixedPointSource.SetNumberOfPoints(2)

        # Calculate the distance to the camera of each point
        distanceToCamera = vtk.vtkDistanceToCamera()
        distanceToCamera.SetInputConnection(fixedPointSource.GetOutputPort())
        distanceToCamera.SetScreenSize(100.0)

        # Glyph each point with an arrow
        arrow = vtk.vtkArrowSource()
        fixedGlyph = vtk.vtkGlyph3D()
        fixedGlyph.SetInputConnection(distanceToCamera.GetOutputPort())
        fixedGlyph.SetSourceConnection(arrow.GetOutputPort())

        # Scale each point
        fixedGlyph.SetScaleModeToScaleByScalar()
        fixedGlyph.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, 
                "DistanceToCamera")

        # Create a mapper
        fixedMapper = vtk.vtkPolyDataMapper()
        fixedMapper.SetInputConnection(fixedGlyph.GetOutputPort())
        fixedMapper.SetScalarVisibility(False)
 
        # Create an actor
        fixedActor = vtk.vtkActor()
        fixedActor.SetMapper(fixedMapper)
        fixedActor.GetProperty().SetColor(0, 1, 1)

        #............................................................
        # Draw some spheres that get bigger when zooming in.
        # Create a set of points
        pointSource = vtk.vtkPointSource()
        pointSource.SetNumberOfPoints(4)

        # Glyph each point with a sphere
        sphere = vtk.vtkSphereSource()
        glyph = vtk.vtkGlyph3D()
        glyph.SetInputConnection(pointSource.GetOutputPort())
        glyph.SetSourceConnection(sphere.GetOutputPort())
        glyph.SetScaleFactor(0.1)

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(glyph.GetOutputPort())
        mapper.SetScalarVisibility(False)
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0, 1, 1)

        distanceToCamera.SetRenderer(self.ren)

        # Add the actors to the scene
        self.ren.AddActor(fixedActor)
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

        self.setWindowTitle("Distance to Camera")

    def categories(self):
        return ['Demo']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
