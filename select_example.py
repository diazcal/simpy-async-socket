import errno
import select
import socket
import time
from datetime import datetime


def other_task():
    i = 0
    while i < 2000:
        i += 1
        print(i)
        time.sleep(0.01)
        yield


def send_data_task(port, data):
    name = data
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', port))
    sock.setblocking(0)

    data = (data + '\n') * 1024 * 1024
    print('Bytes to send: ', len(data))

    start = datetime.now()
    print(f'Start sending at: {start.strftime("%H:%M:%S")}')

    total_sent = 0
    while len(data):
        try:
            sent = sock.send(data.encode())
            total_sent += sent
            data = data[sent:]
            now = datetime.now()
            print(f'Sending data for loop: {name} at {now.strftime("%H:%M:%S")}')
        except socket.error as e:
            block_time = datetime.now()
            print(f'{name} socket is locked at {block_time.strftime("%H:%M:%S")}')
            if e.errno != errno.EAGAIN:
                raise e
            yield 'w', sock

    stop = datetime.now()
    total_time = stop - start
    print(f'Stop sending at: {stop.strftime("%H:%M:%S")}')
    print(f'Bytes sent: {total_sent}')
    print(f'Total time: {total_time} for {name} socket')


if __name__ == '__main__':
    tasks = [
        # other_task(),
        send_data_task(port=1234, data='foo'),
        send_data_task(port=5678, data='bar'),
    ]

    fds = dict(w={}, r={})
    while len(tasks) or len(fds['w']) or len(fds['r']):
        new_tasks = []
        for task in tasks:
            try:
                resp = next(task)
                try:
                    iter(resp)
                    fds[resp[0]][resp[1]] = task
                except TypeError:
                    # this task has to be done since not
                    # dependent on any fd
                    new_tasks.append(task)
            except StopIteration:
                # function completed
                pass

        if len(fds['w'].keys()) or len(fds['r'].keys()):
            readable, writeable, exceptional = select.select(
                fds['r'].keys(), fds['w'].keys(), [], 0)
            for readable_sock in readable:
                new_tasks.append(fds['r'][fd])
                del fds['r'][fd]
            for fd in writeable:
                new_tasks.append(fds['w'][fd])
                del fds['w'][fd]
            # ignore exceptional for now

        tasks = new_tasks
