"""
Modul mit Klassen und Methoden für den KOCHA-Client.
"""

import curses
import locale
import queue
import threading
import time

import utils


class KochaUi:
    """
    Klasse fuer das User Interface des KOCHA-Clients.
    """

    def __init__(self, stdscr=None, prompt="> "):
        """
        Initialisert ein Object der Klasse Ui.

        Args:
            stdscr: Window-Object, das den gesamten Bilschirm repraesentiert.
            prompt: Das Zeichen fuer die Eingabeaufforderung.
        """
        if stdscr is None:
            # Die curses Bibliothek initialisieren, falls kein Hauptfenster
            # uerbgeben wurde
            stdscr = curses.initscr()

            # Zeichen nicht automatisch auf dem Bildschirm ausgeben
            curses.noecho()

            # Bei jeder Eingabe reagieren und nicht nur wenn Enter gedrueckt
            # wird
            curses.cbreak()

            # Sonderzeichen von curses abfangen lassen, damit sie einfacher zu
            # verarbeiten sind
            self.stdscr.keypad(True)

        # Das Haupfenster merken
        self.stdscr = stdscr

        # Das Zeichen fuer die Eingabeaufforderung merken
        self.prompt = prompt

        # Puffer für die Nachrichten initialisieren
        self.messages = []

        # Puffer fuer die Texteingabe initialisieren
        self.input = ""

        # Titel des Programms zeichnen (Hintergrund- und Vordergundfarbe
        # vertauscht)
        self.stdscr.addstr(
            0, 0, "KOCHA " + utils.KOCHA_VERSION, curses.A_REVERSE)
        self.stdscr.chgat(-1, curses.A_REVERSE)
        self.stdscr.refresh()

        # Das Nachrichtenfenster erstellen und zeichnen
        self.messages_window = curses.newwin(
            curses.LINES - 4, curses.COLS, 1, 0)
        self.draw_messages_window()

        # Das Fenster fuer Benuterzeingaben erstellen und zeichnen
        self.input_window = curses.newwin(
            3, curses.COLS, curses.LINES - 3, 0)
        self.draw_input_window()

    def close(self):
        """
        Wird beim Schließen des User Interfaces aufgerufen. Meldet den Client
        am Server ab und stellt den Ursprungszustand des Terminals wieder her.
        """
        # Terminaleinstellungen für curses wieder aufheben
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()

        # Terminal in urspruenglichen Beriebsmodus zuruecksetzen
        curses.endwin()

    def loop(self):
        """
        Wartet auf Nutzereingaben und verarbeitet diese in einer Endlosschleife.
        """
        threading.Thread(target=self.get_messages_from_server).start()

        while True:
            # Auf Nutzereingabe warten
            c = self.input_window.getch()

            # Ausfuehren wenn die Eingabe ein Zeilenende ist
            if c == ord("\n"):
                # Programm beenden, wenn Nutzer /q oder /quit eigegeben hat
                if self.input in { "/q", "/quit" }:
                    break

                # Nutzereingabe zum Nachrichtenpuffer hinzufuegen
                self.messages.append(self.input)

                # Texteingabepuffer zuruecksetzen
                self.input = ""

                # Das Nachrichtenfenster aktualisieren
                self.draw_messages_window()

                # Das Eingabefenster aktualiseren
                self.draw_input_window()
            else:
                # Nutzereingabe zum Puffer Texteingabepuffer hinzufuegen
                self.input += chr(c)

                # Das Eingabefenster aktualisieren
                self.draw_input_window()

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

        # Nachrichten zeichnen
        for y, message in enumerate(self.messages, start=1):
            self.messages_window.addstr(y, 1, message)

        # Abmessungen des Nachrichtenfensters holen
        max_y, max_x = self.messages_window.getmaxyx()

        # Breite des Rahmens abziehen
        max_y, max_x = max_y - 2, max_x - 2

        # Nachrichten an die Breite des Nachrichtenfensters anpassen
        messages = []
        for message in self.messages:
            while message != "":
                messages.append(message[:max_x])
                message = message[max_x:]

        # Index der aeltesten Nachricht, die im Nachrichtenfenster gezeichnet
        # werden kann, bestimmen
        begin = len(self.messages) - max_y
        begin = begin if begin >= 0 else 0

        # Nachrichten ins Nachrichtenfesnter zeichnen
        for y, message in enumerate(messages[begin:], start=1):
            self.messages_window.addstr(y, 1, message)

        # Das Nachrichtenfesnster aktualisieren
        self.messages_window.refresh()


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

        # Zeichen fuer Eingabeaufforderung und Nutzereingabe zusammensetzen
        text = self.prompt + self.input

        # Zeichenkette vorne abschneiden, wenn sie zu lang ist
        begin = len(text) % max_x
        begin = begin if begin != len(text) else 0

        # Text ins Eingabefenster zeichnen
        self.input_window.addstr(1, 1, text[begin:])

        # Cursorposition aktualisieren
        self.input_window.cursyncup()

        # Eingabefenster aktualisieren
        self.input_window.refresh()

    def get_messages_from_server(self):
        for _ in range(10):
            time.sleep(5.0)
            self.messages.append("Insert random chuck norris joke here")
            self.draw_messages_window()
            self.draw_input_window()

    @staticmethod
    def show(stdscr):
        """
        Wird aufgerufen um das User Interface für den KOCHA-Client aufzurufen.

        Args:
            stdscr: Window-Object, das den gesamten Bilschirm repraesentiert.
        """
        ui = KochaUi(stdscr)
        ui.loop()


if __name__ == "__main__":
    # Das Gebietsschema auf die Standardeinstellung des Benutzers setzen
    locale.setlocale(locale.LC_ALL, "")

    curses.wrapper(KochaUi.show)