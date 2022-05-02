from utils import *
from lines import *
from QR import *
from polation import *
from debugging import *
import numpy as np
import cv2 as cv
import time
from matplotlib import pyplot as plt

#Load a video input from file or camera
cap = cv.VideoCapture('3.avi')

#check if capture is correct
if not cap.isOpened():
	print("Cannot open file")
	exit()

# used to record the time when we processed last frame
prev_frame_time = 0
 
# used to record the time at which we processed current frame
new_frame_time = 0

#plot values
xval = []
yval = []
fpsval = []
xsquareval = []
ysquareval = []

#latest qr code
latest_qr = None

#initiate coordinate
coordinate = "fail"

#parameters for code:
# start: used for the start of the algorithm on the first frame, after that it is always False
# changed: used to check if square changed and to stop false double incrementations
# counter: ^^
# qr_changed: To check if the drone reached new qr code
start = False
changed = False
square_counter = 0
qr_counter = 0

#while loop for entire video
#capture is correct
while True:
	#capture frame by frame
	ret, frame = cap.read()

	# if frame is read correctly ret is True
	if not ret:
		print("Can't receive frame (stream end?). Exiting ...")
		break

	#Calculate the center of the frame as reference point
	h, w, x0, y0 = dimensions(frame)

	#Resize it to a standard frame of 300x240
	resized = scale_down(frame)

	#crop the frame to select the the QR code out of the image
	crop = crop_image(frame, h ,w)

	#create the mask of red line detection
	full_mask = mask(frame)

	#Bitwise-AND mask and original frame
	result = cv.bitwise_and(frame, frame, mask= full_mask)

	#Use the Hough transformation to calculate lines
	lines = cv.HoughLinesP(full_mask,1,np.pi/180,100,minLineLength=100,maxLineGap=10)
	if lines is None:
		continue

	#returns a filtered set of lines
	filtered_lines = filter_lines(lines, h, w)

	#Drawing the filtered lines as a square
	for line in filtered_lines:
		x1,y1,x2,y2 = line
		cv.line(result,(x1,y1),(x2,y2),(0,0,255),2)

	#Calculate the intersections of the lines
	intersection = sorted(points_intersection(filtered_lines, h, w))

	#start of the program
	#left_bottom corner of the first square is the start position of the grid
	#left_bottom = (0,0)
	#Initialize new points so they are always None at start of frame
	#0: left_top
	#1: left_bottom
	#2: right_top
	#3: right_bottom
	corners = [None,None,None,None]

	xside_new = None
	yside_new = None

	if start == False:
		for point in intersection:
			if point[0] >= x0 and point[1] >= y0:
				corners[3] = point
			elif point[0] >= x0 and point[1] < y0:
				corners[2] = point
			elif point[0] < x0 and point[1] >= y0:
				corners[1] = point
			elif point[0] < x0 and point[1] < y0:
				corners[0] = point

		set_corners = set(corners)
		if None in set_corners:
			pass
		else:
			#start calculation 
			start_x, start_y, length_side_x, length_side_y = interpolate(corners, x0, y0)
			coordinate = [abs(start_x), abs(start_y)]
			square = [0,0]
			xside_old = length_side_x
			yside_old = length_side_y
			start = True

			#overwritting the old points with the current points for next frame calculation
			corners_old = corners
	else:
		#new_square checks wether there was a square change
		new_square = None

		#link the new points to the old labelled corners
		for point in intersection:
			if corners_old[0] != None and abs(point[0] - corners_old[0][0]) < 50 and abs(point[1] - corners_old[0][1]) < 50:
				if point[0] > x0 + 10:
					new_square = "left"
				elif point[1] > y0 + 10:
					new_square = "up"

				corners[0] = point

			elif corners_old[1] != None and abs(point[0] - corners_old[1][0]) < 50 and abs(point[1] - corners_old[1][1]) < 50:
				if point[0] > x0 + 10:
					new_square = "left"
				elif point[1] < y0 - 10:
					new_square = "down"

				corners[1] = point

			elif corners_old[2] != None and abs(point[0] - corners_old[2][0]) < 50 and abs(point[1] - corners_old[2][1]) < 50:
				if point[0] < x0 - 10:
					new_square = "right"
				elif point[1] > y0 + 10:
					new_square = "up"

				corners[2] = point

			elif corners_old[3] != None and abs(point[0] - corners_old[3][0]) < 50 and abs(point[1] - corners_old[3][1]) < 50:
				if point[0] < x0 - 10:
					new_square = "right"
				elif point[1] < y0 - 10:
					new_square = "down"

				corners[3] = point

		#check if square changed last frame to advoid false double incrementations 
		if changed == True:
			square_counter += 1
			if square_counter > 2:
				changed = False
				square_counter = 0
		elif new_square == "left":
			square[0] -= 1
			changed = True
			order = [2, 3, 0, 1]
			corners = [corners[i] for i in order]
			remove_at_index = [0, 1]
			for index in remove_at_index:
				corners[index] = None
		elif new_square == "right":
			square[0] += 1
			changed = True
			order = [2, 3, 0, 1]
			corners = [corners[i] for i in order]
			remove_at_index = [2, 3]
			for index in remove_at_index:
				corners[index] = None
		elif new_square == "up":
			square[1] += 1
			changed = True
			order = [1, 0, 3, 2]
			corners = [corners[i] for i in order]
			remove_at_index = [0, 2]
			for index in remove_at_index:
				corners[index] = None
		elif new_square == "down":
			square[1] -= 1
			changed = True
			order = [1, 0, 3, 2]
			corners = [corners[i] for i in order]
			remove_at_index = [1, 3]
			for index in remove_at_index:
				corners[index] = None

		corners = check_corners(corners, xside_old, yside_old)
		set_corners = set(corners)
		if None in set_corners:
			for point in intersection:
				if corners[3] == None and point[0] >= x0 and point[1] >= y0:
					corners[3] = point
					cv.circle(result,(point[0],point[1]), 5, (0,0,255), -1)
				elif corners[2] == None and point[0] >= x0 and point[1] < y0:
					corners[2] = point
					cv.circle(result,(point[0],point[1]), 5, (0,0,255), -1)
				elif corners[1] == None and point[0] < x0 and point[1] >= y0:
					corners[1] = point
					cv.circle(result,(point[0],point[1]), 5, (0,0,255), -1)
				elif corners[0] == None and point[0] < x0 and point[1] < y0:
					corners[0] = point
					cv.circle(result,(point[0],point[1]), 5, (0,0,255), -1)

		x_est, y_est, xside_new, yside_new = interpolate(corners, x0, y0)
		coordinate = [0,0]
		if square[0] == 0:
			coordinate[0] = x_est
		elif square[0] > 0:
			coordinate[0] = square[0] + x_est
		else:
			coordinate[0] = - (abs(square[0]) - x_est)
		if square[1] == 0:
			coordinate[1] = y_est
		elif square[1] > 0:
			coordinate[1] = square[1] + y_est
		else:
			coordinate[1] = - (abs(square[1]) - y_est)

		for corner in corners_old:
			if corner != None:
				cv.circle(result,(corner[0],corner[1]), 15, (0,255,0), -1)

		#overwritting the old points with the current points for next frame calculation
		corners_old = corners
		for corner in corners:
			if corner != None:
				cv.circle(result,(corner[0],corner[1]), 5, (255,255,255), -1)

		if xside_new != None:
			xside_old = xside_new
		if yside_new != None:
			yside_old = yside_new

		#adding the coordinate values for the plot
		if coordinate != "fail":
			xval.append(coordinate[0])
			yval.append(coordinate[1])

	#QR code dedection
	#latest_qr is latest scanned qr code
	if qr_counter == 0:
		decoded = qr(crop)
		print(decoded)
		qr_counter = 100
		if len(decoded) != 0 and latest_qr != decoded[0][0]:
			latest_qr = decoded[0][0]
	else:
		qr_counter -= 1

	# time when we finish processing for this frame
	new_frame_time = time.time()

	# Calculating the fps
	# fps will be number of frame processed in given time frame
	# since their will be most of time error of 0.001 second
	# we will be subtracting it to get more accurate result
	fps = 1/(new_frame_time-prev_frame_time)
	prev_frame_time = new_frame_time

	# converting the fps into integer
	fps = int(fps)

	# collect all the fps values
	fpsval.append(fps)

	# converting the fps to string so that we can display it on frame
	# by using putText function
	fps = str(fps)
	
	#print statements
	if start == True:
		print("-----------------------------------------")
		print(round(coordinate[0], 2), round(coordinate[1], 2))
		print(square)
		#print(fps)
		print("-----------------------------------------")
		cv.circle(result,(x0,y0), 5, (255,255,255), -1)

	else:
		print("-----------------------------------------")
		print("waiting for start square")
		print("-----------------------------------------")

	#Adding 2 more channels on the mask so we can stack it
	full_mask_3 = cv.cvtColor(full_mask, cv.COLOR_GRAY2BGR)

	#stacking 
	stacked = np.hstack((full_mask_3,frame,result))

	#Displays the result
	cv.imshow('Result',cv.resize(stacked,None,fx=0.8,fy=0.8))
	k = cv.waitKey(0) & 0xFF
	if k == 27:
		break
	if len(xval) > 2 and len(yval) > 2:
		draw_coordinates(xval, yval)
		#draw_fps(fpsval)

cap.release()
cv.destroyAllWindows()