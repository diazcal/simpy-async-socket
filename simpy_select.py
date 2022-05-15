import errno
import select
import socket
import time
import simpy


def counter(local_env):
    while True:
        print(local_env.now)
        yield local_env.timeout(0.1)

def socket_client(local_env, port, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', port))
    sock.setblocking(0)

    data = (data + '\n') * 1024 * 1024
    print(f'Bytes to send {len(data)}')

    total_sent = 0

    while len(data):
        try:
            sent = yield local_env.process(send_data_async(local_env, sock, data))
            total_sent += sent
            data = data[sent:]
            print('Sending data')
        except socket.error as e:
            if e.errno != errno.EAGAIN:
                raise e
            yield local_env.timeout(0)
    print('Bytes sent: ', total_sent)

def send_data_async(env, sock, data):
    sent = sock.send(data.encode())
    yield env.timeout(0)        # I hate those tricks
    return sent


env = simpy.Environment()
env.process(counter(env))
env.process(socket_client(env, 9999, "hello"))
env.run(until=10)