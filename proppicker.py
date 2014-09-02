#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
import sys
import os.path
import weakref

from PyQt4 import QtCore, QtGui
QtCore.Signal = QtCore.pyqtSignal

import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class MouseInteractorActor(vtk.vtkInteractorStyleTrackballCamera):
    u"""参考
    http://www.vtk.org/Wiki/VTK/Examples/Python/Interaction/MouseEvents"""
    def __init__(self):
        self.AddObserver('LeftButtonPressEvent', self.onLeftButtonPressEvent)
        self.AddObserver('MouseMoveEvent', self.onMouseMoveEvent)
        self.AddObserver('LeftButtonReleaseEvent', self.onLeftButtonReleaseEvent)

        self._lastPickedActor = None
        self._lastPickedProperty = vtk.vtkProperty()

        self._mouseMoved = False

    def lastPickedActor(self):
        return self._lastPickedActor() if self._lastPickedActor else None

    def onLeftButtonPressEvent(self, obj, evt):
        self._mouseMoved = False
        self.OnLeftButtonDown()

    def onMouseMoveEvent(self, obj, evt):
        self._mouseMoved = True
        self.OnMouseMove()

    def onLeftButtonReleaseEvent(self, obj, evt):
        if not self._mouseMoved:
            clickPos = self.GetInteractor().GetEventPosition()
            #Pick from this location
            picker = vtk.vtkPropPicker()
            picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())

            #If we picked something before, reset its property
            if self.lastPickedActor():
                self.lastPickedActor().GetProperty().DeepCopy(self._lastPickedProperty)

            self._lastPickedActor = weakref.ref(picker.GetActor()) if picker.GetActor() else None
            if self.lastPickedActor():
                #Save the property of the picked actor
                self._lastPickedProperty.DeepCopy(self.lastPickedActor().GetProperty())
                #Highlight the picked actor
                self.lastPickedActor().GetProperty().SetColor(1.0, 0.0, 0.0)
                self.lastPickedActor().GetProperty().SetDiffuse(1.0)
                self.lastPickedActor().GetProperty().SetSpecular(0.0)
            else:
                print 'No actor get pickered'

        #Call parent member
        self.OnLeftButtonUp()


class VTKFrame(QtGui.QFrame):
    def __init__(self, parent = None):
        super(VTKFrame, self).__init__(parent)

        self.vl = QtGui.QVBoxLayout(self)
        self.vl.setContentsMargins(0,0,0,0)
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vl.addWidget(self.vtkWidget)
 
        self._renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self._renderer)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        #Create an style
        self._interactorStyle = MouseInteractorActor()
        self._interactorStyle.SetDefaultRenderer(self._renderer)
        self.vtkWidget.SetInteractorStyle(self._interactorStyle)

        self._actor1 = self.createActor1()
        self._actor2 = self.createActor2()
 
        self._renderer.AddActor(self._actor1)
        self._renderer.AddActor(self._actor2)
        self._renderer.ResetCamera()
        self._renderer.SetBackground(.1, .2, .3)

        self._initialized = False

    def createActor1(self):
        # Create source
        polyDataPoints = vtk.vtkPoints()
        polyDataPoints.InsertPoint(0, 1., 0., 0.)
        polyDataPoints.InsertPoint(1, 1., 0., 10.)
        polyDataPoints.InsertPoint(2, 3., 0., 10.)
        polyDataPoints.InsertPoint(3, 2., 0., 0.)

        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(4)
        polygon.GetPointIds().SetId(0, 0)
        polygon.GetPointIds().SetId(1, 1)
        polygon.GetPointIds().SetId(2, 2)
        polygon.GetPointIds().SetId(3, 3)

        polygons = vtk.vtkCellArray()
        polygons.InsertNextCell(polygon)

        polyData = vtk.vtkPolyData()
        polyData.SetPoints(polyDataPoints)
        #polyData.SetLines(polygons)
        polyData.SetPolys(polygons)

        rotationalExtrusionFilter = vtk.vtkRotationalExtrusionFilter()
        rotationalExtrusionFilter.SetInput(polyData)
        rotationalExtrusionFilter.SetResolution(10)
        rotationalExtrusionFilter.SetAngle(240)
        rotationalExtrusionFilter.SetTranslation(0)
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(rotationalExtrusionFilter.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        #actor.GetProperty().SetColor(1.0, 0, 0)

        return actor
    
    def createActor2(self):
        # Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(0, 0, 0)
        source.SetRadius(0.8)
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        return actor

    def showEvent(self, evt):
        if self._initialized:
            return
        self.iren.Initialize()
        self._initialized = True

class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Picker Example")

    def categories(self):
        return ['Simple', 'Picker', 'Extrusion']

    def mainClasses(self):
        return ['vtkPoints', 'vtkPolygon', 'vtkCellArray', 'vtkRotationalExtrusionFilter', 'vtkSphereSource']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
