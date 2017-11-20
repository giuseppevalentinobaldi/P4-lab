#!/usr/bin/python

from scapy.all import *
import Queue, datetime, time

N = 3
q = Queue.Queue(N)


def print_resevoir():
    global q
    tmp = Queue.Queue(N)
    print("=====================================================")
    while not (q.empty()) :
        tup = q.get()
        tmp.put(tup)
        print("{}\n{} ----HTTP----> {}:{}:\n{}".format(tup[0], tup[1][IP].src, tup[1][IP].dst, tup[1][IP].dport, str(bytes(tup[1][TCP].payload))))
    print("=====================================================")
    q = tmp


def resevoir(packet):
    global q
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    if q.qsize() < N:
        q.put((st, packet))
        print_resevoir()
    else:
        q.get()
        q.put((st, packet))
        print_resevoir()


def packet_callback(packet):
    if packet[TCP].payload:
        resevoir(packet)


def main():
    print ("> Reservoir ready!!")
    sniff(iface="eth0", filter="tcp", prn=packet_callback, store=0)


if __name__ == "__main__":
   main()
