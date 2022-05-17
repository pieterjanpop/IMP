#link the new intersection points to old intersection points
#0: left_top
#1: left_bottom
#2: right_top
#3: right_bottom

#check wich corners we dont have
def check_corners(corners, side):
	for index in range(0,len(corners)):
		if corners[index] == None:
			corners[index] = make_corners(corners, index, side)
	return corners

#creates the corners we dont have to make the full square
def make_corners(corners, index, side):
	n = 0
	for point in corners:
		if point != None:
			if index == 0:
				if n == 1:
					new_point = (point[0], point[1] - side)
					return new_point
				elif n == 2:
					new_point = (point[0] - side, point[1])
					return new_point
				elif n == 3:
					new_point = (point[0] - side, point[1] - side)
					return new_point
			elif index == 1:
				if n == 0:
					new_point = (point[0], point[1] + side)
					return new_point
				elif n == 2:
					new_point = (point[0] - side, point[1] + side)
					return new_point
				elif n == 3:
					new_point = (point[0] - side, point[1])
					return new_point
			elif index == 2:
				if n == 0:
					new_point = (point[0] + side, point[1])
					return new_point
				if n == 1:
					new_point = (point[0] + side, point[1] - side)
					return new_point
				if n == 3:
					new_point = (point[0], point[1] - side)
					return new_point
			elif index == 3:
				if n == 0:
					new_point = (point[0] + side, point[1] + side)
					return new_point
				if n == 1:
					new_point = (point[0] + side, point[1])
					return new_point
				if n == 2:
					new_point = (point[0], point[1] + side)
					return new_point

		else:
			n += 1

def interpolate(corners, x0, y0, side_old):
	x_values = []
	y_values = []
	for point in corners:
		x_values.append(point[0])
		y_values.append(point[1])
	
	if len(x_values) > 1:
		x_norm = max(x_values) - min(x_values)
	else:
		x_norm = side_old
	if len(y_values) > 1:
		y_norm = max(y_values) - min(y_values)
	else:
		y_norm = side_old

	norm = (x_norm + y_norm) / 2

	x_delta = x0 - min(x_values)
	y_delta = max(y_values) - y0

	x_est = x_delta / norm
	y_est = y_delta / norm

	return x_est, y_est, norm