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
        parametricObjects = list()
        parametricObjects.append(vtk.vtkParametricBoy())
        parametricObjects.append(vtk.vtkParametricConicSpiral())
        parametricObjects.append(vtk.vtkParametricCrossCap())
        parametricObjects.append(vtk.vtkParametricDini())
 
        parametricObjects.append(vtk.vtkParametricEllipsoid())
        parametricObjects[-1].SetXRadius(0.5)
        parametricObjects[-1].SetYRadius(2.0)
        parametricObjects.append(vtk.vtkParametricEnneper())
        parametricObjects.append(vtk.vtkParametricFigure8Klein())
        parametricObjects.append(vtk.vtkParametricKlein())
 
        parametricObjects.append(vtk.vtkParametricMobius())
        parametricObjects[-1].SetRadius(2)
        parametricObjects[-1].SetMinimumV(-0.5)
        parametricObjects[-1].SetMaximumV(0.5)
        parametricObjects.append(vtk.vtkParametricRandomHills())
        parametricObjects[-1].AllowRandomGenerationOff()
        parametricObjects.append(vtk.vtkParametricRoman())
        parametricObjects.append(vtk.vtkParametricSuperEllipsoid())
        parametricObjects[-1].SetN1(0.5)
        parametricObjects[-1].SetN2(0.1)
 
        parametricObjects.append(vtk.vtkParametricSuperToroid())
        parametricObjects[-1].SetN1(0.2)
        parametricObjects[-1].SetN2(3.0)
        parametricObjects.append(vtk.vtkParametricTorus())
        parametricObjects.append(vtk.vtkParametricSpline())

        # Add some points to the parametric spline.
        inputPoints = vtk.vtkPoints()
        vtk.vtkMath.RandomSeed(8775070)
        for i in range(10):
            x = vtk.vtkMath.Random(0.0,1.0)
            y = vtk.vtkMath.Random(0.0,1.0)
            z = vtk.vtkMath.Random(0.0,1.0)
            inputPoints.InsertNextPoint(x, y, z)
        parametricObjects[-1].SetPoints(inputPoints)
 
        # There are only 15 objects.
        parametricFunctionSources = list()
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
        for idx, item in enumerate(parametricObjects):
            parametricFunctionSources.append(vtk.vtkParametricFunctionSource())
            parametricFunctionSources[idx].SetParametricFunction(item)
            parametricFunctionSources[idx].Update()
 
            mappers.append(vtk.vtkPolyDataMapper())
            mappers[idx].SetInputConnection(parametricFunctionSources[idx].GetOutputPort())
 
            actors.append(vtk.vtkActor())
            actors[idx].SetMapper(mappers[idx])
 
            textmappers.append(vtk.vtkTextMapper())
            textmappers[idx].SetInput(item.GetClassName())
            textmappers[idx].SetTextProperty(textProperty)
 
            textactors.append(vtk.vtkActor2D())
            textactors[idx].SetMapper(textmappers[idx])
            textactors[idx].SetPosition(100, 16)
 
            renderers.append(vtk.vtkRenderer())
 
        gridDimensions = 4
 
        for idx in range(len(parametricObjects)):
            if idx < gridDimensions * gridDimensions:
                renderers.append(vtk.vtkRenderer)
 
        rendererSize = 200
 
        # setup the RenderWindow
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
 
                if idx > (len(parametricObjects) - 1):
                    continue
 
                renderers[idx].SetViewport(viewport)
                self.vtkWidget.GetRenderWindow().AddRenderer(renderers[idx])
 
                renderers[idx].AddActor(actors[idx])
                renderers[idx].AddActor(textactors[idx])
                renderers[idx].SetBackground(0.2,0.3,0.4)
                renderers[idx].ResetCamera()
                renderers[idx].GetActiveCamera().Azimuth(30)
                renderers[idx].GetActiveCamera().Elevation(-30)
                renderers[idx].GetActiveCamera().Zoom(0.9)
                renderers[idx].ResetCameraClippingRange()
        
        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            self._initialized = True
 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Parametric objects example")

    def categories(self):
        return ['Geometric Objects']

    def mainClasses(self):
        return ['vtkParametricBoy', 'vtkParametricConicSpiral', 'vtkParametricCrossCap', 'vtkParametricDini', 'vtkParametricEllipsoid', 'vtkParametricEnneper', 'vtkParametricFigure8Klein', 'vtkParametricKlein', 'vtkParametricMobius', 'vtkParametricRandomHills', 'vtkParametricRoman', 'vtkParametricSuperEllipsoid', 'vtkParametricSuperToroid', 'vtkParametricTorus', 'vtkParametricSpline', 'vtkParametricFunctionSource', 'vtkPoints', 'vtkTextProperty']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
