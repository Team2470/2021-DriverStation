
class CommunicationBackend:
    # Communication backend Interface

    def init(self):
        # Initialize the backend
        pass

    def read(self):
        # Read from the backend
        # TODO Figure out what this returns/figure out the contract
        pass

    def write(self, data: bytes):
        # Write data out via the backend
        pass