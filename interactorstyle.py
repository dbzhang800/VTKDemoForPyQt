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

        #Sphere1
        sphereSource1 = vtk.vtkSphereSource()
        sphereSource1.SetCenter(0, 0, 0)
        sphereSource1.SetRadius(4.0)
        sphereSource1.Update()

        mapper1 = vtk.vtkPolyDataMapper()
        mapper1.SetInputConnection(sphereSource1.GetOutputPort())

        actor1 = vtk.vtkActor()
        actor1.SetMapper(mapper1)
 
        #Sphere2
        sphereSource2 = vtk.vtkSphereSource()
        sphereSource2.SetCenter(10, 0, 0)
        sphereSource2.SetRadius(3.0)
        sphereSource2.Update()

        mapper2 = vtk.vtkPolyDataMapper()
        mapper2.SetInputConnection(sphereSource2.GetOutputPort())

        actor2 = vtk.vtkActor()
        actor2.SetMapper(mapper2)

        #
        self.ren.AddActor(actor1)
        self.ren.AddActor(actor2)
        self.ren.SetBackground(1, 1, 1)
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
        self._createDockWidget()

        self.setWindowTitle("Interactor Style")

    def categories(self):
        return ['Demo']

    def mainClasses(self):
        return ['vtkInteractorStyle', 'vtkSphereSource']

    def _createDockWidget(self):
        self._interactorStylesWidget = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout(self._interactorStylesWidget)

        styles = ['TrackballCamera', 'TrackballActor', 'Unicam', 'User',
                'Switch', 'Flight', 'RubberBandZoom', 'JoystickCamera']

        buttonGroup = QtGui.QButtonGroup(self)
        for s in styles:
            btn = QtGui.QRadioButton(s)
            vbox.addWidget(btn)
            buttonGroup.addButton(btn)

        vbox.addStretch(1)
        dockWidget = QtGui.QDockWidget("Style")
        dockWidget.setWidget(self._interactorStylesWidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWidget)

        buttonGroup.buttonClicked.connect(self.onStyleButtonClicked)

    def onStyleButtonClicked(self, btn):
        funcName = 'vtkInteractorStyle'+btn.text()
        func = getattr(vtk, str(funcName))
        style = func()
        self.centralWidget().iren.SetInteractorStyle(style)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
