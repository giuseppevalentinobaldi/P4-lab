#!/usr/bin/env python
from server import Server
from _thread import start_new_thread


def main():
    server = Server("20.0.0.2", 5005, 1024, 5, None, None, None)
    while True:
        conn = server.accept_connection()
        start_new_thread(server.client_thread, (conn))
    server.close()


if __name__ == "__main__":
    main()
