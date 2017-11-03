#!/bin/bash
# fix tcpdump, intall scapy and run P4

function setup_config(){
	echo "> Compile program P4!!"
	p4c-bm2-ss --p4v $3 /behavioral-model/targets/$1/$2.p4 -o /behavioral-model/targets/$1/$2.json
	echo "> Configure the switch!!"
	sysctl -w net.ipv4.ip_forward=0
	/etc/init.d/procps restart
	echo "> Start the service!!"
	./behavioral-model/targets/$1/$1 -i 0@eth0 -i 1@eth1 /behavioral-model/targets/$1/$2.json --pcap &
	sleep 10
	echo "> no Ready!!"
	/behavioral-model/tools/runtime_CLI.py --json /behavioral-model/targets/$1/$2.json < /behavioral-model/targets/$1/$4.txt
}

function configure_machine(){
	echo "> fix tcpdump!!"
	mv /usr/sbin/tcpdump /usr/bin/tcpdump
	ln -s /usr/bin/tcpdump /usr/sbin/tcpdump
	echo "> install scapy!!"
	cd /scapy
	python setup.py install
	cd /
	setup_config simple_switch copy_to_cpu 14 commands
	echo "> Ready!!"
}

configure_machine