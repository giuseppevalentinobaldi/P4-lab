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
	echo "1 - to run simple router copy to cpu"
	echo "2 - to run simple switch r"
	echo "3 - to run simple switch x"
	read -p 'What do you want to do ?: ' dovar
	sudo docker exec netkit_1000_switch /config_run.sh $dovar
}

run
