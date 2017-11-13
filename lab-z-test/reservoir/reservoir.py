#!/usr/bin/python

from scapy.all import *
import Queue

N = 3
q = Queue.Queue(N)

def print_resevoir():
    global q
    tmp = Queue.Queue(N)
    while not (q.empty()) :
        pkt=q.get()
        tmp.put(pkt)
        print("\n{} ----HTTP----> {}:{}:\n{}\n-------------------------------------------------------".format(pkt[IP].src, pkt[IP].dst, pkt[IP].dport, str(bytes(pkt[TCP].payload))))
    q=tmp

def resevoir(packet):
    global q
    if q.qsize() < N:
        q.put(packet)
        print_resevoir()
    else:
        q.get()
        q.put(packet)
        print_resevoir()

def packet_callback(packet):
    if packet[TCP].payload:
        resevoir(packet)

def main():
    print ("> Reservoir ready!!")
    sniff(iface = "eth0", filter = "tcp", prn=packet_callback, store=0)

if __name__ == "__main__":
   main()