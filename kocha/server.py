import json
import threading

from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM

from parameter import Parameter
from payload import Payload, as_payload


class ClientWrapper:

    def __init__(self, socket, address):
        self.socket = socket
        self.address =address


class Server:

    """A simple chat server."""

    BUF_SIZE = 1024

    def __init__(self, ip_addr="", port=30000):
        self.port = port
        self.ip_addr = ip_addr

        self.actions = dict()
        self.actions[b"/ping"] = self.on_ping
        self.actions[b"/members"] = self.on_members

        self.clients = dict()

        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((self.ip_addr, self.port))
        self.socket.listen(True)

    def run(self):
        """Wait for incoming connections and handle them."""
        while True:
            # Wait for an incoming connection. Return a new socket
            # representing the connection, and the address of the client.
            client_socket, address = self.socket.accept()
            client = ClientWrapper(client_socket, address)

            print("Connection from", client.address)

            # Handle each client's request in a separate thread
            t = threading.Thread(target=self.handle, args=(client,))
            t.start()

    def handle(self, client):
        """Handles a connection.

        Args:
            client: The client.
        """
        while True:
            # Receive data from the client. Data is a bytes object.
            data = client.recv(self.BUF_SIZE)
            if not data:
                break

            # Deserialize the received data
            payload = json.loads(data, object_hook=as_payload)

            # Handle duplicate username and remember client if it's
            # unknown to the server
            try:
                if client != self.clients[payload.user]:
                    print("Username is already taken")
                    break
            except KeyError:
                self.clients[payload.user] = client

            # Get an action based on the received payload
            action = self.dispatch_action(payload)

            # Execute the action with the given parameters
            parameter = Parameter(client, payload)
            action(parameter)

        print("Connection closed")

    def dispatch_action(self, payload, default_action=None):
        """Dispatches a server action based on the received payload.

        Args:
            payload (Payload): The payload.
            default_action (callable): The default action.

        Returns:
            callable: An action.
        """
        if default_action is None:
            default_action = self.on_chat_message

        return self.actions.get(payload.content.lower(), default_action)

    def close(self):
        """Close the server's socket."""
        self.socket.close()

    def on_ping(self, parameter):
        """Send pong back.

        Args:
            parameter (Parameter): The parameter for the action.
        """
        socket = parameter.client.socket
        socket.sendall(b"pong\r\n")

    def on_members(self, parameter):
        """Send a list of all chat members back.

        Args:
            parameter (Parameter): The parameter for the action.
        """
        socket = parameter.client.socket
        parameter.client.sendall("{!r}\r\n".format(self.clients).encode())

    def on_chat_message(self, parameter):
        """Broadcast message to all other clients.

        Args:
            parameter (Parameter): The parameter for the action.
        """
        for client in self.clients.items():
            if client != parameter.client:
                socket = client.socket
                socket.sendall(json.dumps(

if __name__ == "__main__":
    try:
        server = Server("", 25000)
        server.run()
    except KeyboardInterrupt:
        server.close()
