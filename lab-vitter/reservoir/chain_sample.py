#!/usr/bin/python

from scapy.all import *
from queue import Queue
import datetime, time, sys


class ChainSample():

    def __init__(self, sampleArray):
        self.sampleArray = sampleArray
        self.queueList = Queue()
        self.dictDeadline = dict()
        self.t = 0
        self.check = True
    
    def insert(self, packet):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
        if self.check:
            self.sampleArray[self.t] = (st, packet);
            self.dictDeadline.update({'pktDeadline': self.t})  
            self.t += 1
            if self.t == len(self.sampleArray):
                self.t = 0
                self.check = False
        else:
            self.queueList.put((st, packet))
            self.t += 1  
            if self.t == len(self.sampleArray):
                self.t = 0
            self.dictDeadline.update({'pktDeadline': self.t})
            
    def expired(self, deadline):
        indexExpired = self.getdictDeadline[deadline]
        self.sampleArray[indexExpired] = self.getQueueList.get()

    def printQueueList(self):
        tmp = Queue()
        print("=====================================================")
        while not (self.queueList.empty()):
            tup = self.queueList.get()
            tmp.put(tup)
            print("{}\n{} ----HTTP----> {}:{}:\n{}".format(tup[0], tup[1][IP].src, tup[1][IP].dst, tup[1][IP].dport, str(bytes(tup[1][TCP].payload))))
        print("=====================================================")
        self.setQueueList(tmp)
        
    def printSampleArray(self):
        print("*****************************************************")
        for tup in self.sampleArray:
            if tup is not None:
                print("{}\n{} ----HTTP----> {}:{}:\n{}".format(tup[0], tup[1][IP].src, tup[1][IP].dst, tup[1][IP].dport, str(bytes(tup[1][TCP].payload))))
        print("*****************************************************")
        
    def getSampleArray(self):
        return self.sampleArray

    def getQueueList(self):
        return self.queueList

    def getT(self):
        return selft.t
    
    def setSampleArray(self, sampleArray):
        self.sampleArray = sampleArray
        
    def setQueueList(self, queueList):
        self.queueList = queueList
    
    def setT(self, t):
        self.t = t


chain = None


def packet_callback(packet):
    global chain
    if packet[TCP].payload:
        # packet insert
        if packet[IP].tos == 1 :
            chain.insert(packet)
            chain.printQueueList()
            chain.printSampleArray()
        # packet expired
        elif packet[IP].tos == 2 :
            chain.expired(packet[IP].id)
            chain.printQueueList()
            chain.printSampleArray()
        # packet insert + packet expired
        elif packet[IP].tos == 3 :
            chain.insert(packet)
            chain.expired(packet[IP].id)
            chain.printQueueList()
            chain.printSampleArray()
        # other action
        else:
            print ("> No defined action!!")
            chain.printQueueList()
            chain.printSampleArray()


def main(size):
    global chain
    sampleArray = [None] * size
    chain = ChainSample(sampleArray)
    print ("> Chain Sample Ready!!")
    sniff(iface="eth0", filter="tcp", prn=packet_callback, store=0)


if __name__ == "__main__":
        main(int(sys.argv[1]))
