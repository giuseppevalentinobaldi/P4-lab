#!/usr/bin/python

'''
Random Sampling with a Reservoir
JEFFREY SCOTT VITTER
@see: http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.138.784&rep=rep1&type=pdf

@authors: Giuseppe Valentino Baldi, Marco Lorini
@contact: giuseppevalentinobaldi@gmail.com, marck_91@hotmail.it 
@version: 1.0.0
@license: MIT (http://opensource.org/licenses/MIT)
'''

from scapy.all import *
from queue import PriorityQueue
from collections import OrderedDict
from queue import Queue
import random, sys, collections
N, W, t, tw, cExpiry, cSuccessor = 5, 50, 0, 0, (), ()
resevoir = [None] * N
chain = [Queue()] * N
expiry = PriorityQueue()
successor = OrderedDict()


def printPriorityQueueSuccessor():
    global successor
    print("=====================================================")
    for key, value in successor.items():
        print("t: {}\tindex: {}\n".format(key, value))
    print("=====================================================")

        
def printPriorityQueueExpiry():
    global expiry
    tmp = PriorityQueue()
    print("=====================================================")
    while not (expiry.empty()):
        tup = expiry.get()
        tmp.put(tup)
        print("t: {}\tindex: {}\n".format(tup[0], tup[1]))
    print("=====================================================")
    expiry = tmp


def packet_callback(packet):
    global counter, alg
    if packet[TCP].payload:
        chain_sample(packet)


def chain_sample(packet):
    global N, W, t, tw, cExpiry, cSuccessor, resevoir, chain, expiry, successor
    if t < N:
        resevoir[t] = packet
        t = t + 1
        p = random.randint(N + t, W + t)
        while p in successor:
            p = random.randint(N + t, W + t)
        index = t - 1
        expiry.put((t + W, index))
        successor.update({p: index})
        # successor = OrderedDict(sorted(successor.items()))
        printPriorityQueueExpiry()
        printPriorityQueueSuccessor()
        if t == N:
            cExpiry = expiry.get()
    else:
        t = t + 1
        # add element in chain[i-th]
        if t in successor:
            index = successor[t]
            chain[index].put((t + W, packet))
            del successor[t]
            p = random.randint(t + 1, W + t)
            while p in successor:
                p = random.randint(t + 1, W + t)
            successor.update({p: index})
            
        # expiry packet
        if cExpiry[0] == t:
            tup = chain[cExpiry[1]].get()  # prendo la tupla (expiry,packet) dalla i-esima coda 
            expiry.put((tup[0], cExpiry[1]))  # inserisco la scadenza del nuovo campione
            resevoir[cExpiry[1]] = tup[1]  # inserisco il nuovo campione nel reservoir
            cExpiry = expiry.get()  # prendo la prossima scadenza
            
        print(t)
        printPriorityQueueExpiry()
        printPriorityQueueSuccessor()

    
def main():
    sniff(iface="eth2", filter="tcp", prn=packet_callback, store=0)


if __name__ == "__main__":
    main()
