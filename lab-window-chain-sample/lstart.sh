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
    echo "> Run client configuration!!"
    sudo docker exec netkit_1000_client /config_run.sh </dev/null &>/dev/null &
    wait
    echo "> Run server configuration!!"
    sudo nohup docker exec netkit_1000_server /config_run.sh </dev/null &>/dev/null &
    wait
    echo "> Run reservoir configuration!!"
    sudo nohup docker exec netkit_1000_reservoir /config_run.sh </dev/null &>/dev/null &
    wait
    echo "> Run switch configuration!!"
    echo "1 - to run window"
    echo "2 - to run chain sample"
    echo "3 - to run chain sample uniform"
    read -p 'What do you want to do ?: ' dovar
    sudo nohup docker exec netkit_1000_switch /config_run.sh $dovar </dev/null &>/dev/null &
    sleep 15
    echo "> ready!!"
    while true; do 
    	read -p "Press crtl+c to end the lab! " exit_str
    done
}

run
