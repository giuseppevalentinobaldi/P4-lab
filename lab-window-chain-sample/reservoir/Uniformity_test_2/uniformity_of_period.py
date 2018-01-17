#!/usr/bin/python3
import csv
from queue import Queue


class UniformityOfPeriod():
    
    def __init__(self, T, N):
        self.N = N
        self.T = T
        self.uniformPeriod = [0] * self.T
        self.collectorChain = [Queue()] * self.N
        
    def uniformPeriodIncrement(self,t):
        #print("incremente packet{} ".format(t))
        self.uniformPeriod[t] = self.uniformPeriod[t] + 1
        
    def uniformPeriodCollectChain(self, t, i):
        self.collectorChain[i].put(t)
        
    def uniformPeriodIncrementChain(self, i):
        t = self.collectorChain[i].get()
        #print("incremente packet{} ".format(t))
        self.uniformPeriod[t] = self.uniformPeriod[t] + 1
        
    def uniformPeriodChainReset(self):
        self.collectorChain = [Queue()] * self.N
        
    def printUniformPeriod(self):
        for e in self.uniformPeriod:
            print("{} ".format(e), end="")
        print("")
    
    def writeUniformPeriod(self):
        with open('/hosthome/git/P4-lab/lab-window-chain-sample/uniformPeriod.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',', lineterminator="\n")
            writer.writerow(self.uniformPeriod);   


def main():
    print("UniformityOfPeriod")


if __name__ == "__main__":
    main()
