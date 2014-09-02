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
 
        g = vtk.vtkMutableDirectedGraph()
        v1 = g.AddVertex()
        v2 = g.AddVertex()
        v3 = g.AddVertex()

        ### g.AddEdge(v1, v2)
        g.AddGraphEdge(v1, v2)
        g.AddGraphEdge(v2, v3)
        g.AddGraphEdge(v3, v1)

        # Do layout manually before handing graph to the view.
        # This allows us to know the positions of edge arrows.
        graphLayoutView = vtk.vtkGraphLayoutView()

        layout = vtk.vtkGraphLayout()
        strategy = vtk.vtkSimple2DLayoutStrategy()
        layout.SetInput(g)
        layout.SetLayoutStrategy(strategy)

        # Tell the view to use the vertex layout we provide
        graphLayoutView.SetLayoutStrategyToPassThrough()
        # The arrows will be positioned on a straight line between two
        # vertices so tell the view not to draw arcs for parallel edges
        graphLayoutView.SetEdgeLayoutStrategyToPassThrough()

        # Add the graph to the view. This will render vertices and edges,
        # but not edge arrows.
        graphLayoutView.AddRepresentationFromInputConnection(layout.GetOutputPort())

        # Manually create an actor containing the glyphed arrows.
        graphToPoly = vtk.vtkGraphToPolyData()
        graphToPoly.SetInputConnection(layout.GetOutputPort())
        graphToPoly.EdgeGlyphOutputOn()

        # Set the position (0: edge start, 1:edge end) where
        # the edge arrows should go.
        graphToPoly.SetEdgeGlyphPosition(0.98)

        # Make a simple edge arrow for glyphing.
        arrowSource = vtk.vtkGlyphSource2D()
        arrowSource.SetGlyphTypeToEdgeArrow()
        arrowSource.SetScale(0.1)
        arrowSource.Update()

        # Use Glyph3D to repeat the glyph on all edges.
        arrowGlyph = vtk.vtkGlyph3D()
        arrowGlyph.SetInputConnection(0, graphToPoly.GetOutputPort(1))
        arrowGlyph.SetInputConnection(1, arrowSource.GetOutputPort())

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(arrowGlyph.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
 
        self.ren.AddActor(actor)
        self.ren.ResetCamera()

        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            #self.startTimer(30)
            self._initialized = True

    def timerEvent(self, evt):
        self.ren.GetActiveCamera().Azimuth(1)
        self.vtkWidget.GetRenderWindow().Render()
 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Visualize Directed Graph")

    def categories(self):
        return ['demo']

    def mainClasses(self):
        return ['vtkGlyph3D', 'vtkMutableDirectedGraph']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
