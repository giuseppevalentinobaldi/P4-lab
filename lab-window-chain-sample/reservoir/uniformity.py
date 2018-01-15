#!/usr/bin/python3

import csv
from queue import Queue


class Uniformity():
    
    def __init__(self, N, W):
        self.uniform = [0] * W
        self.collector = Queue()
        self.collectorChain = [Queue()] * N
        
    def uniformCollect(self, p):
        self.collector.put(p)
        
    def uniformIncrement(self, t):
        p = self.collector.get()
        W = len(self.uniform)
        delta = p - t
        tw = t - 1 - (int(t / W)) * W
        if tw + delta < W:
            i = tw + delta
            self.uniform[i] = self.uniform[i] + 1
        else:
            i = tw + delta - W
            self.uniform[i] = self.uniform[i] + 1
            
    def uniformCollectChain(self, p, i):
        self.collectorChain[i].put(p)
        
    def uniformIncrementChain(self, t, i):
        p = self.collectorChain[i].get()
        W = len(self.uniform)
        delta = p - t
        tw = t - 1 - (int(t / W)) * W
        if tw + delta < W:
            i = tw + delta
            self.uniform[i] = self.uniform[i] + 1
        else:
            i = tw + delta - W
            self.uniform[i] = self.uniform[i] + 1

    def printUniform(self):
        for e in self.uniform:
            print("{} ".format(e), end="")
        print("")
    
    def writeUniform(self):
        with open('/hosthome/git/P4-lab/lab-window-chain-sample/uniform.csv', 'a', newline='') as f:
            writer = csv.writer(f, delimiter=',', lineterminator="\n")
            writer.writerow(self.uniform);   


def main():
    print("Uniformity")


if __name__ == "__main__":
    main()
