
import csv
import re
from collections import namedtuple
import vtk
import string
import math

# Computes distance in Kilometers
def distance(lat1, lon1, lat2, lon2):
	R = 6371
	dLat = math.radians(lat2-lat1)
	dLon = math.radians(lon2-lon1)
	lat1 = math.radians(lat1)
	lat2 = math.radians(lat2)

	a = math.sin(dLat/2.0) * math.sin(dLat/2.0) + math.sin(dLon/2.0) * math.sin(dLon/2.0) * math.cos(lat1) * math.cos(lat2) 
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) 
	d = R * c
	return d


def read_points_csv(file, year, columns, long_Max, long_Min, lat_Max, lat_Min, type_name="Row"):
	"""Reads coordinates and magnitude from an CSV-file """
	file = open(file) # Open file
	
	# Create tuple
	try:
		row_type = namedtuple(type_name, columns)
	except ValueError:
		row_type = tuple
	rowsR = csv.reader(file, delimiter=';')
	rows = iter(rowsR)
	header = rows.next()
	mapping = [header.index(x) for x in columns]
	
	# To return
	points = vtk.vtkPoints() # create array of Points
	scalars = vtk.vtkFloatArray() # array of scalars
	#time = vtk.vtkFloatArray()
	
	LatMax = 0
	LatMin = 360
	LonMax = 0
	LonMin = 360
	
	for row in rows:
		row = row_type([row[i] for i in mapping])
		if year in row[0]:
			x, y = float(row[1]), float(row[2])
			
			# Compute the extremity of the locations
			if x > LatMax:
				LatMax = x
			if x < LatMin:
				LatMin = x
			if y > LonMax:
				LonMax = y
			if y < LonMin:
				LonMin = y			
			
			if (long_Max > y and long_Min < y and lat_Max > x and lat_Min < x):
				z = float(row[3])
				points.InsertNextPoint(x, y, z)
				magnitude = re.findall("\d+.\d+", row[4])
				magnitude = float(magnitude[0])
				scalars.InsertNextValue(magnitude)
				#t = float(row[0])  # t ar ingen float (behover dock inte den riktigt)
				#time.InsertNextValue(t)
				
	# Compute the range of the data using the distance function
	x1 = distance(LatMin,LonMin,LatMax,LonMin)
	x2 = distance(LatMin,LonMax,LatMax,LonMax)
	y1 = distance(LatMin,LonMin,LatMin,LonMax)
	y2 = distance(LatMax,LonMin,LatMax,LonMax)

	# Adjust the location (points) to kilometers relative to the origin (LatMin, LonMin) instead of latitude and longitude
	xx = x1
	l = points.GetNumberOfPoints()
	i = 0
	while i < l:
		x,y,z = points.GetPoint(i)
		u = (x-LatMin)/(LatMax-LatMin)
		x = (x-LatMin)/(LatMax-LatMin)*xx

		yy = (1-u)*y1+u*y2
		y = (y-LonMin)/(LonMax-LonMin)*yy

		points.SetPoint(i,x,y,z)
		i = i+1
				
				
	return points, scalars #time