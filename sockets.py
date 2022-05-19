import socket
import errno


class AsyncSocket:
    """
    A non-blocking socket for Simpy to enable async communication.
    To be used with SocketEnvironment.
    """
    def __init__(self, env, host, port):
        self.host = host
        self.port = port
        self.env = env
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.env.attach_socket(self)
        self.wait_for_select_signal = self.env.event()

    def connect(self):
        self.sock.connect((self.host, self.port))
        self.sock.setblocking(False)

    def send(self, message):
        # message = (message + '\n') * 1024 * 1024    # comment out to test long messages
        total_sent = 0
        while len(message):
            # "Clean" the event in case it was set
            self.wait_for_select_signal = self.env.event()
            try:
                sent = self.sock.send(message.encode())
                total_sent += sent
                message = message[sent:]
            except socket.error as e:
                if e.errno != errno.EAGAIN:
                    raise e

                # If we are here is because the write buffer is full. Wait for select
                self.env.check_select_availability(self)
                yield self.wait_for_select_signal

    def ready(self):
        self.wait_for_select_signal.succeed()

    def fileno(self):
        return self.sock.fileno()
