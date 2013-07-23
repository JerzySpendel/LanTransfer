__author__ = 'jurek'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import socket, time, os, time, hashlib

CHUNK_SIZE = (2 ** 20)


def intoChunks(f):
    while True:
        temp = f.read(CHUNK_SIZE)
        if not temp == b'':
            yield temp
        elif temp == b'':
            break


def percent(my, all):
    return int((my / all) * 100)


class UploadProcess(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', 8888))
        self.s.listen(10)

    def config(self, path_to_file):
        self.path = path_to_file
        self.name = os.path.basename(self.path)
        self.md5()

    def md5(self):
        m = hashlib.md5()
        m.update(open(self.path,'rb').read())
        self.md5_checksum = m.hexdigest()

    def run(self):
        QObject.emit(self,SIGNAL('makeBusy()'))
        channel, addr = self.s.accept()
        QObject.emit(self,SIGNAL('unmakeBusy()'))
        f = open(self.path, 'rb')
        sent = 0
        bytes = os.path.getsize(self.path)
        if channel.recv(1024).decode('utf-8') == 'checksum please':
            channel.send(str(self.md5_checksum).encode('utf-8'))
        if channel.recv(1024).decode('utf-8') == 'name please':
            channel.send(self.name.encode('utf-8'))
        if channel.recv(1024).decode('utf-8') == 'size please':
            channel.send(str(bytes).encode('utf-8'))
        if channel.recv(1024).decode('utf-8') == 'file please':
            while True:
                for chunk in intoChunks(f):
                    channel.send(chunk)
                    sent += CHUNK_SIZE
                    QObject.emit(self, SIGNAL('wyslano(int)'), percent(sent, bytes))
                    if sent >= bytes:
                        break
                    if channel.recv(1024).decode('utf-8') == 'more':
                        continue
            channel.send(b'end')


class DownloadProcess(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.emiter = Emiter()
        self.emiter.start()
        QObject.connect(self.emiter, SIGNAL('wakeup()'), self.czas)

    def config(self, ip):
        self.ip = ip
        print('Adres IP ustawiono na ', self.ip)

    def czas(self):
        try:
            speed = self.speed(bytes=self.now, time=self.time_c)
            est_time = self.est_time(speed=speed, est_bytes=self.estimated_bytes)
            QObject.emit(self, SIGNAL('updateTime(PyQt_PyObject)'), "Pozostało " + str(int(est_time)) + " sekund")
        except AttributeError:
            print('Waiting for data...')

    def checkFile(self,md5,file):
        f = open(file.name,'rb')
        m = hashlib.md5()
        m.update(f.read())
        if str(m.hexdigest()) == md5:
            return True
        else:
            return False

    def run(self):
        self.s.connect((self.ip, 8888))
        self.s.send(b'checksum please')
        self.md5_checksum = self.s.recv(1024).decode('utf-8')
        self.s.send(b'name please')
        name = self.s.recv(1024).decode('utf-8')
        print('Nazwa pliku: ', name)
        self.s.send(b'size please')
        size = int(self.s.recv(1024).decode('utf-8'))
        print('Ilość bajtów: ', size)
        self.s.send(b'file please')
        f = open(name, 'wb')
        got = 0
        while not got >= size:
            time_a = time.time()
            data = self.s.recv(CHUNK_SIZE)
            got += len(data)
            f.write(data)
            self.s.send(b'more')
            QObject.emit(self, SIGNAL('aktualizacja(int)'), percent(got, size))
            time_b = time.time()
            self.time_c = time_b - time_a
            print('Otrzymano ', got)
            self.estimated_bytes = size - got
            self.now = len(data)
        print('Koniec pobierania')
        print('Checking MD5 checksum...')
        if self.checkFile(self.md5_checksum,f):
            print('MD5 checksum is correct!')
        else:
            print('MD5 checksum is incorrect, error ocurred!')
        self.s.close()

    #Calculate speed of downloading
    def speed(self, bytes=None, time=None):
        return bytes / time

    #Calculate estimate time to download file
    def est_time(self, speed=None, est_bytes=None):
        if not est_bytes == 0:
            return est_bytes / speed
        else:
            return 0


class Emiter(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        while True:
            QObject.emit(self, SIGNAL('wakeup()'))
            time.sleep(2)