#!/usr/bin/python3
from client import Client
import threading


def main():
    users = ["giuseppe", "marco", "fabio", "nicola"]
    msg = 12000000
    
    for user in users:
        client = Client(user + "-firefox", "20.0.0.2", 5005, 1024, None)
        threading.Thread(target=client.client_thread, args=(msg,),).start()


if __name__ == "__main__":
    main()
