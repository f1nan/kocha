from datetime import datetime


class Payload:

    """Represents the payload that is send over the network."""

    def __init__(self, content, user, timestamp=None):
        """Inititializes an object of class Payload.

        Args:
            content (str): The content.
            user (str): The user.
            timestamp (str): The timestamp.
        """
        self.content = content
        self.user = user

        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def as_payload(json_object):
    """Serializes a JSON-Object to a Payload-Object.

    Args:
        json_object (dict): The JSON-Object.

    Returns:
        Payload: The Payload-Object.
    """
    return Payload(
        json_object['content'],
        json_object['user'],
        json_object['timestamp'])
