#!/usr/bin/python3
import socket,time

 
class Server():
    
    def __init__(self, ip, port, buffer, listen, cs, conn, addr):
        self.ip = ip
        self.port = port
        self.buffer = buffer
        self.cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cs.bind((self.ip, self.port))
        self.cs.listen(listen)
    
    def client_thread(self, conn):
        while True:
            data = conn.recv(self.buffer)
            if not data:
                break
            time.sleep(.15)
            conn.send(bytes("ack", "utf-8"))
        conn.close()
    
    def accept_connection(self):
        self.conn, self.addr = self.cs.accept()
        print("[-] Connected to " + self.addr[0] + ":" + str(self.addr[1]))
        return self.conn
        
    def send(self, msg):
        self.conn.send(bytes(msg, "utf-8"))
        
    def recv(self):
        packet = self.conn.recv(self.buffer)
        return packet.decode()
    
    def close(self):
        self.cs.close()
        
    def getIp(self):
        return self.ip
    
    def setIp(self, ip):
        self.ip = ip
        
    def getPort(self):
        return self.port
    
    def setPort(self, port):
        self.port = port
    
    def getBuffer(self):
        return self.buffer
    
    def setBuffer(self, buffer):
        self.buffer = buffer


def main():
    server = Server("20.0.0.2", 5005, 1024, 5, None, None, None)
    server.accept_connection()
    while True:
        data = server.recv()
        if not data: 
            break
        print ("received ", data)
        server.send("ack")
    server.close()


if __name__ == "__main__":
    main()
