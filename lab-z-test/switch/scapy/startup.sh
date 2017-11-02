#!/bin/bash
# fix tcpdump and intall scapy

mv /usr/sbin/tcpdump /usr/bin/tcpdump
ln -s /usr/bin/tcpdump /usr/sbin/tcpdump
python setup.py install
echo "> Ready!!"
