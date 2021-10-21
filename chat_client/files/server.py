import socket
import threading
import json
import sys


host = "127.0.0.1"
port = 43333

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
usernames = []
threads = []


def transmit(message):
    # Server transmits message to all clients 
    for client in clients:
        client.send(message.encode("utf-8"))


def private_transmit(client, message):
    # Server sends message to the specified client
    client.send(message.encode("utf-8"))


def end_connection(client):
    # Server ends connection and removes the client from the chat
    index = clients.index(client)
    clients.remove(client)
    client.close()
    username = usernames[index]
    transmit(f"{username} lämnade chatten!")
    print(f"{username} lämnade chatten!")
    usernames.remove(username)
    threads.remove(threads[index])


def operate(client, username):
    while True:
        try:
            message = client.recv(1024)  # Checks if user is connected
            if message == b"ping":
                client.send(b"pong")
            else:
                message = message.decode("utf-8")
                messageObj = json.loads(message)
                # If client uses "/users" private_transmit will print message below
                if messageObj["text"] == "/users":
                    private_transmit(client, "[SERVER]: Användare som är online är: "+(", ".join(usernames))+".")
                else:
                    transmit(f'{username}: {messageObj["text"]}')
        except socket.timeout:
            end_connection(client)
            break
        except:
            end_connection(client)
            print("Exception occured in operate", *sys.exc_info())
            break


def appending(username, client):
    # appends usernames and clients lists
    usernames.append(username)
    clients.append(client)


def obtain():
    while True:
        # Checks if user connected and server accepted if so print
        client, address = server.accept()
        print(f"Gick med i chatten med addressen {str(address)}")

        client.send(b"user")
        username = client.recv(1024).decode("utf-8")
        appending(username, client)
        client.send(b"ready")

        thread = threading.Thread(target=operate, args=(client, username, ))
        thread.start()
        threads.append(thread)

        client.setblocking(False)
        client.settimeout(10)
        # Prints username, server message and the client that just joined
        print(f"Användarens namn är {username}!")
        private_transmit(client, "Välkommen till servern, du kan skriva /users för att se alla användare online.\n")
        transmit(f"{username} gick med i chatten!")


if __name__ == '__main__':
    obtain()
