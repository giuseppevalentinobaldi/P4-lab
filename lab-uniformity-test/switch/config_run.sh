#!/bin/bash
# Setup switch

function configure_machine(){
    echo "> fix tcpdump!!"
    mv /usr/sbin/tcpdump /usr/bin/tcpdump
    ln -s /usr/bin/tcpdump /usr/sbin/tcpdump
    echo "> install scapy!!"
    cd /scapy
    python3 setup.py install
    cd /
    echo "> Ready!!"
}

configure_machine
