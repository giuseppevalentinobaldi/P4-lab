#!/bin/bash
# repeat send_one.py n times

function repeat_send_one(){
read -p 'What do you want to do ?: ' dovar
for i in $(seq 1 $dovar); do
    python send_one.py
done
}

repeat_send_one
