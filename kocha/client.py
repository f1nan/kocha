"""
Modul mit Klassen und Methoden fuer den KOCHA-Client.
"""

import curses
import enum
import locale
import queue
import socket
import sys
import threading
import time

from kocha import shared


class KochaTcpClient(shared.KochaTcpSocketWrapper):
    """
    Klasse fuer die Kommunikation mit dem KOCHA-Server via TCP/IP.
    """

    def __init__(self, server_host, server_port):
        # Einen TCP-Socket fuer den KOCHA-Client erstellen
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Timeout fuer den Client-Socket setzen
        sock.settimeout(shared.KOCHA_TIMEOUT)

        # Der Alias
        self.alias = ""

        # Mit dem KOCHA-Server verbinden
        self.is_connected = True
        try:
            sock.connect((server_host, server_port))
        except Exception as e:
            print(e, file=sys.stderr)
            self.is_connected = False

        # Den Client-Socket merken
        super().__init__(sock)

    def send(self, message):
        """
        Eine Nachricht an den KOCHA-Server schicken.

        Args:
            message: Die Nachricht.
        """
        # Wenn nicht angemeldet, nix machen
        if not self.alias:
            return

        super().send(message)

    def close(self):
        """
        Den KochaTcpClient herunterfahren und schließen.
        """
        self.socket.shutdown(socket.SHUT_RDWR)
        super().close()

    def try_login(self, alias):
        """
        Versuchen den Client mit einem Alias Am KOCHA-Server anzumelden.

        Args:
            alias: Der Alias fuer die Anmeldung.
        Returns:
            Die Antwort des KOCHA-Servers
        """
        answer = None

        # Wenn nicht mit dem KOCHA-Server verbunden, nix machen
        if self.is_connected:

            # Loginanfrage an den KOCHA-Server senden
            request = shared.KochaMessage(content="/login " + alias)
            data = shared.JsonUtils.to_json(request)
            self.socket.sendall(data.encode())

            # Auf Antwort des KOCHA-Servers warten (maximal 5 Versuche)
            count = 0
            while answer is None and count < 5:
                try:
                    answer = self.receive()
                except socket.timeout:
                    pass

                count += 1

            # Wenn die Anmeldung erfolgreich war den Alias setzen
            if answer is not None:
                if answer.content != "":
                    self.alias = alias

        return answer

@enum.unique
class KochaUiColorPair(enum.IntEnum):
    """
    Enumeration mit Bezeichnern fuer Farbpaare.
    """

    DM = 1
    """
    Bezeichner fuer das Farbpaar zur Hervorhebung des eigenen Namens
    und direkter Nachrichten.
    """

    SERVER = 2
    """
    Bezeichner fuer das Farbpaar zur Hervorhebung von Servernachrichten.
    """


