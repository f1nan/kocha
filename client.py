"""Modul enthält Klassen und Methoden für den KOCHA-Client.
"""

import curses


class Ui:
    """Klasse für das User Interface des Kocha-Clients.
    """

    def __init__(self):
        # curses initialisieren
        self.stdscr = curses.initscr()
        # Zeichen nicht automatisch auf dem Bildschirm ausgeben
        curses.noecho()
        # Bei jeder Eingabe reagieren und nicht nur wenn Enter gedrueckt wird
        curses.cbreak()
        # Sonderzeichen von curses abfangen lassen, damit sie einfacher zu
        # verarbeiten sind
        curses.keypad(True)
