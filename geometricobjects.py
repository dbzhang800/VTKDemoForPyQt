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
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        vl = QtGui.QVBoxLayout(self)
        vl.addWidget(self.vtkWidget)
        vl.setContentsMargins(0, 0, 0, 0)
 
        # Create source
        geometricObjects = list()
        geometricObjects.append(vtk.vtkArrowSource())
        geometricObjects.append(vtk.vtkConeSource())
        geometricObjects.append(vtk.vtkCubeSource())
        geometricObjects.append(vtk.vtkCylinderSource())
        geometricObjects.append(vtk.vtkDiskSource())
        geometricObjects.append(vtk.vtkLineSource())
        geometricObjects.append(vtk.vtkRegularPolygonSource())
        geometricObjects.append(vtk.vtkSphereSource())
        
        renderers = list()
        mappers = list()
        actors = list()
        textmappers = list()
        textactors = list()
        
        # Create a common text property.
        textProperty = vtk.vtkTextProperty()
        textProperty.SetFontSize(10)
        textProperty.SetJustificationToCentered()
        
        # Create a parametric function source, renderer, mapper 
        # and actor for each object.
        for idx, item in enumerate(geometricObjects):
            geometricObjects[idx].Update()
        
            mappers.append(vtk.vtkPolyDataMapper())
            mappers[idx].SetInputConnection(geometricObjects[idx].GetOutputPort())
        
            actors.append(vtk.vtkActor())
            actors[idx].SetMapper(mappers[idx])
        
            textmappers.append(vtk.vtkTextMapper())
            textmappers[idx].SetInput(item.GetClassName())
            textmappers[idx].SetTextProperty(textProperty)
        
            textactors.append(vtk.vtkActor2D())
            textactors[idx].SetMapper(textmappers[idx])
            textactors[idx].SetPosition(150, 16)
        
            renderers.append(vtk.vtkRenderer())
        
        gridDimensions = 3
        
        for idx in range(len(geometricObjects)):
            if idx < gridDimensions * gridDimensions:
                renderers.append(vtk.vtkRenderer())
        
        rendererSize = 300
        
        # Setup the RenderWindow
        self.vtkWidget.GetRenderWindow().SetSize(rendererSize * gridDimensions, rendererSize * gridDimensions)
        
        # Add and position the renders to the render window.
        viewport = list()
        for row in range(gridDimensions):
            for col in range(gridDimensions):
                idx = row * gridDimensions + col
        
                viewport[:] = []
                viewport.append(float(col) * rendererSize / (gridDimensions * rendererSize))
                viewport.append(float(gridDimensions - (row+1)) * rendererSize / (gridDimensions * rendererSize))
                viewport.append(float(col+1)*rendererSize / (gridDimensions * rendererSize))
                viewport.append(float(gridDimensions - row) * rendererSize / (gridDimensions * rendererSize))
        
                if idx > (len(geometricObjects) - 1):
                    continue
        
                renderers[idx].SetViewport(viewport)
                self.vtkWidget.GetRenderWindow().AddRenderer(renderers[idx])
        
                renderers[idx].AddActor(actors[idx])
                renderers[idx].AddActor(textactors[idx])
                renderers[idx].SetBackground(0.4,0.3,0.2)
        
        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            self._initialized = True
 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Geometric objects example")

    def categories(self):
        return ['Geometric Objects']

    def mainClasses(self):
        return ['vtkArrowSource', 'vtkConeSource', 'vtkCubeSource', 'vtkCylinderSource', 'vtkDiskSource', 'vtkLineSource', 'vtkRegularPolygonSource', 'vtkSphereSource', 'vtkTextProperty']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
