# exceptions.py
class NetworkNotConnectedError(Exception):
    """Exception raised when the network is not connected."""

    def __init__(self, message="The network is not connected please connect the network and try again."):
        self.message = message
        super().__init__(self.message)