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
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        superquadricSource = vtk.vtkSuperquadricSource()
        superquadricSource.SetPhiRoundness(3.1)
        superquadricSource.SetThetaRoundness(2.2)

        clipPlane = vtk.vtkPlane()
        clipPlane.SetNormal(1.0, -1.0, -1.0)
        clipPlane.SetOrigin(0, 0, 0)

        clipper = vtk.vtkClipPolyData()
        clipper.SetInputConnection(superquadricSource.GetOutputPort())
        clipper.SetClipFunction(clipPlane)

        superquadricMapper = vtk.vtkPolyDataMapper()
        superquadricMapper.SetInputConnection(clipper.GetOutputPort())

        superquadricActor = vtk.vtkActor()
        superquadricActor.SetMapper(superquadricMapper)

        #create renderers and add actors of plane and cube
        self.ren.AddActor(superquadricActor)

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

        self.setWindowTitle("Solid clip example")

    def categories(self):
        return ['Clipper']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
