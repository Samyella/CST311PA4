#!/usr/bin/python

"""Chat server for CST311 Programming Assignment 4 - Group Chat"""
__author__ = "[team 7]"
__credits__ = ["Kate Liu", "Samuel Caesar"]

import socket as s
import threading
import logging
import os

logging.basicConfig(format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

client_names = ['Client X', 'Client Y', 'Client Z']  # Updated for 3 clients
name_index = 0

def connection_handler(connection_socket, client_name, connections):
    try:
        while True:
            data = connection_socket.recv(1024)
            if not data:
                log.info(f"{client_name} disconnected.")
                break
            message = data.decode()
            log.debug(f"Message from {client_name}: {message}")
            if message == 'bye':
                notify = f'{client_name} has left the chat.'.encode()
                for conn in connections:
                    if conn != connection_socket:
                        conn.sendall(notify)
                break
            else:
                for conn in connections:
                    if conn != connection_socket:
                        conn.sendall(f"{client_name}: {message}".encode())
    finally:
        connection_socket.close()
        connections.remove(connection_socket)
        if not connections:
            log.info("No more clients connected.\n")
            shutdown_server()

def shutdown_server():
    log.info("Returning to command prompt...")
    os._exit(0)

def main():
    server_ip = '10.0.2.2'  # Updated to match h4's IP address
    Port = 12001
    server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    server_socket.bind((server_ip, Port))
    server_socket.listen(3)  # Updated to allow 3 clients
    log.info(f"The server is listening on {server_ip} port {Port}")

    connections = []
    global name_index
    while True:
        if len(connections) < 3:  # Allow 3 clients
            connection_socket, addr = server_socket.accept()
            client_name = client_names[name_index % 3]  # Updated for 3 clients
            name_index += 1
            connections.append(connection_socket)
            log.info(f"{client_name} connected from {addr}")
            thread = threading.Thread(target=connection_handler, args=(connection_socket, client_name, connections))
            thread.daemon = True
            thread.start()

    server_socket.close()

if __name__ == "__main__":
    main()
