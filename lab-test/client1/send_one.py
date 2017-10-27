from scapy.all import *

p = Ether(dst="02:42:ac:12:00:03") / IP(dst="10.0.0.1") / TCP() / "aaaaaaaaaaaaaaaaaaa"
# p.show()
hexdump(p)
sendp(p, iface = "eth0")
