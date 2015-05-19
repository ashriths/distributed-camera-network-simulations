__author__ = 'ashrith'

IP = '127.0.0.1'
#IP = '192.168.43.116'

import socket
from threading import Thread
import json
import math
from model.node import Node


BUFFER_SIZE = 1024

class NetworkGenerator(Thread):
    def __init__(self):
        Thread.__init__(self);
        self.nodes = []
        self.sentinel = False
        self.neighbor_map = {}
        self.socket = None
        self.port = None
        self.ip = IP
        self.listener = Thread(target=self.listen, name = "listen")
    '''
    def get_host_ip(self):
        self.ip = socket.gethostbyname(socket.gethostname())
    '''

    def message(self,address, msg):
        s = socket.socket()
        s.connect(address)
        s.send(msg)
        s.close()
    
    def run(self):
        self.listen()

    def broadcast(self, message):
        for node in self.nodes:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((node.ip, node.port))
            s.send(message)
            s.close()

    def listen(self):
        self.port = 5000
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bind = False
        self.sentinel = True
        while not bind:
            try:
                self.socket.bind((self.ip, self.port))
                bind = True
                print("Server created on %s listening to port %s" % (self.ip, self.port))
            except socket.error:
                self.port += 1
        while True:
            self.socket.listen(5)
            connection, add = self.socket.accept()
            self.process_message(connection.recv(BUFFER_SIZE))

    def process_message(self, msg):
        # try:
        message = json.loads(msg)
        if message['type'] == 'intro':
            data = message['data']
            node = Node(ip=data['ip'], port=data['port'], loc=data['loc'])
            neighbors = self.find_neighbors(node)
    
            self.nodes.append(node)
            self.broadcast(json.dumps(
                {'type': 'admin_broadcast', 'from': 'admin', 'data': "New Node in Network, Address : %s" % str(data)}))
            print "New request to join Network (Address : %s )" % str(data)
            print "Total Nodes in Network = " + str(len(self.nodes))
            # print self.nodes

            # set neighbors
            print "Neighbours found :"+str(neighbors)
            if len(neighbors) > 0:
                self.message((node.ip, node.port),json.dumps({'type': 'neighbor_info', 'from': 'admin', 'data': neighbors }))
                for neighbor in neighbors:
                    self.message((neighbor['ip'], neighbor['port']),json.dumps({'type': 'neighbor_info', 'from': 'admin', 'data': [{'ip': node.ip, 'port': node.port, 'loc': node.loc}] }))
        else :
            print message

    def find_distance(self,node1, node2):
        print node1.loc, node2.loc
        return math.sqrt((node1.loc[0]-node2.loc[0])**2 + (node1.loc[1]-node2.loc[1])**2 )

    def find_neighbors(self, new_node):
        nodes = []
        mins = []
        for node in self.nodes:
            dist = self.find_distance(new_node, node)
            if len(nodes) < 2:
                if len(nodes)!=0 and dist < mins[0]:
                    nodes.insert(0,node)
                    mins.insert(0,dist)
                else:
                    nodes.append(node)
                    mins.append(dist)
        send = []
        for node in nodes:
            send.append({'ip':node.ip, 'port' : node.port, 'loc': node.loc })
        return send


    def stop(self):
        self.run = False
        self.listener.join()
        print "Server Stopped"


    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.start()


# logging.basicConfig(filename='server.log', filemode='w', level=logging.DEBUG)


