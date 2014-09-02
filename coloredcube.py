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
        self.ren.SetBackground(1.0, 1.0, 1.0)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 
        # Create source
        # x = array of 8 3-tuples of float representing the vertices of a cube:
        x = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0),
             (0.0, 0.0, 1.0), (1.0, 0.0 ,1.0), (1.0, 1.0, 1.0), (0.0, 1.0, 1.0)]
     
        # pts = array of 6 4-tuples of vtkIdType (int) representing the faces
        #     of the cube in terms of the above vertices
        pts = [(0,1,2,3), (4,5,6,7), (0,1,5,4),
               (1,2,6,5), (2,3,7,6), (3,0,4,7)]
     
        # We'll create the building blocks of polydata including data attributes.
        points = vtk.vtkPoints()
        polys = vtk.vtkCellArray()
        scalars = vtk.vtkFloatArray()
     
        # Load the point, cell, and data attributes.
        for i in range(8):
            points.InsertPoint(i, x[i])
        for i in range(6):
            idList = vtk.vtkIdList()
            for it in pts[i]:
                idList.InsertNextId(int(it))
            polys.InsertNextCell(idList)
        for i in range(8):
            scalars.InsertTuple1(i,i)
     
        # We now assign the pieces to the vtkPolyData.
        cube = vtk.vtkPolyData()
        cube.SetPoints(points)
        cube.SetPolys(polys)
        cube.GetPointData().SetScalars(scalars)
     
        # Now we'll look at it.
        cubeMapper = vtk.vtkPolyDataMapper()
        cubeMapper.SetInput(cube)
        cubeMapper.SetScalarRange(0,7)
        cubeActor = vtk.vtkActor()
        cubeActor.SetMapper(cubeMapper)
 
        self.ren.AddActor(cubeActor)
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

        self.setWindowTitle("Colored cube example")

    def categories(self):
        return ['Simple']

    def mainClasses(self):
        return ['vtkPoints', 'vtkCellArray']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
