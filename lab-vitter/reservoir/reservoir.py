#!/usr/bin/python

from scapy.all import *
import Queue, datetime

N = 3
q = Queue.Queue(N)


def print_resevoir():
    global q
    tmp = Queue.Queue(N)
    print("=====================================================")
    while not (q.empty()) :
        pkt = q.get()
        tmp.put(pkt)
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print("{}\n{} ----HTTP----> {}:{}:\n{}".format(st, pkt[IP].src, pkt[IP].dst, pkt[IP].dport, str(bytes(pkt[TCP].payload))))
    print("=====================================================")
    q = tmp


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
    sniff(iface="eth0", filter="tcp", prn=packet_callback, store=0)


if __name__ == "__main__":
   main()
