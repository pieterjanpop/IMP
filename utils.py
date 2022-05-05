import numpy as np
import cv2 as cv
from math import dist

###CAMERA/IMAGE FUNCTIONS###

# Define Camera Matrix
mtx = np.array([[9.975865066475905678e+02, 0.000000000000000000e+00, 2.782246584867496608e+02],
                [0.000000000000000000e+00, 1.004004367713010424e+03, 2.802807082904876665e+02],
                [0.000000000000000000e+00, 0.000000000000000000e+00, 1.000000000000000000e+00]])

# Define distortion coefficients
dist = np.array(
    [-8.300163522364806257e-01, 3.943837308660838037e-01, -1.648646193160172024e-02, 2.217851985394334036e-02,
     1.170058044562844124e+00])

#corrects the frame from the camera
def undistort(frame):
    h, w = frame.shape[:2]
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    dst = cv.undistort(frame, mtx, dist, None, newcameramtx)

    # Cropping the frame
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]
    return dst

def scale_down(frame):
	dim = (300,240)
	resized = cv.resize(frame, dim, interpolation = cv.INTER_NEAREST)

	return resized

def crop_image(frame, h, w):
	crop = frame[h//4:3*(h//4),w//4:3*(w//4)]

	return crop

def dimensions(frame):
	(h, w) = frame.shape[:2]
	x0 = w//2
	y0 = h//2

	return h, w, x0, y0

def mask(frame):
	#Convert BGR to HSV
	hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

	#Red is a color on both sides on the spectrum so we splith the mask in 2 parts
	#lower boundary RED color range values; Hue (0 - 10)
	lower1 = np.array([0, 60, 60])
	upper1 = np.array([30, 255, 255])

	#Upper boundary RED color range values; Hue (160 - 180)
	lower2 = np.array([150, 60, 60])
	upper2 = np.array([180, 255, 255])

	#Threshold the HSV image to get only red colors
	lower_mask = cv.inRange(hsv, lower1, upper1)
	upper_mask = cv.inRange(hsv, lower2, upper2)

	#Combine the 2 mask for full threshold
	full_mask = cv.add(lower_mask, upper_mask)

	return full_mask

###UTILITIES FUNCTIONS###

#checks all lines in average for intersection points
def points_intersection(average, h, w):
	intersection = []
	for i in range(0,len(average) - 1):
		for n in range(i+1, len(average)):
			intersection_point = line_intersection(average[i], average[n])
			if intersection_point != None and (0 < intersection_point[0] < w) and (0 < intersection_point[1] < h):
				intersection.append(intersection_point)

	return(intersection)

#calculations made based on two lines
def line_intersection(line1, line2):
	xdiff = (line1[0] - line1[2], line2[0] - line2[2])
	ydiff = (line1[1] - line1[3], line2[1] - line2[3])

	def det(a, b):
		return a[0] * b[1] - a[1] * b[0]

	div = det(xdiff, ydiff)
	if div == 0:
		return None	

	x1,y1,x2,y2 = line1
	line1 = [(x1,y1),(x2,y2)]
	x1,y1,x2,y2 = line2
	line2 = [(x1,y1),(x2,y2)]
	d = (det(*line1), det(*line2))
	x = round(det(d, xdiff) / div)
	y = round(det(d, ydiff) / div)
	return (x, y)

#calculates the sides of the square
def calculate_side(intersection, xside_old, yside_old):
	x = 0
	y = 0
	xside = 0
	yside = 0
	for i in range(0, len(intersection) - 1):
		for n in range(1, len(intersection)):
			if abs(intersection[i][1] - intersection[n][1]) < 25 and abs(intersection[i][0] - intersection[n][0]) < xside_old * 1.5:
				xside += abs(intersection[i][0] - intersection[n][0])
				x += 1
			elif abs(intersection[i][0] - intersection[n][0]) < 25 and abs(intersection[i][1] - intersection[n][1]) < yside_old * 1.5:
				yside += abs(intersection[i][1] - intersection[n][1])
				y += 1
	if xside == 0:
		xside = None
	else:
		xside /= x

	if yside == 0:
		yside = None
	else:
		yside /= y

	return xside, yside

#0: left_top
#1: left_bottom
#2: right_top
#3: right_bottom
def sort_corners(points, x0, y0):
	sorted_points = [(0,0), (0,0), (0,0), (0,0)]
	for point in points:
		if point[0] >= x0 and point[1] >= y0:
			if distance_to_center(point, sorted_points[3], x0, y0):
				sorted_points[3] = point
		elif point[0] >= x0 and point[1] < y0:
			if distance_to_center(point, sorted_points[2], x0, y0):
				sorted_points[2] = point
		elif point[0] < x0 and point[1] >= y0:
			if distance_to_center(point, sorted_points[1], x0, y0):
				sorted_points[1] = point
		elif point[0] < x0 and point[1] < y0:
			if distance_to_center(point, sorted_points[0], x0, y0):
				sorted_points[0] = point

	return sorted_points

def distance_to_center(point1, point2, x0, y0):
	if point2 == (0,0):
		return True
	else:
		print(point1)
		distance_1 = abs(point1[0] - x0) + abs(point1[1] - y0)
		distance_2 = abs(point2[0] - x0) + abs(point2[1] - y0)
		if distance_1 < distance_2:
			return True
		else:
			return False