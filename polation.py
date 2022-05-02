#link the new intersection points to old intersection points
#0: left_top
#1: left_bottom
#2: right_top
#3: right_bottom

#check wich corners we dont have
def check_corners(corners, xside, yside):
	for index in range(0,len(corners)):
		if corners[index] == None:
			corners[index] = make_corners(corners, index, xside, yside)
	return corners

#creates the corners we dont have to make the full square
def make_corners(corners, index, xside, yside):
	n = 0
	for point in corners:
		if point != None:
			if index == 0:
				if n == 1:
					new_point = (point[0], point[1] - yside)
					return new_point
				elif n == 2:
					new_point = (point[0] - xside, point[1])
					return new_point
				elif n == 3:
					new_point = (point[0] - xside, point[1] - yside)
					return new_point
			elif index == 1:
				if n == 0:
					new_point = (point[0], point[1] + yside)
					return new_point
				elif n == 2:
					new_point = (point[0] - xside, point[1] + yside)
					return new_point
				elif n == 3:
					new_point = (point[0] - xside, point[1])
					return new_point
			elif index == 2:
				if n == 0:
					new_point = (point[0] + xside, point[1])
					return new_point
				if n == 1:
					new_point = (point[0] + xside, point[1] - yside)
					return new_point
				if n == 3:
					new_point = (point[0], point[1] - yside)
					return new_point
			elif index == 3:
				if n == 0:
					new_point = (point[0] + xside, point[1] + yside)
					return new_point
				if n == 1:
					new_point = (point[0] + xside, point[1])
					return new_point
				if n == 2:
					new_point = (point[0], point[1] + yside)
					return new_point

		else:
			n += 1

def interpolate(corners, x0, y0):
	x_values = []
	y_values = []
	for point in corners:
		x_values.append(point[0])
		y_values.append(point[1])
	
	x_norm = max(x_values) - min(x_values)
	y_norm = max(y_values) - min(y_values)

	x_delta = x0 - min(x_values)
	y_delta = max(y_values) - y0

	x_est = x_delta / x_norm
	y_est = y_delta / y_norm

	return x_est, y_est, x_norm, y_norm