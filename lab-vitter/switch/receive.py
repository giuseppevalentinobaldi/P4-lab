#!/usr/bin/python

from scapy.all import *

sniff(iface = "eth2", prn = lambda x: hexdump(x))