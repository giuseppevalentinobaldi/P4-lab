#!/usr/bin/python3

from scapy.all import *
from queue import Queue
import random
from uniformity import Uniformity

# size of sample and window
N = 10
W = 100

# uniformity observation
STAMP = 1000 #STAMP*ps > 5 (ps = 1/W) pratical condition
snapshot = 100
counter = 0
obs = 0
checkObs = False

# uniformity initilization
uniform = Uniformity(N, W)

# sample variable
sample = [None] * N
queue = Queue()
i = 0

# successor and expiry
array_successor = [-1] * W # contain index uniformity (default -1, no index -2)
array_expiry = [0] * W
tw = 0

# counter packet chain sample
t = 0

class EntryQueue():

    def __init__(self, packet, index_uniformity):
        self.packet = packet
        self.index_uniformity = index_uniformity
    
    def getPacket(self):
        return self.packet

    def getIndexUniformity(self):
        return self.index_uniformity

    def setPacket(self, packet):
        self.packet = packet

    def setIndexUniformity(self, index_uniformity):
        self.index_successor = index_uniformity


# algorithm chain sample
def chain_sample(packet):
    # import global variable
    global N
    global W
    global sample
    global queue
    global i
    global array_successor
    global array_expiry
    global tw
    global t
    global STAMP
    global uniform
    global obs
    global checkObs
    global snapshot
    global counter

    # sample not full (cold start)
    if(t < N):
        # insert packet in sample
        sample[i] = packet

        # select successor
        while True:
            successor = random.randrange(N+t, t+W)
            if(successor < W):
                if(array_successor[successor] == -1):
                    array_successor[successor] = -2
                    break
            else:
                if(array_successor[successor-W] == -1):
                    array_successor[successor-W] = -2
                    break
        
        # calculate expiry
        array_expiry[tw] = 1

        i += 1
        if(i == N):
            i = 0

    # sample full
    else:
        # control expiry
        if(array_expiry[tw] != 0):
            entry = queue.get()
            sample[i] = entry.getPacket()
            array_expiry[tw] = 0

            # uniformity
            if(entry.getIndexUniformity() != -2):
                uniform.uniformIncrement(entry.getIndexUniformity())
                obs += 1
                checkObs = True

            i += 1
            if(i == N):
                i = 0

        # control successor
        if(array_successor[tw] != -1):
            # insert packet in the queue
            entry = EntryQueue(packet, array_successor[tw])
            queue.put(entry)

            # select successor
            while True:
                successor = random.randrange(t+1, t+W)
                delta = successor - t
                if((tw + delta) < W):
                    if(array_successor[tw+delta] == -1):
                        array_successor[tw+delta] = (tw+delta)
                        break
                else:
                    if(array_successor[(tw+delta)-W] == -1):
                        array_successor[(tw+delta)-W] = ((tw+delta)-W)
                        break

            # calculate expiry
            array_expiry[tw] = 1

            array_successor[tw] = -1
    t += 1
    tw += 1
    if(tw == W):
        tw = 0
    if obs % STAMP == 0 and checkObs:
        uniform.writeUniform()
        checkObs = False
        counter += 1
        print("t: {}".format(t))
        if counter == snapshot:
        	exit()


# print array
def print_array(array):
    for i in range(len(array)):
        print(array[i])


# callback
def packet_callback(packet):
    if packet[TCP].payload:
        chain_sample(packet)

# main
def main():
    print ("Run algorithm Chain Sample P4")
    sniff(iface="eth0", filter="tcp", prn=packet_callback, store=0)


if __name__ == "__main__":
    main()
