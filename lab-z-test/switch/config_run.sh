#!/bin/bash
# fix tcpdump, intall scapy and run P4

function setup_config(){
	echo "> Compile program P4!!"
	p4c-bm2-ss --p4v $3 /behavioral-model/targets/$1/$2.p4 -o /behavioral-model/targets/$1/$2.json
	echo "> Configure the switch!!"
	sysctl -w net.ipv4.ip_forward=0
	/etc/init.d/procps restart
	echo "> Start the service!!"
	if [ $5 = "debug" ]; then
        ./behavioral-model/targets/$1/$1 -i 0@eth0 -i 1@eth1 --log-console /behavioral-model/targets/$1/$2.json --pcap &
    else
        ./behavioral-model/targets/$1/$1 -i 0@eth0 -i 1@eth1 /behavioral-model/targets/$1/$2.json --pcap &
    fi
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
	echo "1 - to run simple switch copy to cpu"
	echo "2 - to run simple switch alg r"
	read -p 'What do you want to do ?: ' dovar
	case $dovar in
     1)
     	setup_config simple_switch copy_to_cpu 14 commands nodebug
        ;;
     2)
		setup_config simple_switch r 16 commands_r debug
        ;;
     *)
        echo "> Error!! -->command not find "
        ;;
	esac
	echo "> Ready!!"
}

configure_machine