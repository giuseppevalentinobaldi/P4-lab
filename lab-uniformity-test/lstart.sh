#!/bin/bash
# run lab

trap ctrl_c INT

function ctrl_c() {
    echo ""
    echo "> exit!!"
    lclean
    exit 1
}

function run(){
    sudo true
    lstart
    echo "> Run switch configuration!!"
    sudo nohup docker exec netkit_1000_switch /config_run.sh </dev/null &>/dev/null &
    sleep 15
    echo "> ready!!"
    while true; do 
    	read -p "Press crtl+c to end the lab! " exit_str
    done
}

run
