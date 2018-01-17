from scapy.all import *
from queue import Queue
import random, math

# size of sample and window
N = 5
W = 101

# max packets send
MAX_PACKET_SEND = 10000

# sample variable
sample = [None] * N
queue = Queue()
i = 0

# successor and expiry
array_succ_exp = [0] * W
array_index_uniformity = [-1] * W
tw = 0

# counter packet chain sample
t = 0

# uniformity and Chi-Quadro
array_uniformity = [0] * (W-1) # observed frequency
count_random = 0
theoretical_frequency = 0
X = 0 # variable test

# variables to multi-test
MULTI_TEST = False
CHI_QUADRO = 124.34 # (p-value = 0.05, 100 (W-1) degrees of freedom)
NUMBER_TEST = 10

limit_test = MAX_PACKET_SEND / NUMBER_TEST
count_limit_test = 0

# value finish test
total_test = 0
test_passed = 0
test_failed = 0


class EntryQueue():

    def __init__(self, packet, index_uniformity):
        self.packet = packet
        self.index_uniformity = index_uniformity
    
    def getPacket(self):
        return self.packet

    def getIndexUniformity(self):
        return self.index_uniformity

    def setPacket(self, packet):
        self.packet = packet

    def setIndexUniformity(self, index_uniformity):
        self.index_successor = index_uniformity   


# algorithm chain sample
def chain_sample(packet):
    # import global variable
    global N
    global W
    global sample
    global queue
    global i
    global array_succ_exp
    global tw
    global t
    global array_uniformity
    global array_index_uniformity
    global count_random

    # sample not full (cold start)
    if(t < N):
        # insert packet in sample
        sample[i] = packet

        # select successor
        while True:
            successor = random.randrange(N+t, t+W)
            if(successor < W):
                if(array_succ_exp[successor] == 0): # =2 non necessaria
                    array_succ_exp[successor] = 1
                    break
            else:
                if(array_succ_exp[successor-W] == 2): # =0 non necessaria
                    array_succ_exp[successor-W] += 1
                    break
        
        # calculate expiry
        array_succ_exp[tw] = 2

        i += 1
        if(i == N):
            i = 0

    # sample full
    else:
        # control expiry
        if(array_succ_exp[tw] >= 2):
            entry = queue.get()
            sample[i] = entry.getPacket()
            array_succ_exp[tw] -= 2
            
            # uniformity
            if(entry.getIndexUniformity() != -1):
                array_uniformity[entry.getIndexUniformity()] += 1
                count_random += 1

            i += 1
            if(i == N):
                i = 0

        # control successor
        if(array_succ_exp[tw] == 1):
            # insert packet in the queue
            entry = EntryQueue(packet, array_index_uniformity[tw])
            queue.put(entry)

            # select successor
            while True:
                successor = random.randrange(t+1, t+W)
                delta = successor - t
                if((tw + delta) < W):
                    if(array_succ_exp[tw+delta] == 0 or array_succ_exp[tw+delta] == 2):
                        array_succ_exp[tw+delta] += 1
                        array_index_uniformity[tw+delta] = (successor-t)-1
                        break
                else:
                    if(array_succ_exp[(tw+delta)-W] == 0 or array_succ_exp[(tw+delta)-W] == 2):
                        array_succ_exp[(tw+delta)-W] += 1
                        array_index_uniformity[(tw+delta)-W] = (successor-t)-1
                        break

            # expiry
            array_succ_exp[tw] = 2
            array_index_uniformity[tw] = -1

    t += 1
    tw += 1
    if(tw == W):
        tw = 0


# print array
def print_array(array):
    for i in range(len(array)):
        print(array[i])


# callback single-test
def packet_callback(packet):
    global t

    if packet[TCP].payload:
        chain_sample(packet)
        print(t)

        if(t == MAX_PACKET_SEND):
            global array_uniformity
            global count_random
            global theoretical_frequency
            global W
            global X

            # uniformity
            print()
            print("Uniformity:")
            print_array(array_uniformity)

            # Chi-Quadro
            print()
            print("Chi-Quadro:")
            print("count random: ", count_random)

            theoretical_frequency = count_random / W
            print("theoretical frequency: ", theoretical_frequency)

            for i in range(len(array_uniformity)):
                X += (pow((array_uniformity[i] - theoretical_frequency), 2)) / (theoretical_frequency)

            print("X: ", X)

            exit()


# callback multi-test
def packet_callback_multi_test(packet):
    global t
    global count_limit_test
    global limit_test

    if packet[TCP].payload:
        chain_sample(packet)
        print(t)

        count_limit_test += 1
        if(count_limit_test == limit_test):
            global array_uniformity
            global count_random
            global theoretical_frequency
            global W
            global X
            global CHI_QUADRO
            global total_test
            global test_passed
            global test_failed

            # chi-quadro
            theoretical_frequency = count_random / W

            for i in range(len(array_uniformity)):
                X += (pow((array_uniformity[i] - theoretical_frequency), 2)) / (theoretical_frequency)

            total_test += 1
            if(X < CHI_QUADRO):
                test_passed += 1
            else:
                test_failed += 1

            # reset
            count_limit_test = 0
            array_uniformity = [0] * (W-1)
            count_random = 0
            #theoretical_frequency = 0
            X = 0
        
        if(t == MAX_PACKET_SEND):
            print()
            print("Total test:", total_test)
            print("Test passed:", test_passed)
            print("Test failed:", test_failed)

            exit()


# main
def main():
    global MULTI_TEST

    if(not MULTI_TEST):
        print ("Run algorithm Chain Sample single-test:")
        sniff(iface="eth0", filter="tcp", prn=packet_callback, store=0)
    else:
        print ("Run algorithm Chain Sample multi-test:")
        sniff(iface="eth0", filter="tcp", prn=packet_callback_multi_test, store=0)


if __name__ == "__main__":
    main()
