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
        ./behavioral-model/targets/$1/$1 -i 0@eth0 -i 1@eth1 -i 2@eth2 --log-console /behavioral-model/targets/$1/$2.json --pcap &
    else
        ./behavioral-model/targets/$1/$1 -i 0@eth0 -i 1@eth1 -i 2@eth2 /behavioral-model/targets/$1/$2.json --pcap &
    fi
    sleep 10
    echo "> no Ready!!"
    if [ $6 = "sswitch_CLI" ]; then
        /behavioral-model/targets/$1/$6 /behavioral-model/targets/$1/$2.json < /behavioral-model/targets/$1/$4.txt
    else
        /behavioral-model/targets/$1/$6 --json /behavioral-model/targets/$1/$2.json < /behavioral-model/targets/$1/$4.txt
    fi
}

function configure_machine(){
    echo "> fix tcpdump!!"
    mv /usr/sbin/tcpdump /usr/bin/tcpdump
    ln -s /usr/bin/tcpdump /usr/sbin/tcpdump
    echo "> install scapy!!"
    cd /scapy
    python3 setup.py install
    cd /
    case $1 in
    1)
        setup_config simple_switch window 16 commands_window nodebug sswitch_CLI
        ;;
    2)
        setup_config simple_switch chain_succ_ordered 16 commands_chain_sample nodebug sswitch_CLI
        ;;
    3)
        setup_config simple_switch chain_uniform_dre 16 commands_chain_sample debug sswitch_CLI
        ;;
    4)
        setup_config simple_switch chain_uniform_sre 16 commands_chain_sample debug sswitch_CLI
        ;;
    5)
        setup_config simple_switch chain_uniform_srr 16 commands_chain_sample debug sswitch_CLI
        ;;
    *)
        echo "> Error!! --> Command not find"
        echo "> Run of default!! --> chain"
        setup_config simple_switch copy_to_cpu 16 commands debug sswitch_CLI
        ;;
    esac
    echo "> Ready!!"
}

configure_machine $1