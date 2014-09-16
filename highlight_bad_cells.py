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
        source = vtk.vtkSphereSource()
        source.Update()

        triangleFilter = vtk.vtkTriangleFilter()
        triangleFilter.SetInputConnection(source.GetOutputPort())
        triangleFilter.Update()

        # Create a mapper and actor
        sphereMapper = vtk.vtkDataSetMapper()
        sphereMapper.SetInputConnection(triangleFilter.GetOutputPort())
        sphereActor = vtk.vtkActor()
        sphereActor.SetMapper(sphereMapper)

        mesh = triangleFilter.GetOutput()
        qualityFilter = vtk.vtkMeshQuality()
        qualityFilter.SetInput(mesh)
        qualityFilter.SetTriangleQualityMeasureToArea()
        qualityFilter.Update()

        qualityMesh = qualityFilter.GetOutput()
        #qualityArray = vtk.vtkDoubleArray.SafeDownCase(qualityMesh.GetCellData().GetArray("Quality"))
        selectCells = vtk.vtkThreshold()
        selectCells.ThresholdByLower(0.02)
        selectCells.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, vtk.vtkDataSetAttributes.SCALARS)
        selectCells.SetInput(qualityMesh)
        selectCells.Update()
        ug = selectCells.GetOutput()

        # Create a mapper and actor
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInput(ug)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1, 0, 0)
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetLineWidth(5)
 
        self.ren.AddActor(sphereActor)
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

        self.setWindowTitle("Highlight Bad Cells")

    def categories(self):
        return ['Filters']

    def mainClasses(self):
        return ['vtkThreshold', 'vtkMeshQuality', 'vtkTriangleFilter']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
