#!/bin/bash
# Switch starter
echo "> Compilo Programma P4_14!!"
p4c-bm2-ss --p4v 14 /behavioral-model/targets/simple_switch/heavy_hitter.p4 -o /behavioral-model/targets/simple_switch/heavy_hitter.json
echo "> Configure the switch!!"
sysctl -w net.ipv4.ip_forward=0
/etc/init.d/procps restart
echo "> Start the service!!"
./behavioral-model/targets/simple_switch/simple_switch -i 0@eth0 -i 1@eth1 --log-console /behavioral-model/targets/simple_switch/heavy_hitter.json --pcap &
sleep 10
echo "> no Ready!!"
/behavioral-model/tools/runtime_CLI.py --json /behavioral-model/targets/simple_switch/heavy_hitter.json < /behavioral-model/targets/simple_switch/commands_heavy_hitter.txt
echo "> Ready!!"