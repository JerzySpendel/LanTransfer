__author__ = 'jurek'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import socket,time,os
def getSize(f):
    size = len(f.read())
    f.seek(0)
    return size
class UploadProcess(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.bind(('',8888))
        self.s.listen(1)
    def config(self,path_to_file):
        self.path = path_to_file
        self.name = os.path.basename(self.path)
    def run(self):
        channel,addr = self.s.accept()
        channel.send(str(self.name).encode('utf-8'))
        f = open(self.path,'rb')
        amount = getSize(f)
        channel.send(str(amount).encode('utf-8'))
        for chunk in f:
            channel.send(chunk)
        self.s.close()
class DownloadProcess(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    def config(self,ip):
        self.ip = ip
        print('Adres IP ustawiono na ',self.ip)
    def run(self):
        self.s.connect((self.ip,8888))
        name = self.s.recv(1024).decode('utf-8')
        print('Nazwa pliku: ',name)
        size = int(self.s.recv(1024).decode('utf-8'))
        print('Ilość kawałków: ',self.s.recv(1024))

        f = open(name,'wb')
        bytes = 0
        while True:
            data = self.s.recv()
            f.write(data)
            bytes = bytes + len(data)
            if bytes >= size:
                break
        print('Odebrano plik: ',name)
        self.s.close()