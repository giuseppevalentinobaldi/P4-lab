import socket, string, random

 
class Client():
    
    def __init__(self, name, ip, port, buffer, encode, cs):
        self.name = name
        self.ip = ip
        self.port = port
        self.buffer = buffer
        self.encode = encode 
        self.cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cs.connect((self.ip, self.port))
        
    def send(self):
        self.cs.send(bytes(self.name +" send: "+ self.randomMessage(), self.encode))
        
    def recv(self):
        packet = self.cs.recv(self.buffer)
        return packet.decode()
    
    def randomMessage(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(1024)) 
    
    def close(self):
        self.cs.close()
        
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name
        
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
    client = Client("giuseppe-firefox", "20.0.0.2", 5005, 1024, "utf-8", None)
    check = True
    while check:
        cond = input('Send packet flow? (y/n): ')
        if cond.lower() == "y":
            client.send()
            print (client.recv())
        else:
            check = False
    client.close()

if __name__ == "__main__":
    main()
