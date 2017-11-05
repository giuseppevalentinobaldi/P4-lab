#!/usr/bin/python

from scapy.all import *

sniff(iface = "eth0", prn = lambda x: hexdump(x))
