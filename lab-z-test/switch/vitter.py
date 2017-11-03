from scapy.all import *
import logging, re, random, sys, math

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
            
V, s, num = 0, 0, 0.0

def x(packet):
    global N, n, t, resevoir, V, s, num
    if n < N:
        resevoir[n] = packet
        n = n + 1
    else:
        if t == 0:
            t = n + 1
            num = num + 1
        else:
            t = t + 1
            num = num + 1
        if s == 0 :
            V = random.uniform(0, 1)
            r = random.randint(0, n - 1)
            if num > 1:
                resevoir[r] = packet
            notFirst = True
            quot = num / t 
            while quot > V:
                s = s + 1
                t = t + 1
                num = num + 1
                quot = quot * num / t 
                print("loop")
            print(V)
            print(quot)
            if s > 0:
                s = s - 1
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
