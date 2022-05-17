# simpy-async-socket
PoC on non-blocking sockets to work with real time discrete event simulations in Simpy

## Context
For some rt simulations I need to be able to write to sockets without blocking the Simpy event loop. Therefore, I make use of select() to unblock the I/O.

So far I made it work to write sockets, but it is easisly extendable to work with read too.

And yeah I know simpy.io is there, but last commit was some years ago. I wanted to see how far can I go without the need of to go through someonelses code.

## References
[Non blocking socket with select()](https://medium.com/vaidikkapoor/understanding-non-blocking-i-o-with-python-part-1-ec31a2e2db9b)
