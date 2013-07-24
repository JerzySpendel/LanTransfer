# -*- coding: UTF-8 -*-

__author__ = 'jurek'
import socket
import time
import os
import hashlib

from PyQt4.QtCore import *


#The size of chunk sending through sockets
CHUNK_SIZE = (2 ** 20)

#Generator which gives next part of files
#Is iterated in for loop in UploadProcess in run method
def intoChunks(f):
    while True:
        temp = f.read(CHUNK_SIZE)
        if not temp == b'':
            yield temp
        elif temp == b'':
            break

#Calculate percents :]
def percent(my, all):
    return int((my / all) * 100)

#Thread beeing resposible for sending next chunks to recipient
#also for sending singals which gives GUI information about the progress


class UploadProcess(QThread):
    #Inner class responsible for calculating MD5 checksum
    #While UploadProcess will upload the file
    class ComputeMD5(QThread):
        def __init__(self, parent):
            QThread.__init__(self, parent)
            self.parent = parent

        def run(self):
            m = hashlib.md5()
            m.update(open(self.parent.path, 'rb').read())
            self.parent.md5_checksum = m.hexdigest()

    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', 8888))
        self.s.listen(10)
        self.computeMD5 = self.ComputeMD5(self)
        self.md5_checksum = None

    def config(self, path_to_file):
        self.path = path_to_file
        self.name = os.path.basename(self.path)
        self.md5(self.md5_checksum)

    def setMD5(self, md5):
        self.md5_checksum = md5

    #Compute MD5 in other thread while file is sending
    def md5(self, here):
        self.computeMD5.start()

    def run(self):
        QObject.emit(self, SIGNAL('makeBusy()'))
        channel, addr = self.s.accept()
        QObject.emit(self, SIGNAL('unmakeBusy()'))
        f = open(self.path, 'rb')
        sent = 0
        bytes = os.path.getsize(self.path)
        self.md5(self.md5_checksum)
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
        if channel.recv(1024).decode('utf-8') == 'checksum please':
            channel.send(str(self.md5_checksum).encode('utf-8'))
            channel.send(b'end')


class DownloadProcess(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.emiter = Emiter()
        self.emiter.start()
        QObject.connect(self.emiter, SIGNAL('wakeup()'), self.czas)

    def config(self, ip, path=None):
        self.ip = ip
        if path != None:
            self.path = path
        print('Adres IP ustawiono na ', self.ip)

    def czas(self):
        try:
            speed = self.speed(bytes=self.now, time=self.time_c)
            est_time = self.est_time(speed=speed, est_bytes=self.estimated_bytes)
            QObject.emit(self, SIGNAL('updateTime(PyQt_PyObject)'), "Pozostało " + str(int(est_time)) + " sekund")
        except AttributeError:
            print('Waiting for data...')

    def checkFile(self, md5, file):
        f = open(file.name, 'rb')
        m = hashlib.md5()
        m.update(f.read())
        if str(m.hexdigest()) == md5:
            return True
        else:
            return False

#Get information about the file from server
    def getData(self):
        self.s.send(b'name please')
        self.name = self.s.recv(1024).decode('utf-8')
        print('Nazwa pliku: ', self.name)
        self.s.send(b'size please')
        self.size = int(self.s.recv(1024).decode('utf-8'))
        print('Ilość bajtów: ', self.size)

    def run(self):
        self.s.connect((self.ip, 8888))
        self.getData()
        self.s.send(b'file please')
        f = open(self.path+'/'+self.name, 'wb')
        got = 0
        while not got >= self.size:
            time_a = time.time()
            data = self.s.recv(CHUNK_SIZE)
            got += len(data)
            f.write(data)
            self.s.send(b'more')
            QObject.emit(self, SIGNAL('aktualizacja(int)'), percent(got, self.size))
            time_b = time.time()
            self.time_c = time_b - time_a
            print('Otrzymano ', got)
            self.estimated_bytes = self.size - got
            self.now = len(data)
        print('Koniec pobierania')
        print('Checking MD5 checksum...')

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