__author__ = 'ashrith'

from lib.node_generator import NodeGenerator
import sys
network_ip = raw_input("Enter Network IP:")
if network_ip == "":
    network_ip = "127.0.0.1"

network_port = raw_input("Enter Network PORT:")
if network_port == "":
    network_port = "5000"
network_port = int(network_port)
print "Enter Location:"
loc_x = int(raw_input("x :"))
loc_y = int(raw_input("y :"))
node = NodeGenerator((network_ip, network_port), (loc_x,loc_y))

while True:
    print "[1] to start"
    print "[2] to stop"
    c = raw_input()
    if c == '1':
        node.start()
    if c == '2':
        sys.exit(0)