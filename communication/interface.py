
class CommunicationBackend:
    # Communication backend Interface

    def connect_port(self):
        # Initialize the backend
        pass

    def is_connected(self):
        # Indicate the port is open or bluetooth is connected
        pass

    def disconnect_port(self):
        # Disconnect from bluetooth or serial
        pass

    def read(self):
        # Read from the backend
        # TODO Figure out what this returns/figure out the contract
        pass

    def write(self, data: bytes):
        # Write data out via the backend
        pass

    def sent_bytes(self):
        # The number of packets sent of the interface
        pass

    def rec_bytes(self):
        # The number of packets received on the interface
        pass