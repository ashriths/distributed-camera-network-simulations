__author__ = 'ashrith'

IP = "127.0.0.1"
IP = '192.168.43.116'
#IP = '192.168.30.107'

TRACK = True

ORB_VALUE = 400
MATCH_PER_FRAME = 20

FRAMES = 20
MATCH_PER_RUN = 300

ANALYSIS_FILE = 'analysis.txt'

import site; site.addsitedir("/usr/local/lib/python2.7/site-packages")
import socket
from threading import Thread
import json
import time
import cv2, math
import numpy as np
import scipy as sp
from matplotlib import pyplot as plt
from collections import OrderedDict
import time
import datetime
import glob
import sys


from model.node import Node

RATIO = 0.65
BUFFER_SIZE = 1024

class NodeGenerator(Node):
    def __init__(self, network_address, loc):
        self.objects = {}
        self.init_network(network_address, loc)
        self.filename = ANALYSIS_FILE
        file = open(self.filename,"w")
        file.close()
        file = open('log.txt',"w")
        file.close()
        if TRACK:
            self.init_tracker()

    def init_network(self, network_address,loc):
        Node.__init__(self)
        self.loc = loc
        self.network_address = network_address
        self.neighbor_map = {}
        self.socket = None
        self.ip = IP
        self.listener = Thread(target=self.listen, name = "listen")
        self.heartbeat_generator = Thread(target=self.send_heartbeat, name= "send_heartbeat")

    
    def init_tracker(self):
        for file in glob.glob('./img/*.png')+glob.glob('./img/*.jpg'):
            img = {}
            img['path'] = file
            img['image'] = cv2.imread(file, cv2.CV_LOAD_IMAGE_GRAYSCALE)
            img['name'] = file.split(".")[1].split("/")[-1]
            img['history'] = []
            self.objects[img['name']] = img

        self.detector = cv2.ORB(ORB_VALUE)
        self.descriptor = cv2.ORB(ORB_VALUE)
        self.matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")
        for object in self.objects.values():
            kp = self.detector.detect(object['image'])
            object['kp'] = kp
            k_f, d_f = self.descriptor.compute(object['image'],kp)
            object['k_f'] = k_f
            object['d_f'] = d_f
            object['height'], object['width'] = object['image'].shape[:2]
            print object['name'], len(d_f)

        self.capture = cv2.VideoCapture(0)

    def write_to_file(self, msg):
        file = open(self.filename,"a")
        file.write(msg+'\n')
        file.close()

    def log(self, msg):
        file = open('log.txt','a')
        file.write(msg+'\n')
        file.close()

    def track(self):

        def filter_asymmetric(k_ftr, matches, matches2):
            sel_matches = []
            for match1 in matches:
                for match2 in matches2:
                    if k_ftr[match1.queryIdx] == k_ftr[match2.trainIdx] and k_scene[match1.trainIdx] == k_scene[match2.queryIdx]:
                        sel_matches.append(match1)
                        break
            return sel_matches

        def filter_distance(matches):
            dist = [m.distance for m in matches]
            thres_dist = (sum(dist) / len(dist)) * RATIO

            # keep only the reasonable matches
            sel_matches = [m for m in matches if m.distance < thres_dist]
            #print '#selected matches:%d (out of %d)' % (len(sel_matches), len(matches))
            return sel_matches

        while True:
            self.all_matches = {}
            self.detected_objects = []
            for object in self.objects.keys():
                self.all_matches[object]=0

            for frame in range(FRAMES):
                f, orig_img = self.capture.read()
                #img_scene = cv2.flip(orig_img, 1)
                img_scene = cv2.cvtColor(orig_img, cv2.COLOR_BGR2GRAY)
                view = img_scene
                #cv2.imshow("Track", view)
                try:
                    kp_scene = self.detector.detect(img_scene)
                    #print '#keypoints in Scene: %d' % (len(kp_scene))

                    k_scene, d_scene = self.descriptor.compute(img_scene, kp_scene)
                    #print '#keypoints in Scene: %d' % ( len(d_scene))
                    for object in self.objects.values():
                        # match the keypoints
                        try :
                            matches = self.matcher.match(d_scene, object['d_f'])
                            matches2 = self.matcher.match(object['d_f'], d_scene)
                            # visualize the matches
                            #print '#matches:', len(matches)
                            dist = [m.distance for m in matches]

                            #print 'distance: min: %.3f' % min(dist)
                            #print 'distance: mean: %.3f' % (sum(dist) / len(dist))
                            #print 'distance: max: %.3f' % max(dist)


                            """ filter matches """
                            matches = filter_distance(matches)
                            matches2 = filter_distance(matches2)
                            if len(matches)+len(matches2) < MATCH_PER_FRAME:
                                raise Exception("Not enough matches")
                            self.all_matches[object['name']] = self.all_matches[object['name']]+len(matches)+len(matches2)
                            sel_matches = filter_asymmetric(object['k_f'], matches, matches2)


                            """ localize object """


                            h_scene, w_scene = img_scene.shape[:2]

                            h_ftr, w_ftr = object['height'], object['width']
                            ftr =[]
                            scene = []

                            for m in sel_matches:
                                scene.append(k_scene[m.queryIdx].pt)
                                ftr.append(object['k_f'][m.trainIdx].pt)

                            ftr = np.float32(ftr)
                            scene = np.float32(scene)

                            homography, mask = cv2.findHomography(ftr, scene, cv2.RANSAC)
                            ftr_corners = np.float32([[0, 0], [w_ftr, 0], [w_ftr, h_ftr], [0, h_ftr]]).reshape(1, -1, 2)
                            corners = np.int32( cv2.perspectiveTransform(ftr_corners, homography).reshape(-1, 2) )





                            """ visualization """

                            view = sp.zeros((max(h_scene, h_ftr), w_scene + w_ftr, 3), np.uint8)
                            view[:h_scene, :w_scene, 0] = img_scene
                            view[:h_ftr, w_scene:, 0] = object['image']
                            view[:, :, 1] = view[:, :, 0]
                            view[:, :, 2] = view[:, :, 0]



                            for m in sel_matches:
                                # draw the keypoints
                                color = tuple([sp.random.randint(0, 255) for _ in xrange(3)])
                                cv2.line(view, (int(k_scene[m.queryIdx].pt[0]), int(k_scene[m.queryIdx].pt[1])),
                                    (int(object['k_f'][m.trainIdx].pt[0] + w_scene), int(object['k_f'][m.trainIdx].pt[1])), color, 2)



                            cv2.polylines(view, [np.int32([c+[w_scene,0] for c in ftr_corners])], True, (0, 255, 0), 2)
                            cv2.polylines(view, [corners], True, (0, 255, 0), 2)
                        except Exception:
                            pass
                except Exception:
                    pass
                view = cv2.resize(view, None, fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC)
                #detected = cv2.resize(detected, None, fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC)
                cv2.imshow("Track", view)
                #cv2.imshow("Detected", detected)
            self.log(json.dumps(self.all_matches))
            for matched_object in self.all_matches:
                if self.all_matches[matched_object] > MATCH_PER_RUN:
                    img = self.objects[matched_object]['image']
                    dim = (200,200)
                    img = cv2.resize(img, dim,interpolation=cv2.INTER_AREA)
                    self.detected_objects.append(img)

                    #send data to neighbours
                    msg = {'type': 'object_info', 'data': {'object': self.objects[matched_object]['name'], 'history' : self.objects[matched_object]['history']+[{'ts':str(datetime.datetime.now()).split('.')[0],'loc': self.loc}] }}
                    self.broadcast_neighbours(json.dumps(msg))
                    self.write_to_file(json.dumps({'object': self.objects[matched_object]['name'], 'ts':str(datetime.datetime.now()).split('.')[0],'loc': self.loc}))

            if len(self.detected_objects) > 0:
                detected = np.concatenate(tuple(self.detected_objects), axis=1)
                cv2.imshow("Detected", detected)
            else:
                detected = sp.zeros((200, 400, 3), np.uint8)
                cv2.putText(detected,"Nothing Detected", (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
                cv2.imshow("Detected", detected)




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
                print ""
                print "OBJECTDATA : %s" % data
                for entry in data['history']:
                    entry['object']= data['object']
                    self.write_to_file(json.dumps(entry))
                self.objects[data['object']]['history']= self.objects[data['object']]['history'] + data['history']
            if message['type'] == 'heartbeat':
                data = message['data']
                self.log("HEARTBEAT : %s" % str(data))
                #print "HEARTBEAT : %s" % data
            #print ""
        except Exception:
            raise
            print 'Bad Message received: %s' % msg

    def message(self,address, msg):
        s = socket.socket()
        s.connect(address)
        s.send(msg)
        s.close()
            

    def broadcast_neighbours(self, message):
        for node in self.neighbors:
            #print "Broadcast to %s" % node
            try :
                self.message((node["ip"],node["port"]),message)
            except Exception:
                print "Cannot reach Neighbour %s" % node

    def send_heartbeat(self):
        while True:
            time.sleep(5)
            self.heartbeat()

    def heartbeat(self):
            self.broadcast_neighbours(json.dumps({'type': 'heartbeat', 'data': {'port': self.port, 'ip': self.ip, 'loc': self.loc}}))

    def stop(self):
        self.listener.terminate()
        sys.exit(0)

    def generate_report(self):
        name = raw_input("Enter the Object name to analyse:")
        if name not in self.objects.keys():
            print "Cannot find object"
            return
        object = self.objects[name]
        history = object['history']
        history.sort(key = lambda d: d['ts'])
        x_pts = []
        y_pts = []
        labels = []
        for entry in history:
            x_pts.append(entry['loc'][0])
            y_pts.append(entry['loc'][1])
            labels.append(entry['ts'])
        plt.plot(x_pts,y_pts,marker='o', label="Trajectory of "+ name)



    def start(self):
        self.listener.start()
        self.heartbeat_generator.start()
        if TRACK:
            self.track()
            pass




