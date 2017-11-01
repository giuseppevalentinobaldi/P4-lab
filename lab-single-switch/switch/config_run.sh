#!/bin/bash
# Switch starter
echo "> Compile program P4_16!!"
p4c-bm2-ss --p4v 16 /behavioral-model/targets/simple_switch/ipv4_forward.p4 -o /behavioral-model/targets/simple_switch/ipv4_forward.jsonecho 
"> Configure the switch!!"
sysctl -w net.ipv4.ip_forward=0
/etc/init.d/procps restart
echo "> Start the service!!"
./behavioral-model/targets/simple_switch/simple_switch -i 0@eth0 -i 1@eth1 --log-console /behavioral-model/targets/simple_switch/ipv4_forward.json --pcap &
sleep 10
echo "> no Ready!!"
/behavioral-model/tools/runtime_CLI.py --json /behavioral-model/targets/simple_switch/ipv4_forward.json < /behavioral-model/targets/simple_switch/commands.txt
echo "> Ready!!"