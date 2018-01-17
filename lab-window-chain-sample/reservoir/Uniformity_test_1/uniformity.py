#!/usr/bin/python3

import csv
from queue import Queue


class Uniformity():
    
    def __init__(self, N, W):
        self.uniform = [0] * W
        self.collectorChain = [Queue()] * N
        
    def uniformIncrement(self, tw):
        self.uniform[tw] = self.uniform[tw] + 1
            
    def uniformCollectChain(self, tw, i):
        self.collectorChain[i].put(tw)
        
    def uniformIncrementChain(self, i):
        tw = self.collectorChain[i].get()
        self.uniform[tw] = self.uniform[tw] + 1

    def printUniform(self):
        for e in self.uniform:
            print("{} ".format(e), end="")
        print("")
    
    def writeUniform(self):
        with open('/hosthome/git/P4-lab/lab-window-chain-sample/reservoir/TempTest1/uniform.csv', 'a', newline='') as f:
            writer = csv.writer(f, delimiter=',', lineterminator="\n")
            writer.writerow(self.uniform);   


def main():
    print("Uniformity")


if __name__ == "__main__":
    main()
