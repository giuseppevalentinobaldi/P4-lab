#!/usr/bin/env python
from client import Client
from _thread import start_new_thread


def main():
    CLIENT_NAME = ["giuseppe", "marco", "fabio", "nicola"]
    NUMBER_MSG = 200
    
    for user in CLIENT_NAME:
        client = Client(user + "-firefox", "20.0.0.2", 5005, 1024, None)
        start_new_thread(server.client_thread, (NUMBER_MSG))


if __name__ == "__main__":
    main()
