
class CommunicationBackend:
    # Communication backend Interface

    def connect(self):
        # Initialize the backend
        pass

    def is_connected(self):
        # Indicate the port is open or bluetooth is connected
        pass

    def disconnect(self):
        # Disconnect from bluetooth or serial
        pass

    def read(self):
        # Read from the backend
        # TODO Figure out what this returns/figure out the contract
        pass

    def write(self, data: bytes):
        # Write data out via the backend
        pass