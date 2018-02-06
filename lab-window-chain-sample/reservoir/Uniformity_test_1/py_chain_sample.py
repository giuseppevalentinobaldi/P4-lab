#!/usr/bin/python3
'''
Sampling From a Moving Window Over Streaming Data
Brian Babcock, Mayur Datar, Rajeev Motwani
@see: https://pdfs.semanticscholar.org/1291/e22341cb130d1fd166f51f6d746ec5fe98a0.pdf

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
    N = 100  # sample
    W = 1000  # windows
    STAMP = 8000 #STAMP*ps > 5 (ps = 1/W) pratical condition
    choice = input("1 - chain sample original\n2 - chain sample gm\n what do you want run? ")
    if int(choice) == 1:
        cs = ChainSampleO(N, W, STAMP)
    else:
        cs = ChainSampleGM(N, W, STAMP)
    sniff(iface="eth0", filter="tcp", prn=chan_sample_callback, store=0)


if __name__ == "__main__":
    main()
