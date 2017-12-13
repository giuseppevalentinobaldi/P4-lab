#!/bin/bash
# repeat send_one.py n times

function read_register(){
    echo "register_read reg"| /behavioral-model/targets/simple_switch/sswitch_CLI /behavioral-model/targets/simple_switch/chain_uniform.json
    echo "register_read reg_successor"| /behavioral-model/targets/simple_switch/sswitch_CLI /behavioral-model/targets/simple_switch/chain_uniform.json
    echo "register_read reg_expiry"| /behavioral-model/targets/simple_switch/sswitch_CLI /behavioral-model/targets/simple_switch/chain_uniform.json
}

read_register
