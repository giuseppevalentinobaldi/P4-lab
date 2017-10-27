#!/bin/bash
# Switch starter
echo "> Compilo Programma P4_14!!"
p4c-bmv2 --json /behavioral-model/targets/simple_switch/copy_to_cpu.json /behavioral-model/targets/simple_switch/copy_to_cpu.p4
echo "> Configuro lo switch!!"
sysctl -w net.ipv4.ip_forward=1
/etc/init.d/procps restart
echo Starto il servizio
./behavioral-model/targets/simple_switch/simple_switch -i 0@eth0 -i 1@eth1 --log-console /behavioral-model/targets/simple_switch/copy_to_cpu.json --pcap &
sleep 10
echo "> no Ready!!"
/behavioral-model/tools/runtime_CLI.py --json /behavioral-model/targets/simple_switch/copy_to_cpu.json < /behavioral-model/targets/simple_switch/commands.txt
echo "> Ready!!"
