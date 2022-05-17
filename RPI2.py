from better_lines import *
# from debugging import *
from utils2 import *
# from lines import *
from QR import *
from polation2 import *
import numpy as np
import cv2 as cv
# import time
#from sqlalchemy.ext.automap import automap_base
#from sqlalchemy.orm import Session
#from sqlalchemy import create_engine
import socket
import time
import threading
from time import sleep
from statistics import mean
#from flask import Flask, render_template, Response, request, redirect, url_for
#from camera import VideoCamera
from threading import Thread
HEADER = 5
PORT = 5000
PORT_2=5050
SERVER ="192.168.3.8" #"192.168.3.9"
SERVER2="10.42.0.2" #"192.168.1.42
FORMAT='utf-8'
DISCONNECT = "end"

ADDR=(SERVER,PORT)
ADDR_2=(SERVER2,PORT_2)
tijd=0
client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server.bind(ADDR)
client_send.connect(ADDR_2)

#Load a video input from file or camera
cap = cv.VideoCapture('Video_6.mov')
status=True


def sendword(msg, client):
	message = msg.encode(FORMAT)
	msg_length = len(message)
	send_length = str(msg_length).encode(FORMAT)
	send_length += b' ' * (HEADER - len(send_length))
	client.send(send_length)
	client.send(message)


def sendnumber(number, client):
	number = str(number)
	message = number.encode(FORMAT)
	msg_length = len(message)
	send_length = str(msg_length).encode(FORMAT)
	send_length += b' ' * (HEADER - len(send_length))
	client.send(send_length)
	client.send(message)


def sendqr(qrstring, client):
	msg_length = len(qrstring)
	send_length = str(msg_length).encode(FORMAT)
	send_length += b' ' * (HEADER - len(send_length))
	client.send(send_length)
	client.send(qrstring)

#check if capture is correct
if not cap.isOpened():
	print("Cannot open file")
	exit()

def IMP(cap, sendsocket):
	# used to record the time when we processed last frame
	prev_frame_time = 0

	# used to record the time at which we processed current frame
	new_frame_time = 0

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
	qr_counter = 0
	square = [0,0]
	mistake = False
	square_counter = 0
	changed = False

	k = 0

	#while loop for entire video
	#capture is correct
	old_coordinate = [0, 0]
	while True:
		#start of the while loop
		# start_while_loop = time.perf_counter()

		#capture frame by frame
		ret, frame = cap.read()

		# if frame is read correctly ret is True
		if not ret:
			print("Can't receive frame (stream end?). Exiting ...")
			break

		#timer of the camera procedures
		# start_camera = time.perf_counter()

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
		resized_full_mask = scale_down_mask(full_mask)
		#end of the camera procedures
		# end_camera = time.perf_counter()
		#start of houghlines and start of lines procedure
		# start_houghlines = time.perf_counter()

		#Use the Hough transformation to calculate lines
		lines = cv.HoughLinesP(resized_full_mask,1,np.pi/180,100,minLineLength=75,maxLineGap=10)

		#end of the houglines
		# end_houglines = time.perf_counter()

		#if there are no lines the while loop is repeated
		if lines is None:
			continue

		#returns a filtered set of lines
		filtered_lines = filter_lines(lines, h, w)

		#end of line procedure
		# end_lines = time.perf_counter()

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

		side_new = None

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
				start_x, start_y, side_new = interpolate(corners, x0, y0, side_old=0)
				coordinate = [abs(start_x), abs(start_y)]
				old_coordinate = coordinate
				side_old = side_new
				start = True

				#overwritting the old points with the current points for next frame calculation
				corners_old = corners

			if mistake == True:
				side_new = calculate_side(corners, side_old)
				corners = check_corners(corners, int(side_new))
				set_corners = set(corners)
				if len(set_corners) < 2 or None in set_corners:
					pass
				else:
					x_est, y_est, side_new = interpolate(corners, x0, y0, side_new)
					coordinate = calc_coord2(old_coordinate, x_est, y_est)
					old_coordinate = coordinate

				#overwritting the old points with the current points for next frame calculation
					corners_old = corners

					if side_new != None:
						side_old = side_new

					mistake = False
		else:
			#new_square checks wether there was a square change
			new_square = None

			#start of linking the points to old corners
			# start_link = time.perf_counter()

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

			#end of linking the corners
			# end_linking = time.perf_counter()

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

			corners = check_corners(corners, int(side_old))

			set_corners = set(corners)
			if len(set_corners) < 2 or None in set_corners:
				mistake = True
			else:
				#start of calculations
				# start_calculations = time.perf_counter()

				#interpolation to calculate the corners
				x_est, y_est, side_new = interpolate(corners, x0, y0, side_old)
				coordinate = calc_coord2(old_coordinate, x_est, y_est)
				old_coordinate = coordinate

				#overwritting the old points with the current points for next frame calculation
				corners_old = corners

				#overwriting the old sides with the new sides for further reference
				if side_new != None:
					side_old = side_new


		#QR code dedection
		#latest_qr is latest scanned qr code

		if qr_counter == 0:
			#start of qr proces
			# start_qr = time.perf_counter()
			decoded = qr(crop)
			qr_counter = 5
			if len(decoded) != 0 and latest_qr != decoded[0][0]:
				latest_qr = decoded[0][0]
				qr_counter = 50
			#end of the qr proces
			# end_qr = time.perf_counter()
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
		# fps = str(fps)

		#end of the process
		# end_frame = time.perf_counter()
		#print(type(end_frame))

		#print statements
		if start == True:
			#print("-----------------------------------------")
			print(round(coordinate[0], 2), round(coordinate[1], 2))
			print(fps)
			#print("-----------------------------------------")
			sendword("imp", sendsocket)
			sendnumber(coordinate[0], sendsocket)
			sendnumber(coordinate[1], sendsocket)

		else:
			# print("-----------------------------------------")
			print("waiting for start square")
			# print("-----------------------------------------")

		k += 1

thread_imp=	Thread(target=IMP,args=(cap, client_send))
thread_imp.start()

#cap.release()
#cv.destroyAllWindows()