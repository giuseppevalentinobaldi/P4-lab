#!/usr/bin/python3
from queue import PriorityQueue
from queue import Queue
from uniformity import Uniformity
from scapy.all import *
import random


class ChainSampleGM():
    
    def __init__(self, N, W):
        self.N = N
        self.W = W
        self.t = 0
        self.reservoir = [None] * N
        self.i = 0
        self.chain = Queue()
        self.queueSuccessor = PriorityQueue()
        self.queueExpiry = PriorityQueue()
        self.successor = 0
        self.expiry = 0
        self.uniform = Uniformity(self.N, self.W)
        
    def execute(self, packet):
        if self.getT() < self.getN():
            self.coolStart(packet)
        else:
            self.regime(packet)
            print("t: {}".format(self.getT()))
            #self.print_chain()
            #self.print_resevoir()
            #print("current Successor {}".format(self.successor))
            #self.printQueue(self.queueSuccessor)
            #print("current Expiry {}".format(self.expiry))
            #self.printQueue(self.queueExpiry)
            if self.getT() % 800 == 0:
                self.uniform.writeUniform()
                self.uniform.printUniform()
        
    def coolStart(self, packet):
        self.reservoir[self.t] = packet
        self.t += 1
        p = random.randint(self.N + self.t, self.W + self.t)
        while self.is_in_queue(p, self.queueSuccessor):
            p = random.randint(self.N + self.t, self.W + self.t)
        self.queueSuccessor.put(p)
        self.uniform.uniformCollect(p)
        self.queueExpiry.put(self.t + self.W)
        if self.t == self.N:
            self.successor = self.queueSuccessor.get()
            self.expiry = self.queueExpiry.get()
    
    def regime(self, packet):
        self.t += 1
        # add element in chain[i-th]
        if self.t == self.successor:
            self.chain.put(packet)
            p = random.randint(self.t + 1, self.W + self.t)
            while self.is_in_queue(p, self.queueSuccessor):
                p = random.randint(self.t + 1, self.W + self.t)
            self.queueSuccessor.put(p)
            self.uniform.uniformCollect(p)
            self.queueExpiry.put(self.t + self.W)
            self.successor = self.queueSuccessor.get()
        # expiry packet
        if self.t == self.expiry:
            self.reservoir[self.i] = self.chain.get()
            self.expiry = self.queueExpiry.get()
            self.uniform.uniformIncrement(self.t)
            self.i += 1
            if self.i == self.N:
                self.i = 0

    def is_in_queue(self, x, q):
        with q.mutex:
            return x in q.queue
        
    def print_resevoir(self):
        print("=====================================================")
        for pkt in self.reservoir :
            print("{} ----HTTP----> {}:{}:\n{}".format(pkt[IP].src, pkt[IP].dst, pkt[IP].dport, str(bytes(pkt[TCP].payload))))
        print("=====================================================")
        
    def print_chain(self):
        tmp = Queue()
        print("=====================================================")
        while not (self.chain.empty()) :
            pkt = self.chain.get()
            tmp.put(pkt)
            print("{} ----HTTP----> {}:{}:\n{}".format(pkt[IP].src, pkt[IP].dst, pkt[IP].dport, str(bytes(pkt[TCP].payload))))
        print("=====================================================")
        self.chain = tmp
        
    def printQueue(self, q):
        with q.mutex:
            print("=====================================================")
            for t in q.queue:
                print("t: {}\n".format(t))
            print("=====================================================")
    
    def getT(self):
        return self.t
    
    def getN(self):
        return self.N
    
    def getW(self):
        return self.W


def main():
    print("ChainSampleGM")


if __name__ == "__main__":
    main()
