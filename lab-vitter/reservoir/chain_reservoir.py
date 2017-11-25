#!/usr/bin/python

from scapy.all import *
from queue import Queue
import datetime, time, sys


class ChainSample():

    def __init__(sampleSize, sampleArray, queueList, dictDeadline, t):
        self.sampleSize = sampleSize
        self.sampleArray = sampleArray
        self.queueList = queueList
        self.dictDeadline = dictDeadline
        self.t = t
    
    def insert(self, packet):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
        if self.t < self.sampleSize:
            self.sampleArray[self.t] = (st, packet);
            self.dictDeadline.update({'pktDeadline': self.t})  # devi passargli la scadenza
            self.t += 1
        else:
            self.queueList.put((st, packet))
            self.t += delta  # devi passargli il lasso di tempo delta ed incrementarlo per ottenere il t totale
            self.dictDeadline.update({'pktDeadline': index})  # devi passargli la scadenza
            
    def deadline(self, deadline):
        indexExpired = self.getdictDeadline[deadline]
        self.sampleArray[indexExpired] = self.getQueueList.get()
        self.t += delta  # devi passargli il lasso di tempo delta ed incrementarlo per ottenere il t totale

    def printQueueList():
        tmp = Queue()
        print("=====================================================")
        while not (self.getQueueList().empty()) :
            tup = self.getQueueList().get()
            tmp.put(tup)
            print("{}\n{} ----HTTP----> {}:{}:\n{}".format(tup[0], tup[1][IP].src, tup[1][IP].dst, tup[1][IP].dport, str(bytes(tup[1][TCP].payload))))
        print("=====================================================")
        self.setQueueList(tmp)
        
    def getSampleSize(self):
        return self.sampleSize

    def getSampleArray(self):
        return self.sampleArray

    def getQueueList(self):
        return self.queueList

    def getDictDeadline(self):
        return self.dictDeadline

    def getT(self):
        return selft.t
    
    def setSampleSize(self, sampleSize):
        self.sampleSize = sampleSize
    
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
        chain.insert(packet)


def main():
    global chain
    chain = ChainSample(3, array(), Queue(), dict(), 0)
    print ("> Chain Sample Ready!!")
    sniff(iface="eth0", filter="tcp", prn=packet_callback, store=0)


if __name__ == "__main__":
        main()
