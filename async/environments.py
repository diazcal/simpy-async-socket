from simpy import RealtimeEnvironment
import select


class SocketEnvironment(RealtimeEnvironment):
    """
    Special environment to watch select state for a given set of Async sockets.
    Only for RealTime simulations.
    To use togther with AsyncSocket. At this moment only used for sockets that want to write
    but is easy to extend to read as well.
    """

    def __init__(self):
        super().__init__()
        self._async_socket_fileno_to_watch = {'w': {}, 'r': {}}
        self._sockets_to_connect = []

    def attach_socket(self, socket):
        self._sockets_to_connect.append(socket)

    def _watch_select(self):
        while True:
            readable, writeable, _ = select.select(self._async_socket_fileno_to_watch['r'], self._async_socket_fileno_to_watch['w'], [], 0)
            for rs in readable:
                self._async_socket_fileno_to_watch['r'][rs].ready()
                del self._async_socket_fileno_to_watch['r'][rs]

            for ws in writeable:
                self._async_socket_fileno_to_watch['w'][ws].ready()
                del self._async_socket_fileno_to_watch['w'][ws]
            yield self.timeout(0.01)

    def run(self, until=None):
        while self._sockets_to_connect:
            socket = self._sockets_to_connect.pop()
            socket.connect()
        self.process(self._watch_select())
        super(SocketEnvironment, self).run(until)

    def check_select_availability(self, socket):
        self._async_socket_fileno_to_watch['w'][socket] = socket
