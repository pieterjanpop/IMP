from utils import *
from better_lines import *
from QR import *
from polation import *
from numpy import pi
import cv2 as cv
import time

start_time = time.perf_counter()
#Load a video input from file or camera
cap = cv.VideoCapture('Video_5.mov')

#check if capture is correct
if not cap.isOpened():
	print("Cannot open file")
	exit()

# used to record the time when we processed last frame
prev_frame_time = 0
 
# used to record the time at which we processed current frame
new_frame_time = 0

#latest qr code
latest_qr = None

#initiate coordinate
coordinate = "fail"

#plot values
xval = []
yval = []

#parameters for code:
# start: used for the start of the algorithm on the first frame, after that it is always False
# changed: used to check if square changed and to stop false double incrementations
# counter: ^^
# qr_changed: To check if the drone reached new qr code
start = False
changed = False
square_counter = 0
qr_counter = 0
square = [0,0]
mistake = False

k = 0

#while loop for entire video
#capture is correct
timer = True
while True:
	#start of the while loop
	start_while_loop = time.perf_counter()

	#capture frame by frame
	ret, frame = cap.read()

	# if frame is read correctly ret is True
	if not ret:
		print("Can't receive frame (stream end?). Exiting ...")
		break
	
	#timer of the camera procedures
	start_camera = time.perf_counter()

	#dimensions of the original feed
	h, w, x0, y0 = dimensions(frame)

	#the image is cropped to speed up the QR code detection
	crop = crop_image(frame, h ,w)

	#Resize it to a standard frame of 300x240
	resized = scale_down(frame)

	#Calculate the center of the frame as reference point
	h, w, x0, y0 = dimensions(resized)

	#create the mask of red line detection
	full_mask = mask(resized)

	#end of the camera procedures
	end_camera = time.perf_counter()
	#start of houghlines and start of lines procedure
	start_houghlines = time.perf_counter()

	resized_full_mask = scale_down_mask(full_mask)
	#Use the Hough transformation to calculate lines
	lines = cv.HoughLinesP(resized_full_mask,1,pi/180,100,minLineLength=75,maxLineGap=10)

	#end of the houglines
	end_houglines = time.perf_counter()

	#if there are no lines the while loop is repeated
	if lines is None:
		continue

	#returns a filtered set of lines
	filtered_lines = filter_lines(lines, h, w)

	#end of line procedure
	end_lines = time.perf_counter()

	#Calculate the intersections of the lines
	intersection = points_intersection(filtered_lines, h, w)
	if intersection is None:
		continue

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

	if start == False or mistake == True:
		intersection = sort_corners(intersection, x0, y0)
		for point in intersection:
			if point == (0,0):
				pass
			elif point[0] >= x0 and point[1] >= y0:
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
		elif mistake == False:
			#start calculation 
			start_x, start_y, length_side_x, length_side_y = interpolate(corners, x0, y0)
			coordinate = [abs(start_x), abs(start_y)]
			xside_old = length_side_x
			yside_old = length_side_y
			start = True

			#overwritting the old points with the current points for next frame calculation
			corners_old = corners

		if mistake == True:
			corners = check_corners(corners, xside_old, yside_old)
			x_est, y_est, xside_new, yside_new = interpolate(corners, x0, y0)
			coordinate = calculate_coordinate(square, x_est, y_est)

			#overwritting the old points with the current points for next frame calculation
			corners_old = corners

			if xside_new != None:
				xside_old = xside_new
			if yside_new != None:
				yside_old = yside_new

			#adding the coordinate values for the plot
			if coordinate != "fail":
				xval.append(coordinate[0])
				yval.append(coordinate[1])

			mistake = False
	else:
		#new_square checks wether there was a square change
		new_square = None

		#start of linking the points to old corners
		start_link = time.perf_counter()

		#link the new points to the old labelled corners
		for point in intersection:
			if corners_old[0] != None and abs(point[0] - corners_old[0][0]) < 40 and abs(point[1] - corners_old[0][1]) < 40:
				if point[0] > x0 + 10:
					new_square = "left"
				elif point[1] > y0 + 10:
					new_square = "up"

				corners[0] = point

			elif corners_old[1] != None and abs(point[0] - corners_old[1][0]) < 40 and abs(point[1] - corners_old[1][1]) < 40:
				if point[0] > x0 + 10:
					new_square = "left"
				elif point[1] < y0 - 10:
					new_square = "down"

				corners[1] = point

			elif corners_old[2] != None and abs(point[0] - corners_old[2][0]) < 40 and abs(point[1] - corners_old[2][1]) < 40:
				if point[0] < x0 - 10:
					new_square = "right"
				elif point[1] > y0 + 10:
					new_square = "up"

				corners[2] = point

			elif corners_old[3] != None and abs(point[0] - corners_old[3][0]) < 40 and abs(point[1] - corners_old[3][1]) < 40:
				if point[0] < x0 - 10:
					new_square = "right"
				elif point[1] < y0 - 10:
					new_square = "down"

				corners[3] = point

		#end of linking the corners
		end_linking = time.perf_counter()

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
		if len(set_corners) < 2:	
			mistake = True
		else:
			#start of calculations
			start_calculations = time.perf_counter()

			#interpolation to calculate the corners
			x_est, y_est, xside_new, yside_new = interpolate(corners, x0, y0)
			coordinate = calculate_coordinate(square, x_est, y_est)

			#overwritting the old points with the current points for next frame calculation
			corners_old = corners

			#overwriting the old sides with the new sides for further reference
			if xside_new != None and abs(xside_new - xside_old) < 30:
				xside_old = xside_new
			if yside_new != None and abs(yside_new - yside_old) < 30:
				yside_old = yside_new

			#adding the coordinate values for the plot
			if coordinate != "fail":
				xval.append(coordinate[0])
				yval.append(coordinate[1])

	#QR code dedection
	#latest_qr is latest scanned qr code
	if qr_counter == 0:
		#start of qr proces
		start_qr = time.perf_counter()
		decoded = qr(crop)
		qr_counter = 5
		if len(decoded) != 0 and latest_qr != decoded[0][0]:
			latest_qr = decoded[0][0]
			qr_counter = 50
		#end of the qr proces
		end_qr = time.perf_counter()
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

	# converting the fps to string so that we can display it on frame
	# by using putText function
	fps = str(fps)

	#end of the process
	end_frame = time.perf_counter()

	#print statements
	if start == True:
		print("-----------------------------------------")
		print(round(coordinate[0], 2), round(coordinate[1], 2))
		print(square)
		print(fps)
		print("-----------------------------------------")

	else:
		print("-----------------------------------------")
		print("waiting for start square")
		print("-----------------------------------------")

	if timer == True and k > 5:
		global_time = end_frame - start_while_loop
		camera_time = end_camera - start_camera
		hougline_time = end_houglines - start_houghlines
		line_time = end_lines - end_houglines
		total_line_time = hougline_time + line_time
		linking_time = end_linking - start_link
		calculation_time = end_frame - start_calculations
		
		frame_data = f'Frame {k}\n\nGlobal time: {global_time}\nCamera time: {camera_time}\nHoughline time: {hougline_time}\nLine time: {line_time}\nTotal time lines: {total_line_time}\nLinking time: {linking_time}\nCalculation time: {calculation_time}\n\nEnd of frame {k}\n\n'
		with open('output.txt', 'a') as output:
			output.write(frame_data)

	k += 1

print(xval)
print(yval)
cap.release()
cv.destroyAllWindows()