__author__ = 'jurek'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import socket,time,os,time
CHUNK_SIZE = (2**20)
def intoChunks(f):
    chunks = []
    while True:
        temp = f.read(CHUNK_SIZE)
        if not temp == b'':
            chunks.append(temp)
        elif temp == b'':
            break
    return chunks
def percent(my,all):
    return int((my/all)*100)
class UploadProcess(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.bind(('',8888))
        self.s.listen(10)
    def config(self,path_to_file):
        self.path = path_to_file
        self.name = os.path.basename(self.path)
    def run(self):
        channel,addr = self.s.accept()
        f = open(self.path,'rb')
        sent = 0
        bytes = os.path.getsize(self.path)
        if channel.recv(1024).decode('utf-8') == 'name please':
            channel.send(self.name.encode('utf-8'))
        if channel.recv(1024).decode('utf-8') == 'size please':
            channel.send(str(bytes).encode('utf-8'))
        if channel.recv(1024).decode('utf-8') == 'file please':
            while True:
                for chunk in intoChunks(f):
                    channel.send(chunk)
                    sent = sent + CHUNK_SIZE
                    QObject.emit(self,SIGNAL('wyslano(int)'),percent(sent,bytes))
                    if channel.recv(1024).decode('utf-8') == 'more':
                        continue
            channel.send(b'end')
class DownloadProcess(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.emiter = Emiter()
        self.emiter.start()
        QObject.connect(self.emiter,SIGNAL('wakeup()'),self.czas)
    def config(self,ip):
        self.ip = ip
        print('Adres IP ustawiono na ',self.ip)
    def czas(self):
        try:
            speed = self.speed(bytes=self.now,time=self.time_c)
            est_time = self.est_time(speed=speed,est_bytes=self.estimated_bytes)
            QObject.emit(self,SIGNAL('updateTime(PyQt_PyObject)'),"Pozostało "+str(int(est_time))+" sekund")
        except AttributeError:
            print('Waiting for data...')
    def run(self):
        self.s.connect((self.ip,8888))
        self.s.send(b'name please')
        name = self.s.recv(1024).decode('utf-8')
        print('Nazwa pliku: ',name)
        self.s.send(b'size please')
        size = int(self.s.recv(1024).decode('utf-8'))
        print('Ilość bajtów: ',size)
        self.s.send(b'file please')
        f = open(name,'wb')
        got = 0
        estimated_bytes = size
        while not got >= size:
            time_a = time.time()
            data = self.s.recv(CHUNK_SIZE)
            got = got + len(data)
            f.write(data)
            self.s.send(b'more')
            QObject.emit(self,SIGNAL('aktualizacja(int)'),percent(got,size))
            time_b = time.time()
            self.time_c = time_b-time_a
            print('Otrzymano ',got)
            self.estimated_bytes = size - got
            self.now = len(data)
        print('Koniec pobierania')
        self.s.close()
    def speed(self,bytes=None,time=None):
        return bytes/time
    def est_time(self,speed=None,est_bytes=None):
        if not est_bytes == 0:
            return est_bytes/speed
        else:
            return 0
class Emiter(QThread):
    def __init__(self):
        QThread.__init__(self)
    def run(self):
        while True:
            QObject.emit(self,SIGNAL('wakeup()'))
            time.sleep(2)