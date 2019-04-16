class Parameter:

    """Klasse kapselt die Argumete einer Action."""

    def __init__(self, client, payload):
        """Initailisiert eine Instanz der Klasse ActionParameter.

        Args:
            client (ClientWrapper): The client.
            payload (Payload): The Payload.
        """
        self.client = client
        self.payload = payload
