#!/bin/bash
# Switch starter

#echo Compilo p4
#p4c-bmv2 --json /behavioral-model/targets/l2_switch/l2_switch.json /behavioral-model/targets/l2_switch/l2_switch.p4 
sysctl -w net.ipv4.ip_forward=0
echo Starto il servizio
./behavioral-model/targets/simple_switch/simple_switch -i 0@eth0 -i 1@eth1 -i 2@eth2 --log-console /behavioral-model/targets/simple_router/ipv4_forward.json --pcap &
sleep 10
echo "no Ready!!"
/behavioral-model/tools/runtime_CLI.py --json /behavioral-model/targets/simple_router/ipv4_forward.json < /behavioral-model/targets/simple_router/commands.txt
 echo "Ready!!"