class KochaUi:
    """
    Klasse fuer das User Interface des KOCHA-Clients.
    """

    def __init__(
        self,
        kocha_tcp_client,
        stdscr=None,
        prompt="> ",
        welcome_message=None):
        """
        Initialisert ein Object der Klasse KochaUi.

        Args:
            stdscr: Window-Object, das den gesamten Bilschirm
            repraesentiert.
            prompt: Das Zeichen fuer die Eingabeaufforderung.
        """
        # Den kocha_tcp_client merken
        self.kocha_tcp_client = kocha_tcp_client

        # Das Zeichen fuer die Eingabeaufforderung merken
        self.prompt = prompt

        # Puffer fuer die Nachrichten initialisieren
        self.messages = []

        # Puffer fuer die Texteingabe initialisieren
        self.input = ""

        # Signal zum schließen des KOCHA-Clients
        self.stop = False

        if stdscr is None:
            # Die curses Bibliothek initialisieren, falls kein
            # Hauptfenster uerbgeben wurde
            self.stdscr = curses.initscr()

            # Zeichen nicht automatisch auf dem Bildschirm ausgeben
            curses.noecho()

            # Bei jeder Eingabe reagieren und nicht nur wenn Enter
            # gedrueckt wird
            curses.cbreak()
        else:
            # Das Haupfenster merken
            self.stdscr = stdscr

        # Farbschemata anlegen
        self.has_colors = False
        if (curses.has_colors()):
            # Initialisiert 8 Grundfarben (schwarz, rot, gruen, gelb,
            # blau, magenta, cyan und weiß) und muss aufgerufen werden
            # bevor andere Farbmanipulationen ausgefuehrt werden
            curses.start_color()

            # Farbschema zur Hervorhebung des eigenen Namens und
            # direkter Nachrichten anlegen
            curses.init_pair(
                KochaUiColorPair.DM,
                curses.COLOR_RED,
                curses.COLOR_BLACK)

            # Farbschema zur Hervorhebung von Servernachrichten
            curses.init_pair(
                KochaUiColorPair.SERVER,
                curses.COLOR_BLUE,
                curses.COLOR_BLACK)

            self.has_colors = True

            # Die Wilkommensnachricht, darf nur angehaengt werden, wenn
            # fest steht, dass das Terminal Farben unterstuetzt
            if welcome_message is not None:
                self.messages.append(welcome_message)

        # Titel des Programms zeichnen (Hintergrund- und Vordergundfarbe
        # vertauscht)
        self.draw_title()

        # Das Nachrichtenfenster erstellen und zeichnen
        self.messages_window = curses.newwin(
            curses.LINES - 4, curses.COLS, 1, 0)
        self.draw_messages_window()

        # Das Fenster fuer Benuterzeingaben erstellen und zeichnen
        self.input_window = curses.newwin(
            3, curses.COLS, curses.LINES - 3, 0)
        self.draw_input_window()

        # Sonderzeichen wie Pfeiltasten von curses abfangen lassen
        self.input_window.keypad(True)

        # Die Ansicht aktualisieren
        self.refresh()

        # Den Worker-Thread zum Empfangen von Nachrichten starten
        self.receive_messages_worker = threading.Thread(
            target=self.receive_messages, daemon=True)
        self.receive_messages_worker.start()

    def close(self):
        """
        Wird beim Schließen des User Interfaces aufgerufen. Meldet den
        Client am Server ab und stellt den Ursprungszustand des
        Terminals wieder her.
        """
        # Warten bis der Worker-Thread terminiert
        self.receive_messages_worker.join()

        # Den KochaTcpClient schließen
        self.kocha_tcp_client.close()

        # Terminaleinstellungen fuer curses wieder aufheben
        curses.nocbreak()
        self.input_window.keypad(False)
        curses.echo()

        # Terminal in urspruenglichen Beriebsmodus zuruecksetzen
        curses.endwin()

    def loop(self):
        """
        Wartet auf Nutzereingaben und verarbeitet diese in einer
        Endlosschleife.
        """
        while not self.stop:
            # Auf Nutzereingabe warten und diese verarbeiten
            c = self.input_window.getch()

            if c == ord("\n"):
                # Zeilenende ohne sonstige Eingabe ignorieren
                if self.input == "":
                    continue

                # Bei /q oder /quit Programm beenden
                if self.input.lower() in { "/q", "/quit" }:
                    self.stop = True

                # Ein Message-Object erstellen
                message = shared.KochaMessage(
                    content=self.input,
                    sender=self.kocha_tcp_client.alias)

                # Nachricht zum Nachrichtenpuffer hinzufuegen
                self.messages.append(message)

                # Eingabepuffer zuruecksetzen
                self.input = ""

                # Nachrichtenfenster und Eingabefenster neu zeichnen
                self.draw_messages_window()
                self.draw_input_window()

                # Message an den KOCHA-Server uerbermitteln
                self.kocha_tcp_client.send(message)

            elif c == curses.KEY_BACKSPACE or c == 127:
                # Bei Ruecktaste zuvor eingegebenes Zeichen entfernen
                self.input = self.input[:-1]

                # Eingabefenster neu zeichnen
                self.draw_input_window()

            elif c == curses.KEY_RESIZE:
                # Groesse des Interface an die neue Groesse des
                # Terminals anpassen
                self.resize()

            elif 31 < c and c <= 126:
                # Druckbare ASCII-Zeichen anhaengen
                self.input += chr(c)

                # Eingabefenster neu zeichnen
                self.draw_input_window()

            # Ansicht aktualisieren
            self.refresh()

        # KOCHA-Client am Server abmelden und UI schließen
        self.close()

    def draw_messages_window(self):
        """
        Zeichnet das Nachrichtenfenster.
        """
        # Das Nachrichtenfenster leeren
        self.messages_window.clear()

        # Einen Rahmen um das Nachrichtenfenster zeichnen
        self.messages_window.box()

        # Abmessungen des Nachrichtenfensters holen
        max_y, max_x = self.messages_window.getmaxyx()

        # Breite des Rahmens abziehen
        max_y, max_x = max_y - 2, max_x - 2

        # Nachrichten an die Breite des Nachrichtenfensters anpassen
        lines = []
        for message in self.messages:
            line = ""

            # Indikator fuer Direct-Message, Server-Message oder
            # Chat-Message voranstellen
            if message.sender == shared.KOCHA_SERVER_ALIAS:
                line += "[SM]"
            elif message.sender == self.kocha_tcp_client.alias:
                line += "[ME]"
            elif message.is_dm:
                line += "[DM]"
            else:
                line += "[CM]"

            # Sendezeit anhaengen
            line += message.sent_at.strftime("[%H:%M:%S] ")

            # Alias des Senders anhaengen
            line += message.sender + ": "

            # Eigentlichen Nachrichteninhalt anhaengen
            line += message.content

            # Newlines in Zeile verarbeiten
            parts = line.split("\n")

            # Zeilen an die Breite des User Interfaces anpassen
            for part in parts:
                while part != "":
                    lines.append(part[:max_x])
                    part = part[max_x:]

        # Index der aeltesten Nachricht, die im Nachrichtenfenster
        # gezeichnet werden kann, bestimmen
        begin = len(lines) - max_y
        begin = begin if begin >= 0 else 0

        for y, line in enumerate(lines[begin:], start=1):
            # Nachricht ins Nachrichtenfenster zeichnen
            self.messages_window.addstr(y, 1, line)

            # Den Beginn des eigentlichen Inhalts bestimmen (die
            # Startposition ergibt sich aus der Laenge des Headers)
            start_content = line.find(":", 15) + 1

            # Direktnachrichten und Servernachrichten hervorheben
            if line.startswith("[SM]"):
                self.messages_window.chgat(
                    y,
                    1,
                    start_content,
                    curses.color_pair(KochaUiColorPair.SERVER))
            elif line.startswith("[DM]"):
                self.messages_window.chgat(
                    y,
                    1,
                    start_content,
                    curses.color_pair(KochaUiColorPair.DM))

            # Keine Hervorhebung fuer Nachrichten, die man selbst
            # geschrieben hat
            if line.startswith("[ME]"):
                continue

            # Liste fuer die X-Positionen des eigenen Alias anlegen
            alias_x_positions = []

            # Die X-Position des eigenen Aliases in einer Zeile
            # finden
            line_lower = line.lower()
            alias_lower = self.kocha_tcp_client.alias.lower()
            while True:
                alias_x = line_lower.find(alias_lower, start_content)

                # Wenn der Alias nicht auftaucht, abbrechen
                if alias_x == -1:
                    break

                # X-Position des Alias zur Liste hinzufuegen
                alias_x_positions.append(alias_x)
                start_content = alias_x + len(alias_lower)

            # Den eigenen Alias im Nachrichtentext hervorheben
            for alias_x in alias_x_positions:
                self.messages_window.chgat(
                    y,
                    1 + alias_x,
                    len(self.kocha_tcp_client.alias),
                    curses.color_pair(KochaUiColorPair.DM))

    def draw_input_window(self):
        """
        Zeichnet das Fenster zur Eingabe von Text.
        """
        # Eingabefenster leeren
        self.input_window.clear()

        # Einen Rahmen um das Eingabefenster zeichnen
        self.input_window.box()

        # Abemessungen der Eingabezeile holen
        _, max_x = self.input_window.getmaxyx()

        # Breite des Rahmens und des Cursors abziehen
        max_x -= 3

        # Zeichen fuer Eingabeaufforderung und Nutzereingabe
        # zusammensetzen
        text = self.prompt + self.input

        # Zeichenkette vorne abschneiden, wenn sie zu lang ist
        begin = len(text) % max_x
        begin = begin if begin != len(text) else 0

        # Text ins Eingabefenster zeichnen
        self.input_window.addstr(1, 1, text[begin:])

        # Cursorposition aktualisieren
        self.input_window.cursyncup()

    def refresh(self):
        """
        Die Ansicht aktualisieren.
        """
        # Fenster von unterstem zum obersten Layer aktualisieren, damit
        # keine Inhalte verdeckt oder ueberschrieben werden
        self.stdscr.noutrefresh()
        self.messages_window.noutrefresh()
        self.input_window.noutrefresh()

        curses.doupdate()

    def receive_messages(self):
        """
        Nachrichten vom KOCHA-Server empfangen und ins
        Nachrichtenfenster zeichnen.
        """
        while not self.stop:
            try:
                message = self.kocha_tcp_client.receive()

                self.messages.append(message)
                self.draw_messages_window()
                self.refresh()
            except socket.timeout:
                pass

    def draw_title(self):
        """
        Den Titel zeichnen.
        """
        self.stdscr.clear()
        self.stdscr.addstr(
            0, 0, " KOCHA CLIENT " + shared.KOCHA_VERSION, curses.A_REVERSE)
        self.stdscr.chgat(-1, curses.A_REVERSE)

    def resize(self):
        """
        Die Groeße des Kocha-Clients anpassen.
        """
        # Titel neu zeichnen
        self.draw_title()

        # Neue Abmessungen bestimmen
        max_y, max_x = self.stdscr.getmaxyx()

        # Die Groesse des Nachrichtenfensters anpassen und neu zeichnen
        self.messages_window.resize(max_y - 4, max_x)
        self.draw_messages_window()

        # Postion und Groeße des Eingabefensters anpassen und
        # Eingabefenster neu zeichnen
        self.input_window.mvwin(max_y - 3, 0)
        self.input_window.resize(3, max_x)
        self.draw_input_window()

    @staticmethod
    def show():
        """
        Wird aufgerufen um das User Interface fuer den KOCHA-Client
        aufzurufen.
        """
        # Das Gebietsschema auf die Standardeinstellung des Benutzers
        # setzen
        locale.setlocale(locale.LC_ALL, "")

        # Kommandozeilenparameter verarbeiten
        if (len(sys.argv) != 3):
            print("Usage: python3 -m kocha.client SERVER_HOST SERVER_PORT")
            return 1

        server_host = sys.argv[1]
        server_port = int(sys.argv[2])

        # Eine Instanz des KochaTcpClients erstellen und mit dem Server
        # verbinden
        kocha_tcp_client = KochaTcpClient(
            server_host=server_host, server_port=server_port)
        if not kocha_tcp_client.is_connected:
            print("Couldn't connect with KOCHA-Server. Did you provide the"
                 "correct host and port? Is the KOCHA-Server running?")
            return 1

        # Mit dem Client am KOCHA-Server anmelden
        welcome_message = None
        while not kocha_tcp_client.alias:
            # Alias vom Benutzer holen
            alias = input("Enter alias: ")

            # Versuchen sich mit dem Alias anzumelden
            welcome_message = kocha_tcp_client.try_login(alias)

            # Bei gescheiterter Anmeldung, Nutzer fragen, ob er es mit
            # einem anderen Alias nochmal probieren moechte
            if not kocha_tcp_client.alias:
                print("The login failed. Your alias might be taken by another "
                      "user or your alias contains illegal characters like ':' "
                      "or any form of whitespace.")

                try_again = input("Try again with a different alias? [y/n] ")
                if try_again.lower() != "y":
                    return 1

        # Das User-Interface des KOCHA-Clients erstellen
        ui = KochaUi(kocha_tcp_client, welcome_message=welcome_message)

        # Wenn das Terminal keine Farben unterstuezt, hier abbrechen
        if not ui.has_colors:
            ui.close()
            print("Terminal has to support colors in order to run"
                  "KOCHA-Client")
            return 1

        # Auf Benutzereingaben warten und Nachrichten anzeigen
        ui.loop()


if __name__ == "__main__":
    sys.exit(KochaUi.show())
