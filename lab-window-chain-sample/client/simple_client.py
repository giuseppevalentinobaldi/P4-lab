 #!/usr/bin/env python
 
import socket, random, string 
from time import sleep

# dichiarazione ed inizializzazione variabili
TCP_IP = '20.0.0.2'
TCP_PORT = 5005
BUFFER_SIZE = 20
MAX_PACKET_SEND = 10000000
count = 1

# creazione socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connessione al server
s.connect((TCP_IP, TCP_PORT))

print ("Connection server!")

# invio messaggi
while count <= MAX_PACKET_SEND:
	s.send(bytes("giuseppe@giuseppe-ThinkPad-E550: " + str(count) + "\n" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(512)), "utf-8"))
	# print "Send packet: ", count
	print (str(count))
	count += 1

	# data = s.recv(BUFFER_SIZE)
	# print "received data: ", data
	sleep(0.004)

print("Close connection!")

# chiusura socket
s.close()
