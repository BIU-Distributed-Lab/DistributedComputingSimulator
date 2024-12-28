# exceptions.py
class ParseTopologyFileError(Exception):
    """Exception raised when the topology file cannot be parsed."""

    def __init__(self, message="The topology file could not be parsed."):
        self.message = message
        super().__init__(self.message)


