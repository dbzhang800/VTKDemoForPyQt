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
         
        #Create a sphere
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(50)
        sphere.SetThetaResolution(100)
        sphere.SetPhiResolution(100)
         
        plane = vtk.vtkPlane()
        plane.SetOrigin(20, 0, 0)
        plane.SetNormal(1, 0, 0)
         
        #create cutter
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputConnection(sphere.GetOutputPort())
        cutter.Update()
         
        cutStrips = vtk.vtkStripper()
        cutStrips.SetInputConnection(cutter.GetOutputPort())
        cutStrips.Update()
        cutPoly = vtk.vtkPolyData()
        cutPoly.SetPoints((cutStrips.GetOutput()).GetPoints())
        cutPoly.SetPolys((cutStrips.GetOutput()).GetLines())
         
        cutMapper = vtk.vtkPolyDataMapper()
        cutMapper.SetInput(cutPoly)
        #cutMapper.SetInputConnection(cutter.GetOutputPort())
         
        cutActor = vtk.vtkActor()
        cutActor.GetProperty().SetColor(1, 1, 0)
        cutActor.GetProperty().SetEdgeColor(0, 1, 0)
         
        cutActor.GetProperty().SetLineWidth(2)
        cutActor.GetProperty().EdgeVisibilityOn()
        cutActor.SetMapper(cutMapper)

        #create renderers and add actors of plane and cube
        self.ren.AddActor(cutActor)

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

        self.setWindowTitle("Cut example")

    def categories(self):
        return ['Cutter']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
