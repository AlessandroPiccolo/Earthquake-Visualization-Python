# Earthquake visualization in Italy

from vtk import *
import read_CSV_io
import math
from vtk.util.misc import vtkGetDataRoot

# Variables of interest
file = "events3.csv"
year  = "2012"
# Regios of interest
long_Max = 11.793806
long_Min = 10.120710
lat_Max = 44.971109
lat_Min = 44.427205

# Get data (x,y,z and magnitude)
data = vtk.vtkPolyData()
points, scalars = read_CSV_io.read_points_csv(file, year, "TempoOrigine(UTC),Latitudine,Longitudine,Profondita,Magnitudo".split(","), long_Max, long_Min, lat_Max, lat_Min)
data.SetPoints(points) # location
data.GetPointData().SetScalars(scalars) # magnitude

xmi, xma, ymi, yma, zmi, zma = points.GetBounds()

# Creates balls
ball = vtk.vtkSphereSource()
ball.SetRadius(0.25)
ball.SetThetaResolution(15)
ball.SetPhiResolution(8)

ballGlyph = vtk.vtkGlyph3D()
ballGlyph.SetInput(data)
ballGlyph.SetSourceConnection(ball.GetOutputPort())
ballGlyph.SetScaleModeToScaleByScalar()
ballGlyph.SetColorModeToColorByScalar()
ballGlyph.SetScaleFactor(1.0)

# Colors
colorTransferFunction = vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0.0, 0, 0, 0.4)
colorTransferFunction.AddRGBPoint(2.0, 0, 0, 1)
colorTransferFunction.AddRGBPoint(2.5, 0, 0.5, 0.8)
colorTransferFunction.AddRGBPoint(3.0, 0, 0.8, 0.8)
colorTransferFunction.AddRGBPoint(4.0, 0.7, 0.75, 0.45)
colorTransferFunction.AddRGBPoint(4.5, 0.8, 0.8, 0.2)
colorTransferFunction.AddRGBPoint(5.0, 0.85, 0.85, 0)
colorTransferFunction.AddRGBPoint(6.0, 1, 1, 0)

ballMapper = vtkPolyDataMapper()
ballMapper.SetInputConnection(ballGlyph.GetOutputPort())
ballMapper.SetLookupTable(colorTransferFunction)

ballActor = vtkActor()
ballActor.SetMapper(ballMapper)

# Image as background
# Load in the texture map. A texture is any unsigned char image. If it
# is not of this type, you will have to map it through a lookup table
# or by using vtkImageShiftScale
map_png = "map.png"
pngReader = vtk.vtkPNGReader()
pngReader.SetFileName(map_png)
pngReader.Update()
atext = vtk.vtkTexture()
atext.SetInputConnection(pngReader.GetOutputPort())
atext.InterpolateOn()

# # Change image
# iss = vtk.vtkImageShiftScale()
# iss.SetInput( data )
# iss.SetOutputScalarTypeToUnsignedChar()
# iss.SetShift(-a)
# iss.SetScale(255.0/(b-a))
# # Now you use iss.GetOutput() instead
# data2 = iss.GetOutput()


# Create a plane source and actor. The vtkPlanesSource generates
# texture coordinates.
plane = vtk.vtkPlaneSource()
plane.SetOrigin(xmi,ymi,zmi)
plane.SetPoint1(xma,ymi,zmi)
plane.SetPoint2(xmi,yma,zmi)

planeMapper = vtk.vtkPolyDataMapper()
planeMapper.SetInputConnection(plane.GetOutputPort())
planeActor = vtk.vtkActor()
planeActor.SetMapper(planeMapper)
planeActor.SetTexture(atext)
planeActor.GetProperty().SetOpacity(0.5)

#Create an outline of the volume
outline = vtk.vtkOutlineFilter()
outline.SetInput(ballGlyph.GetOutput())
outline_mapper = vtk.vtkPolyDataMapper()
outline_mapper.SetInput(outline.GetOutput())
outline_actor = vtk.vtkActor()
outline_actor.SetMapper(outline_mapper)
outline_actor.GetProperty().SetColor(0.8, 0.8, 0.8) #Define actor properties (color, shading, line width, etc)
outline_actor.GetProperty().SetLineWidth(2.0)

# Create Scalar Bar
scalarBar = vtk.vtkScalarBarActor()
scalarBar.SetLookupTable(ballMapper.GetLookupTable())
scalarBar.SetTitle("Magnitude")
scalarBar.GetLabelTextProperty().SetColor(0,0,1)
scalarBar.GetTitleTextProperty().SetColor(0,0,1)
scalarBar.SetWidth(.12)
scalarBar.SetHeight(.95)

spc = scalarBar.GetPositionCoordinate()
spc.SetCoordinateSystemToNormalizedViewport()
spc.SetValue(0.05,0.05)

# Create a renderer and add the actors to it
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.2, 0.2, 0.2)
renderer.AddActor(outline_actor)
renderer.AddActor(scalarBar)
renderer.AddActor(planeActor)
renderer.AddActor(ballActor)

# renderer.ResetCamera()
# cam1 = renderer.GetActiveCamera()
# cam1.Elevation(-30)
# cam1.Roll(-20)
# renderer.ResetCameraClippingRange()

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.SetWindowName("Earth quake")
render_window.SetSize(500, 500)
render_window.AddRenderer(renderer)

# Create an interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Initialize the interactor and start the rendering loop
interactor.Initialize()
render_window.Render()
interactor.Start()