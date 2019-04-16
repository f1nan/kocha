"""
Modul mit Hilfsklasse und Methoden.
"""

import json
from datetime import datetime

KOCHA_VERSION = "v1.0.0"
"""
Die aktuelle Versionsnummer des KOCHA-Servers und des KOCHA-Clients.
"""


class KochaMessage:
    """
    Klasse kapselt ein Nachrichten-Object, dass im JSON-Format über
    TCP/IP zwischen KOCHA-Server und KOCHA-Client ausgetauscht wird.
    """

    def __init__(self, content="", sender="", sent_at=None, is_dm=False):
        """
        Initialisiert ein Object der Klasse KochaMessage.

        Args:
            content: Der Inhalt der Nachricht.
            sender: Der Alias des Senders.
            sent_at: datetime-Object mit dem Versendezeitpunkt.
            is_dm: Gibt an, ob die Nachricht eine Direct-Message ist.
        """
        self.content = content
        self.sender = sender
        self.sent_at = datetime.now() if sent_at is None else sent_at
        self.is_dm = is_dm


class KochaMessageEncoder(json.JSONEncoder):
    """
    Klasse fuer die Serialisierung von KochaMessage-Objects.
    """

    def default(self, obj):
        """
        Gibt ein seriailisierbares Object zurueck.

        Args:
            obj: Das Object, das serialisiert werden soll.

        Returns:
            Das serialisierbare Object.
        """
        if isinstance(obj, KochaMessage):
            # Dictionary mit allen Attributen von obj erstellen
            serializable = dict(**obj.__dict__)

            # Aus dem datetime-Object einen Timestamp machen, da dieser
            # serialisiert werden kann
            serializable["sent_at"] = obj.sent_at.timestamp()
            return serializable
        
        # Wenn obj keine Instanz von KochaMessage ist, wirft der Encoder
        # der Basisklasse hier einen TypeError
        return super().default(obj)


class KochaMessageDecoder(json.JSONDecoder):
    """
    Klasse fuer die Deserialisierung von KochaMessage-Objects im
    JSON-Format.
    """

    def __init__(self, *args, **kwargs):
        """
        Eine Instanz der Klasse KochaMessageDecoder erstellen. Dabei
        die Object-Hook für die Deserialisierung von
        KochaMessage-Objects initialisieren.

        Args:
            *args: Optionale Positionsparameter.
            **kwargs: Optionale Schluesselwortparameter.
        """
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        """
        Wird aufgerufen, um anstelle des normalen deserialisierten
        Objects (dict) ein anderes KochaMessage-Object zurueck zu geben.

        Args:
            dct: Das deserialisierten Object.

        Returns:
            Das KochaMessage-Object.
        """
        obj = KochaMessage()

        # Attribute setzen, falls es sich bei dem deserialisierten
        # Obejct um ein KochaMessage-Object handelt
        is_kocha_message = all(
            True if key in dct else False for key in vars(obj))
        if is_kocha_message:
            obj.sender = dct["sender"]
            obj.content = dct["content"]
            obj.sent_at = datetime.fromtimestamp(dct["sent_at"])
            obj.is_dm = dct["is_dm"]

        return obj


class JsonUtils:
    """
    Klasse mit Hilfsmethoden fuer die Arbeit mit JSON.
    """

    @staticmethod
    def to_kocha_message(json_data):
        """
        Erstellt aus Daten im JSON-Format ein KochaMessage-Object.

        Args:
            json_data: Daten im JSON-Format.

        Returns:
            Ein KochaMessage-Object.
        """
        return json.loads(json_data, cls=KochaMessageDecoder)

    @staticmethod
    def to_json(kocha_message):
        """
        Erstellt ein JSON-Object aus einem KochaMessage-Object.

        Args:
            kocha_message: Ein KochaMessage-Object.
        
        Returns:
            Daten im JSON-Format.
        """
        return json.dumps(kocha_message, cls=KochaMessageEncoder)