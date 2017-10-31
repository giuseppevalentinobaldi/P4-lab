#!/bin/bash
# Switch starter
echo "> Compilo Programma P4_14!!"
p4c-bmv2 --json /behavioral-model/targets/simple_router/ipv4_forward_P4_14.json /behavioral-model/targets/simple_router/ipv4_forward_P4_14.p4
echo "> Configuro lo switch!!"
sysctl -w net.ipv4.ip_forward=0
/etc/init.d/procps restart
echo Starto il servizio
./behavioral-model/targets/simple_router/simple_router -i 0@eth0 -i 1@eth1 --log-console /behavioral-model/targets/simple_router/ipv4_forward_P4_14.json --pcap &
sleep 10
echo "> no Ready!!"
/behavioral-model/tools/runtime_CLI.py --json /behavioral-model/targets/simple_router/ipv4_forward_P4_14.json < /behavioral-model/targets/simple_router/commands_P4_14.txt
echo "> Ready!!"