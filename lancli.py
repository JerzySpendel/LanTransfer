import argparse, mmap, os
from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from functools import partial

parser = argparse.ArgumentParser(description="Sends files")
parser.add_argument('-f', '--file', help="Location of hosting file")
parser.add_argument('--host', action='store_true', help='Host given file')
parser.add_argument('-d', '--directory', help="Directory where script will save file")
parser.add_argument('-i', '--ip', help='IP address of host')
parser.add_argument('-s', '--size', nargs="?", default=1024, type=int, help='Size of signle chunk of file')
args = parser.parse_args()
CHUNK_SIZE = int(args.size)

class StreamerF(Factory):

    def __init__(self, path):
        self.f = open(path, 'r+')
        self.fg = iter(partial(self.f.read, CHUNK_SIZE), b'')

    def dataPlease(self):
        try:
            return next(self.fg)
        except StopIteration:
            return None

    def buildProtocol(self, addr):
        return Streamer(self)

class Streamer(Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.transport.write(self.factory.f.name)

    def abortConnection(self):
        pass

    def dataReceived(self, data):
        if data.strip() == 'more':
            send = self.factory.dataPlease()
            if send is not None:
                self.transport.write(send)

class Receiver(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.STATE = 'init'

    def connectionMade(self):
        pass

    def handle_INIT(self, data):
        self.filename = os.path.split(data)[1]
        self.file = open(os.path.join(self.factory.dir_path, self.filename), 'wb')
        self.STATE = 'download'
        self.transport.write('more')

    def handle_DOWNLOAD(self, data):
        self.file.write(data)
        self.file.flush()
        self.transport.write('more')

    def dataReceived(self, data):
        if self.STATE is 'init':
            print('State = init')
            self.handle_INIT(data)
            return
        elif self.STATE is 'download':
            print('State = download')
            self.handle_DOWNLOAD(data)
            return

class ReceiverF(ClientFactory):
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def buildProtocol(self, addr):
        return Receiver(self)



if args.host:
    print('Initializing server')
    endpoint = TCP4ServerEndpoint(reactor, 8007)
    endpoint.listen(StreamerF(args.file))
    reactor.run()
    print('Initialized')
else:
    print('Starting downloading a file')
    reactor.connectTCP(args.ip, 8007, ReceiverF(args.directory))
    reactor.run()
