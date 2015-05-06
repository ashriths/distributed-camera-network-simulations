__author__ = 'ashrith'
import json
import site; site.addsitedir("/usr/local/lib/python2.7/site-packages")
from matplotlib import pyplot as plt
import numpy

file_name = raw_input("Enter File_name:")
if file_name=="":
    file_name="analysis.txt"

file = open(file_name,'r')
history = []
#print file.readlines()
for line in file.readlines():
    l = line.strip("\n")
    try:
        p = json.loads(l)
        history.append(p)
    except Exception:
        pass
object = raw_input("Enter Object Name:")
#print history

if len(history) > 0:
    history = [i for i in history if i['object'] == object]
print len(history), "Entries found to plot"
history.sort(key = lambda d: d['ts'])
x_pts = []
y_pts = []
labels = []
for entry in history:
    x_pts.append(entry['loc'][0])
    y_pts.append(entry['loc'][1])
    labels.append(entry['ts'])
#print x_pts, y_pts, labels
x = numpy.array(x_pts)
y = numpy.array(y_pts)
plt.figure()
q = plt.quiver(x[:-1], y[:-1], x[1:]-x[:-1], y[1:]-y[:-1], scale_units='xy', angles='xy', scale=1)
plt.plot(x_pts,y_pts,marker='o', linestyle='None', label="Trajectory of")
for x,y in zip(x_pts,y_pts):
    plt.annotate("("+str(x)+","+str(y)+")" , xy=(x, y), xytext=(x+0.3, y))

plt.show()

