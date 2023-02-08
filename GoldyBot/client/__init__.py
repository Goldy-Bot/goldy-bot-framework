from nextcore.http.client import HTTPClient

from nextcore.http import BotAuthentication

class Goldy(HTTPClient):
    """The main Goldy Bot class that controls the whole framework and let's you start an instance of Goldy Bot."""
    def __init__(self, token:str):
        self.authentication = BotAuthentication(token)
        ...