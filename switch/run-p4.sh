#!/bin/bash
# Switch starter

echo Compilo p4
p4c-bmv2 --json /behavioral-model/targets/l2_switch/l2_switch.json /behavioral-model/targets/l2_switch/l2_switch.p4
echo Starto il servizio
./behavioral-model/targets/l2_switch/l2_switch -i 0@eth0 /behavioral-model/targets/l2_switch/l2_switch.json
