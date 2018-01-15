#!/usr/bin/python3
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
from chain_sample_o import ChainSampleO
from chain_sample_gm import ChainSampleGM
cs = None
import sys


def chan_sample_callback(packet):
    global cs
    if packet[TCP].payload:
        cs.execute(packet)
    
   
def main():
    global cs
    N = 10  # sample
    W = 100  # windows
    choice = input("1 - chain sample original\n2 - chain sample gm\n what do you want run? ")
    if int(choice) == 1:
        cs = ChainSampleO(N, W)
    else:
        cs = ChainSampleGM(N, W)
    sniff(iface="eth0", filter="tcp", prn=chan_sample_callback, store=0)


if __name__ == "__main__":
    main()
