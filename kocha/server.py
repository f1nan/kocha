"""
Modul mit Klassen und Methoden für den KOCHA-Server.
"""

import json
import threading
from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM

from utils import JsonUtils
from utils import KochaMessage


class KochaTcpClientWrapper:
    """
    Klasse kapselt die Verbindung zu einem KochaTcpClient.
    """

    def __init__(self, socket, address):
        """
        Initialisiert ein Object der Klasse KochaTcpClientWrapper.

        Args:
            socket: Das socket-Object des KochaTcpClients.
            address: Die Adressinformationen des KochaTcpClients.
        """
        self.socket = socket
        self.address =address


class KochaTcpServer:

    """
    Der KochaTcpServer kommuniziert mit den KOCHA-Clients via TCP/IP.
    Er stellt den Clients mithilfe von Kommandos bestimmte
    Funktionalitaeten zur Verfuegung. Der KochaTcpServer nutzt Threads
    um mehrere Clients gleichzeitig bedienen zu koennen.
    """

    BUFFER_SIZE = 4096
    """
    Die maximale Anzahl an Bytes die auf einmal empfangen werden kann.
    """

    def __init__(self, host="", port=36037):
        """
        Initialisiert ein Object der Klasse KochaTcpServer.

        Args:
            host: Der Host des KOCHA-Servers.
            port: Der Port auf dem KOCHA-Server lauscht.
        """
        # Host und Port des KOCHA-Servers merken
        self.port = port
        self.host = host

        # Set zum Speichern der Clientverbindungen initialisieren
        self.clients = {}

        # Liste mit allen Threads zur Bearbeitung der Clientanfragen
        # initialisieren
        self.handlers = []

        # Signal zum Herunterfahren des KochaTcpServers
        self.stop = False

        # Einen TCP-Socket für den KOCHA-Server erstellen
        self.socket = socket(AF_INET, SOCK_STREAM)

        # Den erstellten Socket an die uebergene IP-Adresse und den
        # uebergebene Port binden
        self.socket.bind((self.host, self.port))

        # Server gestatten Verbindungen anzunehmen
        self.socket.listen(5)

    def loop(self):
        """
        Auf eingehenden Verbindungen von KOCHA-Clients warten und diese
        jweils in einem eigenen Thread bearbeiten.
        """
        while not self.stop:
            # Auf eine eingehende Clientverbindung warten
            client_socket, address = self.socket.accept()

            # Die Verbinungsdaten des Clients kapseln
            client = KochaTcpClientWrapper(client_socket, address)

            print("Connection from", client.address)

            # Die Anfragen des Clients in einem eigen Thread bearbeiten
            handler = threading.Thread(target=self.handle, args=(client,))
            self.handlers.append(handler)
            handler.start()

    def handle(self, client):
        """Methode zur Bearbeitung der Anfragen eines KOCHA-Clients.

        Args:
            client: Die Daten der Clientverbindung.
        """
        while not self.stop:
            # Daten vom Client in Form eines Bytes-Objects empfangen.
            json_data = client.recv(self.BUFFER_SIZE)

            # Wenn keine Daten empfange wurden, die Bearbeitung der
            # Anfragen dieses Clients abbrechen
            if not json_data:
                break

            # Die empfangenen Daten deserialisieren
            message = JsonUtils.to_kocha_message(json_data)

            # Wenn der Client unbekannt ist, Anmeldung am Server
            # versuchen
            if client not in self.clients:
                self.try_login(client, message.content)

                # TODO: Aktion bei Misserfolg stimmt nicht!
                # Wenn die Anmeldung gescheitert ist, keine weiteren
                # Anfragen dieses Clients bearbeiten
                if client not in self.clients:
                    break

                # Bei erfolgreicher Anmeldung auf die naechste Anfrage
                # des Clients warten
                continue

            if (message.content.startswith("/h ")
                or message.content.startswith("/help ")):
                # Dem KOCHA-Client die Kommandouebersicht schicken
                self.on_help(client)
            elif (message.content.startswith("/dm ")):
                # Einem anderen Client eine direkte Nachricht
                # weiterleiten
                try:
                    self.on_dm(client, message)
                except ValueError:
                    # TODO: Dem Client die Hilfe für das /dm- Kommando
                    # schicken
                    pass
            elif (message.content.startswith("/q ")
                  or message.content.startswith("/quit ")):
                # TODO: Den Client vom Server abmelden
                self.on_quit(client)
                break
            elif (message.content.startswith("/l ")
                  or message.content.startswith("/list ")):
                # TODO: Dem Client eine Liste mit allen angemeldeten
                # Clients geben
                self.on_list(client)
            else:
                # Die Nachricht im Chat veröffentlichen
                self.on_broadcast(client, message)

        print("Closed connection of " + client.address)

    def try_login(self, client, content):
        """
        Einen KOCHA-Client am KOCHA-Server anmelden.

        Args:
            client: Die Daten der Clientverbindung.
            content: Der Inhalt der Nachricht.
        """
        command, alias, *_ = message.content.split()
        if command == "/login":
            if alias not in self.clients.values():
                self.clients[client] = alias

    def close(self):
        """
        Den KochaTcpServer herunterfahren und schließen.
        """
        # Alle handler-Threads beenden
        self.stop = True
        for handler in self.handlers:
            handler.join()

        # Alle Clientverbindungen schließen
        for client in self.clients:
            client.socket.close()

        # Den TCP-Socket des KOCHA-Servers herunterfahren und
        # anschließend die Verbindung zum Socket schließen
        self.socket.shutdown()
        self.socket.close()

    def on_list(self, client):
        """
        Dem anfragenden Client eine Liste aller am KOCHA-Server
        angemeldeten Clients liefern.

        Args:
            client: Die Daten der Clientverbindung.
        """
        # TODO: Methode on_list implementieren

    def on_broadcast(self, client, message):
        """
        Die Nachricht des Clients im Chat veroeffentlichen.

        Args:
            client: Die Daten der Clientverbindung
            message: Das KochaMessage-Object.
        """
        # TODO: Methode on_broadcast implementieren

    def on_dm(self, client, message):
        """
        Einem anderen Client eine direkte Nachricht senden.

        Args:
            client: Die Daten der Clientverbindung.
            message: Das KochaMessage-Object.
        """
        # TODO: Methode on_dm implementieren

    def on_quit(self, client):
        """
        Den Client am KOCHA-Server abmelden.
        """
        # Die Clientverbindung schließen
        client.socket.close()

        # Den Client aus der Liste der angemeldenten Clients entfernen
        del self.clients[client]

    def on_help(self, client):
        """
        Dem anfragenden Client eine Ueberischt aller Befehle schicken.
        """
        # TODO: Methode on_help implementieren


if __name__ == "__main__":
    try:
        server = KochaTcpServer()
        server.loop()
    except KeyboardInterrupt:
        server.close()
