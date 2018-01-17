from scapy.all import *
from queue import Queue
import random, math, csv

# size of sample and window
N = 5
W = 100

# sample variable
sample = [None] * N
queue = Queue()
i = 0

# successor and expiry
array_succ_exp = [0] * W
tw = 0

# counter packet chain sample
t = 0
# counter total packets
t_tot = 0


# max packets send
MAX_PACKET_SEND = 100000
# number of test
NUMBER_TEST = 100
# limit single test
limit_test = MAX_PACKET_SEND / NUMBER_TEST
count_limit_test = 0

array_packet_count = [0] * int(limit_test - N)


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
    global array_packet_count

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
                    # uniformity
                    if(successor < limit_test):
                        array_packet_count[successor-N] += 1
                    break
            else:
                if(array_succ_exp[successor-W] == 2): # =0 non necessaria
                    array_succ_exp[successor-W] += 1
                    # uniformity
                    if(successor < limit_test):
                        array_packet_count[successor-N] += 1
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

            i += 1
            if(i == N):
                i = 0

        # control successor
        if(array_succ_exp[tw] == 1):
            # insert packet in the queue
            entry = EntryQueue(packet, -1)
            queue.put(entry)

            # select successor
            while True:
                successor = random.randrange(t+1, t+W)
                delta = successor - t
                if((tw + delta) < W):
                    if(array_succ_exp[tw+delta] == 0 or array_succ_exp[tw+delta] == 2):
                        array_succ_exp[tw+delta] += 1
                        # uniformity
                        if(successor < limit_test):
                            array_packet_count[successor-N] += 1
                        break
                else:
                    if(array_succ_exp[(tw+delta)-W] == 0 or array_succ_exp[(tw+delta)-W] == 2):
                        array_succ_exp[(tw+delta)-W] += 1
                        # uniformity
                        if(successor < limit_test):
                            array_packet_count[successor-N] += 1
                        break

            # expiry
            array_succ_exp[tw] = 2

    t += 1
    tw += 1
    if(tw == W):
        tw = 0


# print array
def print_array(array):
    for i in range(len(array)):
        print(array[i])


# write on file
def writeOnFile(array):
        with open('/hosthome/netkit_temp/labs/Test_Chain_Sample/uniform.csv', 'a', newline='') as f:
            writer = csv.writer(f, delimiter=',', lineterminator="\n")
            writer.writerow(array);


# callback single-test
def packet_callback(packet):
    global t
    global limit_test
    global count_limit_test
    global t
    global tw
    global i
    global t_tot
    global sample
    global queue
    global array_succ_exp
    global array_packet_count

    if packet[TCP].payload:
        chain_sample(packet)
        #print(t)
        t_tot += 1

        count_limit_test += 1
        if(count_limit_test == limit_test):
            count_limit_test = 0
            t = 0
            tw = 0
            i = 0
            sample = [None] * N
            queue = Queue()
            array_succ_exp = [0] * W

        if(t_tot == MAX_PACKET_SEND):
            print("Write on file...")
            writeOnFile(array_packet_count)
            print("Exit!")
            exit()


# main
def main():

    print ("Run algorithm Chain Sample:")
    sniff(iface="eth0", filter="tcp", prn=packet_callback, store=0)


if __name__ == "__main__":
    main()
