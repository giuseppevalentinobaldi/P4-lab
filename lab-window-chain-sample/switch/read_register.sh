#!/bin/bash
# repeat send_one.py n times

function read_register(){
    echo "register_read reg"| /behavioral-model/targets/simple_switch/sswitch_CLI /behavioral-model/targets/simple_switch/chain_uniform_srr.json
    echo "register_read reg_succ_exp"| /behavioral-model/targets/simple_switch/sswitch_CLI /behavioral-model/targets/simple_switch/chain_uniform_srr.json
}

read_register
