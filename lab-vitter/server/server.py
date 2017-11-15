import socket

 
class Server():
    
    def __init__(self, ip, port, buffer, encode, cs, conn, addr):
        self.ip = ip
        self.port = port
        self.buffer = buffer
        self.encode = encode
        self.cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cs.bind((self.ip, self.port))
        self.cs.listen(1)
        self.conn, self.addr = self.cs.accept()
        
    def send(self):
        self.conn.send(bytes("ack", self.encode))
        
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
        
    def getEncode(self):
        return self.encode
    
    def setEncode(self, encode):
        self.encode = encode

def main():
    server = Server("20.0.0.2", 5005, 1024, "utf-8", None, None, None)
    while 1:
        data = server.recv()
        if not data: 
            break
        print ("received ", data)
        server.send()
    conn.close()

if __name__ == "__main__":
    main()