#!/usr/bin/env python

import socket


print "Startup Server..."

# dichiarazione variabili
TCP_IP = '20.0.0.2'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response
count = 1

# creazione socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# attesa di connessioni
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print "Server run!"

# accettazione connessione dal client
while 1:
	print "Waiting for connections..."

	conn, addr = s.accept()

	print "Connection address:", addr

	# ricezione messaggi dal client
	while 1:
		data = conn.recv(BUFFER_SIZE)
		if not data: break

		print "received data: ", data

		#ack = "ACK "+ str(count)
		#conn.send(ack)  # ack
		#count += 1
		#print "send :", ack

	#count = 0
	print "Close connection with: ", addr


print "Stop Server!"

conn.close()
