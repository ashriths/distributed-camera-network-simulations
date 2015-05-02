__author__ = 'ashrith'

IP = "127.0.0.1"
#IP = '192.168.43.116'

import socket
from threading import Thread
import json
import time
import cv2, math
import numpy as np
from collections import OrderedDict
import time
import datetime

from model.node import Node


BUFFER_SIZE = 1024

class NodeGenerator(Node):
    def __init__(self, network_address, loc):
        self.init_network(network_address, loc)
        #self.init_tracker()

    def init_network(self, network_address,loc):
        Node.__init__(self)
        self.loc = loc
        self.network_address = network_address
        self.neighbor_map = {}
        self.socket = None
        self.ip = IP
        self.listener = Thread(target=self.listen, name = "listen")
        self.heartbeat_generator = Thread(target=self.send_heartbeat, name= "send_heartbeat")
        self.objects = {}
    
    def init_tracker(self):
        cv2.namedWindow("ColourTrackerWindow", cv2.CV_WINDOW_AUTOSIZE)
        self.capture = cv2.VideoCapture(0)

        self.colors = ('red', 'green', 'blue')
        self.present = {'red':{}, 'blue':{}, 'green':{}}
        for key in self.present:
            self.present[key]['present'] = False
            self.present[key]['timestamp'] = None
        self.scale_down = 4
        self.lower = {}
        self.upper = {}
        self.xx = 1
        self.yy = 1

        self.lower['blue'] = np.array([95, 112, 50],np.uint8)
        self.upper['blue'] = np.array([130, 255, 255],np.uint8)

        self.lower['red'] = np.array([160, 120, 80],np.uint8)
        self.upper['red'] = np.array([180, 255, 200],np.uint8)

        self.lower['green'] = np.array([30,127,50],np.uint8)
        self.upper['green'] = np.array([70,255,204],np.uint8)



   
    def printText(self, img, contour, text):
        # text_size,f = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, thickness=2)
        # corner1 = tuple(approx[0][0])
        # corner2 = (approx[0][0][0] + text_size[0] , approx[0][0][1] - text_size[1]  )
        # cv2.rectangle(img,corner1,corner2  , (0,255,0), -1)
        approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True)
        #find top right point
        largest = [10000,10000]
        for coord1 in approx:
            for coord_inner in coord1:
                if largest[0] > coord_inner[0]:
                    largest = coord_inner
        largest[0] -= 10;
        largest[1] -= 10
        M = cv2.moments(contour);
        if M['m00']<10:
            return
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        cv2.circle(img, (cx, cy), 5,(0,100,255) ,thickness=3)
        cv2.putText(img, str(cx) + ", " + str(cy) , (cx+10, cy+10), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,150,255),thickness= 1);
        cv2.putText(img, text , tuple(largest), cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,255),thickness= 2);

    def sorted_contours(self,contours):
        area = {}
        for idx, contour in enumerate(contours):
            area[cv2.contourArea] = contour
        area = OrderedDict(sorted(area.items(), key = lambda t: t[0], reverse = True))
        return area


    def track(self):
        print "tracking Started.."
        while True:
            
            f, orig_img = self.capture.read()
            orig_img = cv2.flip(orig_img, 1)
            base_img = cv2.GaussianBlur(orig_img, (5,5), 0)
            base_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2HSV)
            cv2.imshow("cvtColor",base_img)
            kernel = np.ones((4,4),np.uint8)
            # mask the same image for red, green and blue
            for color in self.colors:
                img = base_img
                binary = cv2.inRange(img, self.lower[color], self.upper[color])
                cv2.imshow("inrange",binary)
                #erode image to remove noise then dilate image to increase pixel thickness
                dilated_img = cv2.dilate(binary,kernel,iterations = 1)
                cv2.imshow("dilation",dilated_img)
                binary = cv2.morphologyEx(dilated_img, cv2.MORPH_OPEN, kernel)
                cv2.imshow("opening",binary)
                contours, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                #sort contours in desc acc to area
                allContours = {}
                for idx, contour in enumerate(contours):
                    allContours[cv2.contourArea(contour)] = contour
                allContours = OrderedDict(sorted(allContours.items(), key = lambda t: t[0], reverse = True))
                i=0
                #plot rectangles for contours
                for key in allContours.iterkeys():
                    if(cv2.contourArea(allContours[key]) <100 or i>1 ):
                        break;

                    self.present[color]['present'] = True
                    timestamp = str (datetime.datetime.utcnow())
                    self.present[color]['timestamp'] = timestamp

                    self.printText(orig_img,allContours[key],color)
                    cv2.drawContours(orig_img,[allContours[key]], 0, (0, 0, 255),2)
                    i+=1;

            cv2.imshow("ColourTrackerWindow", orig_img)
            if cv2.waitKey(10) == 27:
                cv2.destroyWindow("ColourTrackerWindow")
                # cv2.destroyWindow("ColourTrackerWindow2")
                # cv2.destroyWindow("ColourTrackerWindow3")
                # cv2.destroyWindow("bgsub")
                cv2.destroyAllWindows()
                self.capture.release()
            time.sleep(1)
             
            for color in self.present.keys():
                if self.present[color]['present']:
                    if not self.objects.has_key(color):
                        self.objects[color] = {'data':{'history' : []}}
                    if len(self.objects[color]['data']['history'])<1 or not self.objects[color]['data']['history'][-1]['node'] == self.port:
                        self.objects[color]['data']['history'].append({'ts': self.present[color]['timestamp'], 'node' : [self.ip,self.port]})
                    msg = json.dumps({'type': 'object_info', 'data': {'color': color, 'history' : self.objects[color]['data']['history'] }})   
                    print msg
                    self.broadcast_neighbours(msg)
                    
            # color = 'red' # update this line to get me the color of the object from tracker
            # msg = json.dumps({'type': 'object_info', 'data': {'color': color, 'history' : self.objects[color].data.history }})
            # print msg
            #self.broadcast_neighbours()

    def listen(self):
        # find a port that is free for listening and bind my listener
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 5000
        bind = False
        while not bind:
            try:
                # print self.port
                self.socket.bind((self.ip, self.port))
                bind = True
                print("Client created on %s listening to port %s" % (self.ip, self.port))
            except socket.error:
                self.port += 1

        # tell my listening port and address to the network admin
        admin = socket.socket()
        admin.connect(self.network_address)
        admin.send(json.dumps({'type': 'intro', 'data': {'port': self.port, 'ip': self.ip, 'loc': self.loc}}))
        admin.close()
        while True:
            self.socket.listen(5)
            connection, address = self.socket.accept()
            self.process_message(connection.recv(BUFFER_SIZE))

    def process_message(self, msg):
        try:
            message = json.loads(msg)
            if message['type'] == 'admin_broadcast':
                data = message['data']
                print "BROADCAST: %s" % data
            if message['type']== 'neighbor_info':
                data=message['data']
                print data
                self.neighbors = self.neighbors+data
                print "NEIGHBOURS : %s "% self.neighbors
                print "NEIGHBOR INFO: %s" % data
            if message['type'] == 'object_info':
                data = message['data']
                print "OBJECTDATA : %s" % data
                self.objects[data['color']] = data
            if message['type'] == 'heartbeat':
                data = message['data']
                print "HEARTBEAT : %s" % data
            print ""
        except Exception:
            #raise
            print 'Bad Message received: %s' % msg

    def message(self,address, msg):
        try:
            s = socket.socket()
            s.connect(address)
            s.send(msg)
            s.close()
        except Exception:
            print "Cannot reach : %s" % address
            

    def broadcast_neighbours(self, message):
        for node in self.neighbors:
            #print "Broadcast to %s" % node
            self.message((node["ip"],node["port"]),message)

    def send_heartbeat(self):
        while True:
            time.sleep(5)
            self.heartbeat()

    def heartbeat(self):
        self.broadcast_neighbours(json.dumps({'type': 'heartbeat', 'data': {'port': self.port, 'ip': self.ip, 'loc': self.loc}}))


    def stop(self):
        self.listener.terminate()
        #self.tracker.terminate()

    def start(self):
        self.listener.start()
        self.heartbeat_generator.start()
        #self.track()
        




