#!/bin/bash
# fix tcpdump

mv /usr/sbin/tcpdump /usr/bin/tcpdump
ln -s /usr/bin/tcpdump /usr/sbin/tcpdump

echo "> Ready!!"