#!/usr/bin/python3
from queue import PriorityQueue
from queue import Queue
from uniformity_of_period import UniformityOfPeriod
from scapy.all import *
import random


class ChainSampleGMIncrementSuccessor():
    
    def __init__(self, N, W, T, totalPacket):
        self.N = N
        self.W = W
        self.T = T
        self.totalPacket = totalPacket
        self.tTotal = 0
        self.t = 0
        self.tw = 0
        self.reservoir = [None] * N
        self.i = 0
        self.chain = Queue()
        self.arraySuccessor = [-1] * W
        self.queueExpiry = PriorityQueue()
        self.expiry = 0
        self.uniform = UniformityOfPeriod(self.T - self.N, self.N)
        
    def execute(self, packet):
        if self.getT() < self.getN():
            self.coldStart(packet)
        else:
            self.regime(packet)
            # self.print_chain()
            # self.print_resevoir()
            # print("current Expiry {}".format(self.expiry))
            # self.printQueue(self.queueExpiry)
            if self.getT() % self.T == 0:
                self.tTotal += self.getT()
                if self.tTotal == self.totalPacketa :
                    self.uniform.writeUniformPeriod()
        if self.getT() == self.T:
            self.t = 0
            self.tw = 0
            self.reservoir = [None] * self.N
            self.i = 0
            self.chain = Queue()
            self.arraySuccessor = [-1] * self.W
            self.queueExpiry = PriorityQueue()
            self.expiry = 0
            
    def coldStart(self, packet):
        self.reservoir[self.t] = packet
        self.t += 1
        # set Successor
        while True:
            p = random.randint(self.N + self.t, self.W + self.t)
            delta = p - self.t
            if((self.tw + delta) < self.W):
                if(self.arraySuccessor[self.tw + delta] == -1):
                    self.arraySuccessor[self.tw + delta] = 1
                    self.uniform.uniformPeriodIncrement(p - self.N - 1)
                    break
            else:
                if(self.arraySuccessor[(self.tw + delta) - self.W] == -1):
                    self.arraySuccessor[(self.tw + delta) - self.W] = 1
                    self.uniform.uniformPeriodIncrement(p - self.N - 1)
                    break
        self.queueExpiry.put(self.t + self.W)
        self.tw += 1
        if self.t == self.N:
            self.expiry = self.queueExpiry.get()
    
    def regime(self, packet):
        self.t += 1
        # add element in chain[i-th]
        if self.arraySuccessor[self.tw] == 1:
            self.chain.put(packet)
            self.arraySuccessor[self.tw] = -1
            # set Successor
            while True:
                p = random.randint(self.t + 1 , self.W + self.t)
                delta = p - self.t
                if((self.tw + delta) < self.W):
                    if(self.arraySuccessor[self.tw + delta] == -1):
                        self.arraySuccessor[self.tw + delta] = 1
                        self.uniform.uniformPeriodIncrement(p - self.N - 1)
                        break
                else:
                    if(self.arraySuccessor[(self.tw + delta) - self.W] == -1):
                        self.arraySuccessor[(self.tw + delta) - self.W] = 1
                        self.uniform.uniformPeriodIncrement(p - self.N - 1)
                        break
            self.queueExpiry.put(self.t + self.W)
        # expiry packet
        if self.t == self.expiry:
            self.reservoir[self.i] = self.chain.get()
            self.expiry = self.queueExpiry.get()
            self.i += 1
            if self.i == self.N:
                self.i = 0
        self.tw += 1
        if self.tw == self.W:
            self.tw = 0
        
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
    print("ChainSampleGMIncrementSucessor")


if __name__ == "__main__":
    main()