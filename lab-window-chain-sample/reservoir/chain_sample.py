#!/usr/bin/python3

from scapy.all import *
from queue import Queue
import datetime, time, sys


class ChainSample():

    def __init__(self, sampleArray):
        self.sampleArray = sampleArray
        self.queueList = Queue()
        self.i = 0
        self.check = True
    
    def insert(self, packet):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
        if self.check:
            self.sampleArray[self.i] = (st, packet); 
            self.i += 1
            if self.i == len(self.sampleArray):
                self.i = 0
                self.check = False
        else:
            self.queueList.put((st, packet))
            
    def expired(self):
        self.sampleArray[self.i] = self.queueList.get()
        self.i += 1  
        if self.i == len(self.sampleArray):
            self.i = 0
            
    def restore(self, packet):
        packet[IP].tos = 0

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

    def getI(self):
        return selft.i
    
    def setSampleArray(self, sampleArray):
        self.sampleArray = sampleArray
        
    def setQueueList(self, queueList):
        self.queueList = queueList
    
    def setI(self, i):
        self.i = i


chain = None


def packet_callback(packet):
    global chain
    print ("TypeOfService: {}".format(packet[IP].tos))
    if packet[TCP].payload:
        # packet insert
        if packet[IP].tos == 1 :
            chain.restore(packet)
            chain.insert(packet)
            #chain.printQueueList()
            #chain.printSampleArray()
        # packet expired
        elif packet[IP].tos == 2 :
            chain.restore(packet)
            chain.expired()
            #chain.printQueueList()
            #chain.printSampleArray()
        # packet insert + packet expired
        elif packet[IP].tos == 3 :
            chain.restore(packet)
            chain.insert(packet)
            chain.expired()
            #chain.printQueueList()
            #chain.printSampleArray()
        # other action
        else:
            print ("> No defined action!!")
            chain.printQueueList()
            chain.printSampleArray()
        # print ("TypeOfService: {}, checksum: {}".format(packet[IP].tos, packet[IP].chksum))


def main(size):
    global chain
    sampleArray = [None] * size
    chain = ChainSample(sampleArray)
    print ("> Chain Sample Ready!!")
    sniff(iface="eth0", filter="tcp", prn=packet_callback, store=0)


if __name__ == "__main__":
        main(int(sys.argv[1]))
