#!/usr/bin/python3
import csv
from queue import Queue


class UniformityOfPeriod():
    
    def __init__(self, T, N):
        self.uniformPeriod = [0] * T
        self.collector = Queue()
        self.collectorChain = [Queue()] * N
        
    #def uniformPeriodIncrement(self, t):
    #    self.uniformPeriod[t] = self.uniformPeriod[t] + 1
        
    def uniformPeriodCollectChain(self, t, i):
        self.collectorChain[i].put(t)
        
    def uniformPeriodIncrementChain(self, i):
        t = self.collectorChain[i].get()
        print("incremente packet{} ".format(t))
        self.uniformPeriod[t] = self.uniformPeriod[t] + 1
        
    def uniformPeriodReset(self):
        self.collectorChain = [Queue()] * N
        
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
