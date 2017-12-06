#!/bin/bash
# repeat send_one.py n times

function read_register(){
    read -p 'What is the name of the register you want to read ?: ' dovar
    read -p 'What is the name of the json file ?: ' json
    echo "register_read $dovar"| /behavioral-model/targets/simple_switch/sswitch_CLI /behavioral-model/targets/simple_switch/$json.json
}

read_register
