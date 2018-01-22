#!/usr/bin/python3
from queue import PriorityQueue
from queue import Queue
from collections import OrderedDict
from uniformity import Uniformity
from scapy.all import *
import random


class ChainSampleO():
    
    def __init__(self, N, W, STAMP):
        self.N = N
        self.W = W
        self.STAMP = STAMP
        self.t = 0
        self.tw = 0
        self.reservoir = [None] * N
        self.chain = [Queue()] * N
        self.arraySuccessor = [-1] * W
        self.queueExpiry = PriorityQueue()
        self.expiry = ()
        self.uniform = Uniformity(self.N, self.W)
        
    def execute(self, packet):
        if self.getT() < self.getN():
            self.coldStart(packet)
        else:
            self.regime(packet)
            # self.print_chain()
            # self.print_resevoir()
            # print("current Expiry {} with index {}".format(self.expiry[0], self.expiry[1]))
            # self.printQueue(self.queueExpiry)
            if self.getT() % self.STAMP == 0:
                self.uniform.writeUniform()
                print("t: {}".format(self.getT()))
        
    def coldStart(self, packet):
        self.reservoir[self.t] = packet
        self.t += 1
        index = self.t - 1
        # set Successor
        while True:
            p = random.randint(self.N + self.t, self.W + self.t)
            delta = p - self.t
            if((self.tw + delta) < self.W):
                if(self.arraySuccessor[self.tw + delta] == -1):
                    self.arraySuccessor[self.tw + delta] = index
                    self.uniform.uniformCollectChain(self.tw + delta, index)
                    break
            else:
                if(self.arraySuccessor[(self.tw + delta) - self.W] == -1):
                    self.arraySuccessor[(self.tw + delta) - self.W] = index
                    self.uniform.uniformCollectChain((self.tw + delta) - self.W, index)
                    break
        self.queueExpiry.put((self.t + self.W, index))
        self.tw += 1
        if self.t == self.N:
            self.expiry = self.queueExpiry.get()
    
    def regime(self, packet):
        self.t += 1
        # add element in chain[i-th]
        if self.arraySuccessor[self.tw] != -1:
            index = self.arraySuccessor[self.tw]  # give index
            self.arraySuccessor[self.tw] = -1
            self.chain[index].put((self.t + self.W, packet))
            # set Successor
            while True:
                p = random.randint(self.t + 1 , self.W + self.t)
                delta = p - self.t
                if((self.tw + delta) < self.W):
                    if(self.arraySuccessor[self.tw + delta] == -1):
                        self.arraySuccessor[self.tw + delta] = index
                        self.uniform.uniformCollectChain(self.tw + delta, index)
                        break
                else:
                    if(self.arraySuccessor[(self.tw + delta) - self.W] == -1):
                        self.arraySuccessor[(self.tw + delta) - self.W] = index
                        self.uniform.uniformCollectChain((self.tw + delta) - self.W , index)
                        break
        # expiry packet
        if self.expiry[0] == self.t:
            tup = self.chain[self.expiry[1]].get()  # prendo la tupla (expiry,packet) dalla i-esima coda 
            self.queueExpiry.put((tup[0], self.expiry[1]))  # inserisco la scadenza del nuovo campione
            self.reservoir[self.expiry[1]] = tup[1]  # inserisco il nuovo campione nel reservoir
            self.uniform.uniformIncrementChain(self.expiry[1])  # u(t,i) increment at time of insert for uniformity 
            self.expiry = self.queueExpiry.get()  # prendo la prossima scadenza
        self.tw += 1
        if self.tw == self.W :
            self.tw = 0
            
    def print_resevoir(self):
        print("=====================================================")
        for pkt in self.reservoir :
            print("{} ----HTTP----> {}:{}:\n{}".format(pkt[IP].src, pkt[IP].dst, pkt[IP].dport, str(bytes(pkt[TCP].payload))))
        print("=====================================================")
        
    def print_chain(self):
        for i in range(0, self.N):
            print("index: {}".format(i))
            tmp = Queue()
            print("=====================================================")
            while not (self.chain[i].empty()) :
               tup = self.chain[i].get()
               tmp.put(tup)
               print("expiry: {}\n{} ----HTTP----> {}:{}:\n{}".format(tup[0], tup[1][IP].src, tup[1][IP].dst, tup[1][IP].dport, str(bytes(tup[1][TCP].payload))))
            print("=====================================================")
            self.chain[i] = tmp
        
    def printQueue(self, q):
        with q.mutex:
            print("=====================================================")
            for tup in q.queue:
                print("t: {}\tindex: {}\n".format(tup[0], tup[1]))
            print("=====================================================")
    
    def getT(self):
        return self.t
    
    def getN(self):
        return self.N
    
    def getW(self):
        return self.W


def main():
    print("ChainSampleO")


if __name__ == "__main__":
    main()
