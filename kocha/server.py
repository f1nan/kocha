"""
Modul mit Klassen und Methoden für den KOCHA-Server.
"""

import json
import locale
import socket
import threading

from . import shared


class KochaTcpConnection(shared.KochaTcpSocketWrapper):
    """
    Klasse kapselt die Verbindung einens KOCHA-Clients mit dem
    KOCHA-Server.
    """

    def __init__(self, socket, address):
        """
        Intialisiert ein Object der Klasse KochaTcpConnectionWrapper.

        Args:
            socket: Das socket-Object des KochaTcpClients.
            address: Die Adressinformationen des KochaTcpClients.
        """
        self.address = address
        super().__init__(socket)


class KochaTcpServer(shared.KochaTcpSocketWrapper):
    """
    Der KochaTcpServer kommuniziert mit den KOCHA-Clients via TCP/IP.
    Er stellt den Clients mithilfe von Kommandos bestimmte
    Funktionalitaeten zur Verfuegung. Der KochaTcpServer nutzt Threads
    um mehrere Clients gleichzeitig bedienen zu koennen.
    """

    KOCHA_WELCOME_MESSAGE = (
        "Hello {}! Welcome to the KOCHA chat. Type /h or /help to dispaly a "
        "list of available commands.")
    """
    Die Willkommensnachricht des KOCHA-Servers.
    """

    KOCHA_HELP_CONTENT = (
        "List of available commands:\n"
        "/h or /help          -- Show this list\n"
        "/q or /quit          -- Exit the KOCHA chat\n"
        "/m or /members       -- Show a list of all registered users\n"
        "/dm <user> <message> -- Write a direct message")
    """
    Liste aller verfuegbaren Kommandos, die beim Aufruf der Hilfe
    gezeigt wird.
    """

    def __init__(self, host="", port=9999):
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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Den erstellten Socket an die uebergene IP-Adresse und den
        # uebergebene Port binden
        sock.bind((self.host, self.port))

        # Server gestatten Verbindungen anzunehmen
        sock.listen(5)

        # Socket merken
        super().__init__(sock)

    def loop(self):
        """
        Auf eingehenden Verbindungen von KOCHA-Clients warten und diese
        jweils in einem eigenen Thread bearbeiten.
        """
        while not self.stop:
            # Auf eine eingehende Clientverbindung warten
            client_socket, address = self.socket.accept()

            # Timeout fuer den Client-Socket setzen
            client_socket.settimeout(shared.KOCHA_TIMEOUT)

            # Die Verbinungsdaten des Clients kapseln
            client = KochaTcpConnection(client_socket, address)

            print("Connection from", client.address)

            # Die Anfragen des Clients in einem eigen Thread bearbeiten
            handler = threading.Thread(
                target=self.handle, args=(client,), daemon=True)
            self.handlers.append(handler)
            handler.start()

    def handle(self, client):
        """Methode zur Bearbeitung der Anfragen eines KOCHA-Clients.

        Args:
            client: Die Daten der Clientverbindung.
        """
        while not self.stop:
            # Auf eine Anfrage des Clients warten
            request = None
            try:
                request = client.receive()
            except socket.timeout:
                continue
            except:
                # Den Client abmelden, da der Socket 
                # hoechstwahrscheinlich von der anderen Seite einfach
                # geschlossen wurde
                self.on_quit(client)
                break

            # Wenn der Client unbekannt ist, Anmeldung am Server
            # versuchen
            if client not in self.clients:
                self.try_login(client, request.content)

                # Auf naechste Anfrage des Clients warten
                continue

            # Die Anfrage des Clients interpretieren und bearbeiten
            if (request.content == "/h" or request.content == "/help"):
                # Dem KOCHA-Client die Kommandouebersicht schicken
                self.on_help(client)
            elif (request.content == "/q" or request.content == "/quit"):
                # TODO: Den Client vom Server abmelden
                self.on_quit(client)
                break
            elif (request.content == "/m" or request.content == "/members"):
                # TODO: Dem Client eine Liste mit allen angemeldeten
                # Clients geben
                self.on_members(client)
            elif (request.content.startswith("/dm ")):
                # Einem anderen Client eine direkte Nachricht
                # weiterleiten
                self.on_dm(client, request)
            else:
                # Die Nachricht im Chat veröffentlichen
                self.on_broadcast(client, request)

    def try_login(self, client, content):
        """
        Einen KOCHA-Client am KOCHA-Server anmelden.

        Args:
            client: Die Daten der Clientverbindung.
            content: Der Inhalt der Nachricht.
        """
        command, alias, *_ = content.split()
        content = ""
        if command == "/login":
            if (not set(": ").issubset(alias)
                    and alias not in self.clients.values()
                    and alias != shared.KOCHA_SERVER_ALIAS):
                self.clients[client] = alias
                content = self.KOCHA_WELCOME_MESSAGE.format(alias)

        response = shared.KochaMessage(
            content=content,
            sender=shared.KOCHA_SERVER_ALIAS,
            is_dm=True)
        client.send(response)

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
            client.close()

        # Den TCP-Socket des KOCHA-Servers herunterfahren und
        # anschließend die Verbindung zum Socket schließen
        self.socket.shutdown(socket.SHUT_RDWR)
        super().close()

    def on_members(self, client):
        """
        Dem anfragenden Client eine durch Kommata getrennte Liste aller
        am KOCHA-Server angemeldeten Clients liefern.

        Args:
            client: Die Daten der Clientverbindung.
        """
        content = ", ".join(
            self.clients[cli] for cli in self.clients if cli != client)
        response = shared.KochaMessage(
            content=content,
            sender=shared.KOCHA_SERVER_ALIAS)
        client.send(response)

    def on_broadcast(self, client, message):
        """
        Die Nachricht des Clients im Chat veroeffentlichen.

        Args:
            client: Die Daten der Clientverbindung
            message: Das KochaMessage-Object.
        """
        for cli in self.clients:
            if cli != client:
                cli.send(message)

    def on_dm(self, client, message):
        """
        Einem anderen Client eine direkte Nachricht senden.

        Args:
            client: Die Daten der Clientverbindung.
            message: Das KochaMessage-Object.
        """
        addressed_alias, content = "", ""
        try:
            _, addressed_alias, content = message.content.split()
        except ValueError:
            return

        # Wenn Sender auch Empfaenger ist, nix machen
        if message.sender == addressed_alias:
            return

        for cli in self.clients:
            alias = self.clients[cli]
            if alias == addressed_alias:
                message.content = content
                message.is_dm = True

                cli.send(message)
                return

    def on_quit(self, client):
        """
        Den Client am KOCHA-Server abmelden.
        """
        # Die Clientverbindung schließen
        client.close()

        print("Closed connection of {!r}".format(client.address))

        # Den Client aus der Liste der angemeldenten Clients entfernen
        del self.clients[client]

    def on_help(self, client):
        """
        Dem anfragenden Client eine Ueberischt aller Befehle schicken.
        """
        response = shared.KochaMessage(
            content=self.KOCHA_HELP_CONTENT, sender=shared.KOCHA_SERVER_ALIAS)
        client.send(response)


if __name__ == "__main__":
    # Das Gebietsschema auf die Standardeinstellung des Benutzers setzen
    locale.setlocale(locale.LC_ALL, "")

    # Den KochaTcpServer auf Port 9090 starten
    try:
        server = KochaTcpServer()
        server.loop()
    except KeyboardInterrupt:
        server.close()
