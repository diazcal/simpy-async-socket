import errno
import select as sel
import socket
import simpy
from datetime import datetime


class AsyncSocket:
    def __init__(self, local_env, host, port, select):
        self.env = local_env
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.setblocking(0)
        self.select = select
        self.wait_for_select_signal = self.env.event()

    def send(self, message):
        name = message
        message = (message + '\n') * 1024 * 1024
        print('Bytes to send: ', len(message))

        start = datetime.now()
        print(f'Start sending at: {start.strftime("%H:%M:%S")} for {name} socket')

        total_sent = 0
        while len(message):
            # "Clean" the event in case it was set
            self.wait_for_select_signal = self.env.event()
            try:
                sent = self.socket.send(message.encode())
                total_sent += sent
                message = message[sent:]
            except socket.error as e:
                block_time = datetime.now()
                print(f'{name} socket is locked at {block_time.strftime("%H:%M:%S")}')
                if e.errno != errno.EAGAIN:
                    raise e

                # If we are here is because the write buffer is full. Wait for select
                self.select.wait(self)
                yield self.wait_for_select_signal

        stop = datetime.now()
        total_time = stop - start
        print(f'Stop sending at: {stop.strftime("%H:%M:%S")} for {name} socket')
        print(f'Bytes sent: {total_sent}')
        print(f'Total time: {total_time} for {name} socket')

    def ready(self):
        self.wait_for_select_signal.succeed()

    def fileno(self):
        return self.socket.fileno()


class SelectWatchdog:
    def __init__(self, local_env):
        self.env = local_env
        self.async_sockets_to_watch = {'w': {}, 'r': {}}        # at this moment they are all write.

    def watch(self):
        while True:
            _, writeable, _ = sel.select([], self.async_sockets_to_watch['w'].keys(), [], 0)
            for ws in writeable:
                self.async_sockets_to_watch['w'][ws].ready()
                del self.async_sockets_to_watch['w'][ws]
            yield self.env.timeout(0.01)

    def wait(self, sock):
        self.async_sockets_to_watch['w'][sock.socket] = sock


def counter(local_env, delay):
    while True:
        print(local_env.now)
        yield local_env.timeout(delay)


env = simpy.rt.RealtimeEnvironment()

w_dog = SelectWatchdog(env)
a_socket = AsyncSocket(env, 'localhost', 1234, w_dog)
b_socket = AsyncSocket(env, 'localhost', 5678, w_dog)


env.process(counter(env, 1))
env.process(w_dog.watch())
env.process(a_socket.send('foo'))
env.process(b_socket.send('bar'))

env.run(until=10)
print(env.now)
