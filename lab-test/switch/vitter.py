from scapy.all import *
import logging, re, random, sys

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
N, n, t = 3, 0, 0
resevoir = [None] * N

def packet_callback_r(packet):
    if packet[TCP].payload:
        pkt = str(packet[TCP].payload)
        if packet[IP].dport == 80:
            r(packet)

def r(packet):
    global N, n, t, resevoir
    if n < N:
        resevoir[n] = packet
        n = n + 1
    else:
        if t == 0:
            t = n + 1
        else:
            t = t + 1
        random_m = random.randint(0, t - 1)
        if random_m < n:
            resevoir[random_m] = packet
        for e in resevoir:
            print("\n{} ----HTTP----> {}:{}:\n{}".format(e[IP].src, e[IP].dst, e[IP].dport, str(bytes(e[TCP].payload))))
            
def packet_callback_x(packet):
    if packet[TCP].payload:
        pkt = str(packet[TCP].payload)
        if packet[IP].dport == 80:
            x(packet)
            
V, P, s, notFirst = 0, 0, 0, False

def x(packet):
    global N, n, t, resevoir, V, P, s, notFirst
    if n < N:
        resevoir[n] = packet
        n = n + 1
    else:
        if t == 0:
            t = n + 1
            V = random.randint(0, n - 1)
        else:
            t = t + 1
        if s == 0 :
            if notFirst:
                resevoir[P] = packet
            notFirst = True
            while (pow((t + 1 - n), s + 1) / pow((t + 1), s + 1)) > V:
                s = s + 1
                print("loop")
            P = s
        else :
            s = s - 1
        for e in resevoir:
            print("\n{} ----HTTP----> {}:{}:\n{}".format(e[IP].src, e[IP].dst, e[IP].dport, str(bytes(e[TCP].payload))))

def main(argv):
    print ("Eseguo algoritmo " + (argv.capitalize()))
    if argv == "r" :
        sniff(filter="tcp", prn=packet_callback_r, store=0)
    elif argv == "x": 
        sniff(filter="tcp", prn=packet_callback_x, store=0)
    else:
        print ("Argomento mancante o incorretto")

if __name__ == "__main__":
   main(sys.argv[1])
