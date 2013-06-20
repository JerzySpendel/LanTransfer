__author__ = 'jurek'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import socket,time,os
def intoChunks(f):
    chunks = []
    while True:
        temp = f.read(1024)
        if not temp == b'':
            chunks.append(temp)
        elif temp == b'':
            break
    return chunks
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
        bytes = os.path.getsize(self.path)
        if channel.recv(1024).decode('utf-8') == 'name please':
            channel.send(self.name.encode('utf-8'))
        if channel.recv(1024).decode('utf-8') == 'size please':
            channel.send(str(bytes).encode('utf-8'))
        if channel.recv(1024).decode('utf-8') == 'file please':
            while True:
                for chunk in intoChunks(f):
                    channel.send(chunk)
                    if channel.recv(1024).decode('utf-8') == 'more':
                        continue
            channel.send(b'end')
class DownloadProcess(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    def config(self,ip):
        self.ip = ip
        print('Adres IP ustawiono na ',self.ip)
    def run(self):
        self.s.connect((self.ip,8888))
        self.s.send(b'name please')
        name = self.s.recv(1024).decode('utf-8')
        print('Nazwa pliku: ',name)
        self.s.send(b'size please')
        size = int(self.s.recv(1024).decode('utf-8'))
        print('Ilość kawałków: ',size)
        self.s.send(b'file please')
        f = open(name,'wb')
        while True:
            data = self.s.recv(1024)
            try:
                if data.decode('utf-8') == 'end':
                    break
            except Exception:
                pass
            f.write(data)
            f.flush()
            self.s.send(b'more')
        self.s.close()