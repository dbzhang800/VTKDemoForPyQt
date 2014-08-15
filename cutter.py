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

        #Create a cube
        cube=vtk.vtkCubeSource()
        cube.SetXLength(40)
        cube.SetYLength(30)
        cube.SetZLength(20)
        cubeMapper=vtk.vtkPolyDataMapper()
        cubeMapper.SetInputConnection(cube.GetOutputPort())
         
        #create a plane to cut,here it cuts in the XZ direction (xz normal=(1,0,0);XY =(0,0,1),YZ =(0,1,0)
        plane=vtk.vtkPlane()
        plane.SetOrigin(10,0,0)
        plane.SetNormal(1,0,0)
         
        #create cutter
        cutter=vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputConnection(cube.GetOutputPort())
        cutter.Update()
        cutterMapper=vtk.vtkPolyDataMapper()
        cutterMapper.SetInputConnection( cutter.GetOutputPort())
         
        #create plane actor
        planeActor=vtk.vtkActor()
        planeActor.GetProperty().SetColor(1.0,1,0)
        planeActor.GetProperty().SetLineWidth(2)
        planeActor.SetMapper(cutterMapper)
         
        #create cube actor
        cubeActor=vtk.vtkActor()
        cubeActor.GetProperty().SetColor(0.5,1,0.5)
        cubeActor.GetProperty().SetOpacity(0.5)
        cubeActor.SetMapper(cubeMapper)
         
        #create renderers and add actors of plane and cube
        self.ren.AddActor(planeActor)
        self.ren.AddActor(cubeActor) 

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

        self.setWindowTitle("Simple cut example")

    def categories(self):
        return ['Cutter']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
