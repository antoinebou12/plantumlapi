"""
Exceptions for PlantUML.
"""


class PlantUMLError(Exception):
    """
    Error in processing.
    """
    pass


class PlantUMLConnectionError(PlantUMLError):
    """
    Error connecting or talking to PlantUML Server.
    """
    pass


class PlantUMLHTTPError(PlantUMLConnectionError):
    """
    Request to PlantUML server returned HTTP Error.
    """

    def __init__(self, response, content, *args, **kwdargs):
        self.response = response
        self.content = content
        message = f"HTTP Error : {response.request.url} {response}"
        if not getattr(self, 'message', None):
            self.message = message
        super().__init__(message, *args, **kwdargs)