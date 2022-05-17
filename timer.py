import matplotlib.pyplot as plt

global_time = 0
camera_time = 0
hougline_time = 0
line_time = 0
total_line_time = 0
linking_time = 0
calculation_time = 0
frame = 0

with open('output.txt') as output:
    for line in output:
        words_in_line = line.split()
        if 'Global' in words_in_line:
            global_time += float(words_in_line[-1])
        elif 'Camera' in words_in_line:
            camera_time += float(words_in_line[-1])
        elif 'Houghline' in words_in_line:
            hougline_time += float(words_in_line[-1])
        elif 'Line' in words_in_line:
            line_time += float(words_in_line[-1])
        elif 'Total' in words_in_line:
            total_line_time += float(words_in_line[-1])
        elif 'Linking' in words_in_line:
            linking_time += float(words_in_line[-1])
        elif 'Calculation' in words_in_line:
            calculation_time += float(words_in_line[-1])
        elif 'Frame' in words_in_line:
            frame = words_in_line[-1]

fraction_camera = round((camera_time / global_time) * 100, 2) 
fraction_hougline = round((hougline_time / global_time) * 100, 2)
fraction_line = round((line_time / global_time) * 100, 2)
fraction_total = round((total_line_time / global_time) * 100, 2)
fraction_linking = round((linking_time / global_time) * 100, 2)
fraction_calculation = round((calculation_time / global_time) * 100, 2)

average_houghlines = hougline_time / float(frame)
print(average_houghlines)

# Pie chart, where the slices will be ordered and plotted counter-clockwise:
labels = 'Camera', 'Houghline', 'Line', 'Linking', 'calculation'
sizes = [fraction_camera, fraction_hougline, fraction_line, fraction_linking, fraction_calculation]
explode = (0, 0, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

plt.show()