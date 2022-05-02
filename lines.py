import numpy as np

def filter_lines(lines, h, w):
	#collect all the lines in their appropriate location
	x0 = w//2
	y0 = h//2
	l1 = 0
	l2 = 0
	l3 = 0
	h1 = 0
	h2 = 0
	h3 = 0
	vertical1 = []
	vertical2 = []
	vertical3 = []
	horizontal1 = []
	horizontal2 = []
	horizontal3 = []
	for line in lines:
		x1,y1,x2,y2 = line[0]
		if abs(x1 - x2) <= 30:
			line[0][1] = 0
			line[0][3] = h
			x1,y1,x2,y2 = line[0]
			if l1 == 0:
				l1 = x1
				vertical1.append(line[0])

			elif abs(l1 - x1) < 50:
				vertical1.append(line[0])

			elif l2 == 0 and abs(l1 - x1) > w//3:
				l2 = x1
				vertical2.append(line[0])

			elif abs(l2 - x1) < 50 and abs(l1 - x1) > w//3:
				vertical2.append(line[0])

			elif l3 == 0 and abs(l1 - x1) > w//3 and abs(l2 - x1) > w//3:
				l3 = x1
				vertical3.append(line[0])

			elif abs(l3 - x1) < 50 and abs(l1 - x1) > w//3 and abs(l2 - x1) > w//3:
				vertical3.append(line[0])

		elif abs(y1 - y2) <= 30:
			line[0][0] = 0
			line[0][2] = w
			x1,y1,x2,y2 = line[0]
			if h1 == 0:
				h1 = y1
				horizontal1.append(line[0])

			elif abs(h1 - y1) < 50:
				horizontal1.append(line[0])

			elif h2 == 0 and abs(h1 - y1) > w//3:
				h2 = y1
				horizontal2.append(line[0])

			elif abs(h2 - y1) < 50 and abs(h1 - y1) > w//3:
				horizontal2.append(line[0])

			elif h3 == 0 and abs(h1 - y1) > w//3 and abs(h2 - y1) > w//3:
				h3 = y1
				horizontal3.append(line[0])

			elif abs(h3 - y1) < 50 and abs(h1 - y1) > w//3 and abs(h2 - y1) > w//3:
				horizontal3.append(line[0])

	#calculating the average coordinates of the lines for better stability
	average = []
	if len(vertical1) != 0:
		average.append(np.mean(vertical1, axis=0).astype(np.int64))
	if len(vertical2) != 0:
		average.append(np.mean(vertical2, axis=0).astype(np.int64))
	if len(vertical3) != 0:
		average.append(np.mean(vertical3, axis=0).astype(np.int64))
	if len(horizontal1) != 0:
		average.append(np.mean(horizontal1, axis=0).astype(np.int64))
	if len(horizontal2) != 0:
		average.append(np.mean(horizontal2, axis=0).astype(np.int64))
	if len(horizontal3) != 0:
		average.append(np.mean(horizontal3, axis=0).astype(np.int64))

	return average	