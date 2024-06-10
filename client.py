import socket
import select
import msvcrt

from server import SERVER_PORT

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect(("127.0.0.1", SERVER_PORT))

msg = input("Enter your name: ")
while True:
    # Send the name to the server
    my_socket.send(f"NAME: {msg}".encode())
    data = my_socket.recv(1024).decode()
    print(data)

    while True:
        data = my_socket.recv(1024).decode().strip()
        if not data:
            print("Connection closed by server")
            break
        messages = data.split("\n")
        for message in messages:
            if message == "INPUT":
                msg = input()
                # msg = '0' # For quick testing
                my_socket.send(msg.encode())
            else:
                print(message)
