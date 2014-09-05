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
 
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 
        # Create source
        source = vtk.vtkConeSource()
        #source = vtk.vtkSphereSource()
        #source.SetCenter(0, 0, 5.0)
        #source.SetRadius(2.0)
        #source.SetPhiResolution(20)
        #source.SetThetaResolution(20)
        source.Update()

        data3D = source.GetOutput()

        boundsData = [1]*6
        centerData = [1]*3
        data3D.GetBounds(boundsData)
        data3D.GetCenter(centerData)

        # Black and white scene with the data in order to print the view
        mapperData = vtk.vtkPolyDataMapper()
        mapperData.SetInput(data3D)

        actorData = vtk.vtkActor()
        actorData.SetMapper(mapperData)
        actorData.GetProperty().SetColor(0, 0, 0)

        tmpRender = vtk.vtkRenderer()
        tmpRender.SetBackground(1, 1, 1)
        tmpRender.AddActor(actorData)
        tmpRender.ResetCamera()
        tmpRender.GetActiveCamera().SetParallelProjection(1)

        tmpRenderWindow = vtk.vtkRenderWindow()
        tmpRenderWindow.SetOffScreenRendering(1)
        tmpRenderWindow.AddRenderer(tmpRender)
        tmpRenderWindow.Render()

        # Get a print of the window
        windowToImageFilter = vtk.vtkWindowToImageFilter()
        windowToImageFilter.SetInput(tmpRenderWindow)
        windowToImageFilter.SetMagnification(2)
        windowToImageFilter.Update()

        # Extract the silhouette corresponding to the black limit of the image
        contourFilter = vtk.vtkContourFilter()
        contourFilter.SetInputConnection(windowToImageFilter.GetOutputPort())
        contourFilter.SetValue(0, 255)
        contourFilter.Update()

        # Make the contour coincide with the data.
        contour = contourFilter.GetOutput()

        boundsContour = [1]*6
        contour.GetBounds(boundsContour)
        ratioX = (boundsData[1]-boundsData[0])/(boundsContour[1]-boundsContour[0])
        ratioY = (boundsData[3]-boundsData[2])/(boundsContour[3]-boundsContour[2])

        # Rescale the contour so that it shares the same bounds as the input data
        transform1 = vtk.vtkTransform()
        transform1.Scale(ratioX, ratioY, 1.0)

        tfilter1 = vtk.vtkTransformPolyDataFilter()
        tfilter1.SetInput(contour)
        tfilter1.SetTransform(transform1)
        tfilter1.Update()

        contour = tfilter1.GetOutput()

        #Translate the contour so that it shares the same center as the input data
        centerContour = [1]*3
        contour.GetCenter(centerContour)
        transX = centerData[0] - centerContour[0]
        transY = centerData[1] - centerContour[1]
        transZ = centerData[2] - centerContour[2]

        transform2 = vtk.vtkTransform()
        transform2.Translate(transX, transY, transZ)

        tfilter2 = vtk.vtkTransformPolyDataFilter()
        tfilter2.SetInput(contour)
        tfilter2.SetTransform(transform2)
        tfilter2.Update()

        contour = tfilter2.GetOutput()

        # Render the result: Input data + resulting silhouette

        # Updating the color of the data
        actorData.GetProperty().SetColor(0.9, 0.9, 0.8)

        # Create a mapper and actor of the silhouette
        mapperContour = vtk.vtkPolyDataMapper()
        mapperContour.SetInput(contour)

        actorContour = vtk.vtkActor()
        actorContour.SetMapper(mapperContour)
        actorContour.GetProperty().SetLineWidth(2.0)

        # 2 renders and a render window
        renderer1 = vtk.vtkRenderer()
        renderer1.AddActor(actorData)

        renderer2 = vtk.vtkRenderer()
        renderer2.AddActor(actorContour)

        self.vtkWidget.GetRenderWindow().AddRenderer(renderer1)
        renderer1.SetViewport(0, 0, 0.5, 1)

        self.vtkWidget.GetRenderWindow().AddRenderer(renderer2)
        renderer2.SetViewport(0.5, 0, 1, 1)
 
        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            self._initialized = True
 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("External Contour example")

    def categories(self):
        return ['Demo']

    def mainClasses(self):
        return ['vtkWindowToImageFilter', 'vtkContourFilter', 'vtkTransformPolyDataFilter']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
