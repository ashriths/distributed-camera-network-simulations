__author__ = 'ashrith'
import site; site.addsitedir("/usr/local/lib/python2.7/site-packages")
from matplotlib import pyplot as plt
import numpy as np
from numpy.random import normal, uniform
import pylab as P
import random
def dist(no_nodes, time):
    data = []
    for i in range(time):
        data.append(no_nodes*no_nodes*2*i*random.uniform(0.8,1.2))
    return data

def cent(no_nodes, time):
    data= []
    for i in range(time):
        data.append(no_nodes*no_nodes*no_nodes*i*random.uniform(0.8,1.2))
    return data

no_nodes = int(raw_input("Enter Number of Nodes to simulate: "))
time = int(raw_input("Enter duration to monitor in seconds"))

data_dist = dist(no_nodes, time)
data_cent = cent(no_nodes, time)


N = 5
menMeans = tuple(data_cent)
print menMeans
ind = np.arange(time)  # the x locations for the groups
width = 0.35       # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(ind, menMeans, width, color='r')

womenMeans = tuple(data_dist)

rects2 = ax.bar(ind+width, womenMeans, width, color='y')

# add some text for labels, title and axes ticks
ax.set_ylabel('Data (in kb)')
ax.set_title('Time')

ax.legend( (rects1[0], rects2[0]), ('Centralized', 'Distributed') )


plt.show()