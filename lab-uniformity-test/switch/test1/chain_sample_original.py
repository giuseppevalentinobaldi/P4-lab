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
array_queue = [Queue()] * N
i = 0

# successor and expiry
array_successor = [None] * W
array_expiry = [-1] * W
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


class EntrySuccessor():

    def __init__(self, index_queue, index_uniformity):
        self.index_queue = index_queue
        self.index_uniformity = index_uniformity
    
    def getIndexQueue(self):
        return self.index_queue

    def getIndexUniformity(self):
        return self.index_uniformity

    def setIndexQueue(self, index_queue):
        self.index_queue = index_queue

    def setIndexUniformity(self, index_uniformity):
        self.index_successor = index_uniformity


# algorithm chain sample
def chain_sample(packet):
    # import global variable
    global N
    global W
    global sample
    global array_queue
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
                if(array_successor[successor] == None):
                    entry_succ = EntrySuccessor(i, -1)
                    array_successor[successor] = entry_succ
                    break
            else:
                if(array_successor[successor-W] == None):
                    entry_succ = EntrySuccessor(i, -1)
                    array_successor[successor-W] = entry_succ
                    break
        
        # calculate expiry
        array_expiry[tw] = i

        i += 1

    # sample full
    else:
        # control expiry
        if(array_expiry[tw] != -1):
            entry_queue = array_queue[array_expiry[tw]].get()
            sample[array_expiry[tw]] = entry_queue.getPacket()
            array_expiry[tw] = -1

            # uniformity
            if(entry_queue.getIndexUniformity() != -1):
                uniform.uniformIncrement(entry_queue.getIndexUniformity())
                obs += 1
                checkObs = True

        # control successor
        if(array_successor[tw] != None):
            # insert packet in the queue
            entry_queue = EntryQueue(packet, array_successor[tw].getIndexUniformity())
            array_queue[array_successor[tw].getIndexQueue()].put(entry_queue)

            # select successor
            while True:
                successor = random.randrange(t+1, t+W)
                delta = successor - t
                if((tw + delta) < W):
                    if(array_successor[tw+delta] == None):
                        entry_succ = EntrySuccessor(array_successor[tw].getIndexQueue(), (tw + delta))
                        array_successor[tw+delta] = entry_succ
                        break
                else:
                    if(array_successor[(tw+delta)-W] == None):
                        entry_succ = EntrySuccessor(array_successor[tw].getIndexQueue(), ((tw+delta)-W))
                        array_successor[(tw+delta)-W] = entry_succ
                        break

            # calculate expiry
            array_expiry[tw] = array_successor[tw].getIndexQueue()

            array_successor[tw] = None
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
    print ("Run algorithm Chain Sample Original")
    sniff(iface="eth0", filter="tcp", prn=packet_callback, store=0)


if __name__ == "__main__":
    main()
