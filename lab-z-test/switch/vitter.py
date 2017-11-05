from scapy.all import *
import logging, re, random, sys, math

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
alg, N, n, t, s, num, term = "", 3, 0, 0, 0, 0.0, 0
resevoir = [None] * N
counter = 1

def packet_callback(packet):
    global counter, alg
    if packet[TCP].payload:
        pkt = str(packet[TCP].payload)
        if packet[IP].dport == 80:
            print("packet #: " + `counter`)
            counter = counter + 1
            if alg == "r" :
                r(packet)
            elif alg == "x": 
                x(packet)
            elif alg == "z": 
                z(packet)
            else:
                print ("Missing or incorrect parameter")
                sys.exit(0)

def r(packet):
    global N, n, t, resevoir
    if n < N:
        resevoir[n] = packet
        n = n + 1
        print("------------------------ next step ------------------------")
    else:
        if t == 0:
            t = n + 1
        else:
            t = t + 1
        M = random.randint(0, t - 1)
        if M < n:
            resevoir[M] = packet
        for e in resevoir:
            print("\n{} ----HTTP----> {}:{}:\n{}".format(e[IP].src, e[IP].dst, e[IP].dport, str(bytes(e[TCP].payload))))
        print("------------------------ next step ------------------------")
        
def calculateS(V):
    global t, s, num
    quot = num / t 
    while quot > V:
        s = s + 1
        t = t + 1
        num = num + 1
        quot = quot * num / t 
    print("Skip: " + `s`)
    print("Probability V: " + `V`)
    

def x(packet):
    global N, n, t, resevoir, s, num
    if n < N:
        resevoir[n] = packet
        n = n + 1
        if n == N:
            t = n
        print("------------------------ next step ------------------------")
    else:
        if s == 0:
            t = t + 1
            num = num + 1
            V = random.uniform(0, 1)
            M = random.randint(0, n - 1)
            if num > 1:
                resevoir[M] = packet
                calculateS(V)
            else:
                calculateS(V)
                if s == 0:
                    resevoir[M] = packet
                else:
                    s = s - 1                
        else:
            s = s - 1
        print("Skip: " + `s`)
        for e in resevoir:
            print("\n{} ----HTTP----> {}:{}:\n{}".format(e[IP].src, e[IP].dst, e[IP].dport, str(bytes(e[TCP].payload))))
        print("------------------------ next step ------------------------")

def z(packet):
    global N, n, t, resevoir, s, term
    thresh = 22 * N
    if t < thresh:
        print("Algorithm X")
        x(packet)
    else:
        print("Algorithm Z")
        if s > 0:
            s = s - 1
        else:
            M = random.randint(0, n - 1)
            resevoir[M] = packet
            W = pow(random.uniform(0, 1), -1 / n)
            if term == 0:
                term = t - n + 1
            while True:
                U = random.uniform(0, 1)
                Y = t * (W - 1)
                s = int (Y)
                lhs = pow((U * (pow(((t + 1) / term), 2)) * (term + s)) / (t + Y), 1 / n)
                rhs = (((t + Y) / (term + s)) * term) / t;
                if lhs <= rhs:
                    W = rhs / lhs
                    print ("Mod")
                    break
                y = (((U * (t + 1)) / term) * (t + s + 1)) / (t + Y)
                if n < s: 
                    denom = t 
                    numer_lim = term + s
                else:
                    denom = t - n + s 
                    numer_lim = t + 1
                for numer in range (int(t + s), int(numer_lim), -1):
                    y = (y * numer) / denom
                    denom = denom - 1
                W = pow(random.uniform(0, 1), -1 / n)
                if pow(y, 1 / n) <= (t + Y) / t :
                    print ("Break")
                    break
            t = t + s + 1
            term = term + s + 1
        print("Skip: " + `s`)    
        for e in resevoir:
            print("\n{} ----HTTP----> {}:{}:\n{}".format(e[IP].src, e[IP].dst, e[IP].dport, str(bytes(e[TCP].payload))))
        print("------------------------ next step ------------------------")  
    
def main(argv):
    global alg
    alg = argv
    print ("Run algorithm " + (alg.capitalize()))
    sniff(filter="tcp", prn=packet_callback, store=0)

if __name__ == "__main__":
   main(sys.argv[1])
