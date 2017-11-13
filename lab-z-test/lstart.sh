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
	#/config_run.sh 1 run copy_to_cpu.p4
	#/config_run.sh 2 run r.p4
	#/config_run.sh 3 run x.p4
	sudo docker exec netkit_1000_switch /config_run.sh 2
}

run
