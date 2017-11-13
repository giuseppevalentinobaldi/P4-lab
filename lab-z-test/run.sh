#!/bin/bash
# run lab

trap ctrl_c INT

function ctrl_c() {
        echo "> exit!!"
	lclean
}

function run(){
	lstart
	echo "> Run client configuration!!"
	sudo docker exec netkit_1000_client /config_run.sh
	echo "> Run server configuration!!"
	sudo docker exec netkit_1000_server /config_run.sh
	echo "> Run reservoir configuration!!"
	sudo docker exec netkit_1000_reservoir /config_run.sh
	echo "> Run switch configuration!!"
	sudo docker exec netkit_1000_switch /config_run.sh 2
}

run
