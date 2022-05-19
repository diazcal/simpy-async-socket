from environments import SocketEnvironment
from sockets import AsyncSocket


def counter(env, tick):
    while True:
        print(env.now)
        yield env.timeout(tick)


env = SocketEnvironment()

socket_a = AsyncSocket(env, "localhost", 1234)
socket_b = AsyncSocket(env, "localhost", 5678)

env.process(counter(env, 1))
env.process(socket_a.send("foo"))       # env is passed when the object is instantiated
env.process(socket_b.send("bar"))       # env is passed when the object is instantiated

env.run(until=10)
