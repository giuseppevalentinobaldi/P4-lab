#!/usr/bin/env python
from server import Server
import threading


def main():
    server = Server("20.0.0.2", 5005, 1024, 5, None, None, None)
    print("> Server ready!!")
    while True:
        conn = server.accept_connection()
        threading.Thread(target=server.client_thread, args=(conn,),).start()
    server.close()


if __name__ == "__main__":
    main()
