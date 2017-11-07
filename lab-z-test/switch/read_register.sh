#!/bin/bash
# repeat send_one.py n times

function read_register(){
read -p 'What is the name of the register you want to read ?: ' dovar
echo "register_read $dovar"| /behavioral-model/targets/simple_switch/sswitch_CLI /behavioral-model/targets/simple_switch/r.json
}

read_register
