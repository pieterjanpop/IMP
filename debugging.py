from matplotlib import pyplot as plt
from math import floor, ceil
import numpy as np
import cv2 as cv

def draw_coordinates(xval, yval):
	colors = ['blue']
	colors *= len(xval)
	colors[-1] = 'red'
	colors[-2] = 'orange'

	#plt.plot(xval, yval, color='red', linestyle='dashed', linewidth = 1)
	plt.scatter(xval, yval, s=1, color=colors, marker='+')

	# changing the tick of the axis
	min_x, max_x, min_y, max_y = boundaries(xval, yval)
	plt.xticks(np.arange(min_x - 1, max_x + 1, 1.0))
	plt.yticks(np.arange(min_y - 1, max_y + 1, 1.0))

	# naming the x axis
	plt.xlabel('x - axis')
	# naming the y axis
	plt.ylabel('y - axis')
		
	# giving a title to my graph
	plt.title('Flight of the drone')

	# adding the grid
	plt.grid()

	# function to show the plot
	plt.show()

def boundaries(xval, yval):

	min_x = floor(min(xval) + 100) - 100
	max_x = ceil(max(xval) + 100) - 100

	min_y = floor(min(yval) + 100) - 100
	max_y = ceil(max(yval) + 100) - 100

	return min_x, max_x, min_y, max_y

def draw_fps(fpsval):

	# make x-data
	x = np.linspace(0, len(fpsval), len(fpsval))

	# plot
	fig, ax = plt.subplots()

	ax.plot(x, fpsval, linewidth=2.0)

	plt.show()