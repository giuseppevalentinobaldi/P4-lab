#!/bin/bash
# repeat send_one.py n times

function read_register(){
    echo "register_read reg"| /behavioral-model/targets/simple_switch/sswitch_CLI /behavioral-model/targets/simple_switch/chain_uniform_sre.json
    echo "register_read reg_se"| /behavioral-model/targets/simple_switch/sswitch_CLI /behavioral-model/targets/simple_switch/chain_uniform_sre.json
}

read_register
