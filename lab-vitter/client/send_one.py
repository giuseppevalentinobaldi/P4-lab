#!/usr/bin/python

from scapy.all import *
import string, random

p = Ether(dst="02:42:ac:12:00:02") / IP(dst="10.0.0.1") / TCP() / ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
# p.show()
hexdump(p)
sendp(p, iface = "eth0")