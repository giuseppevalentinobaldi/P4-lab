#!/bin/bash
# Switch starter

#echo Compilo p4
#p4c-bmv2 --json /behavioral-model/targets/l2_switch/l2_switch.json /behavioral-model/targets/l2_switch/l2_switch.p4

echo Starto il servizio
./behavioral-model/targets/simple_router/simple_router -i 0@eth0 -i 1@eth1 --log-console /behavioral-model/targets/simple_router/ipv4_forward.json
sleep 2
/behavioral-model/tools/runtime_CLI.py --json /behavioral-model/targets/simple_router/ipv4_forward.json < /behavioral-model/targets/simple_router/commands.txt
