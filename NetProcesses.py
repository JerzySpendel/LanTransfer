# -*- coding: UTF-8 -*-

__author__ = 'jurek'
import socket
import time
import os
import hashlib
from Utils import Config
from PyQt4.QtCore import *


#The size of chunk sending through sockets
CHUNK_SIZE = 2 ** 20

#Function return list of generators
#Each of generator is used to send part of file to corresposnding input socket to recipient
def intoChunks(f, amount_of_generators):
    generators = []

    def generatorForFile(path_to_file):
        f = open(path_to_file, 'rb')

        def generator():
            while True:
                yield f.read(CHUNK_SIZE)

        return generator

    def preparePartFilesAndGenerators():
        path = os.path.abspath(f.name)
        each_size = os.path.getsize(path) // amount_of_generators #No, this is not a comment
        fr = open(path, 'rb')
        bytes = 0
        for i in range(amount_of_generators - 1):
            filePath = path + '.part' + str(i)
            generators.append(generatorForFile(filePath))
            fw = open(path + '.part' + str(i), 'wb')
            data = fr.read(each_size)
            bytes += len(data)
            fw.write(data)
        delta = os.path.getsize(path) - bytes
        if delta != 0:
            fw = open(path + '.part' + str(amount_of_generators-1), 'wb')
            fw.write(fr.read(delta))

    preparePartFilesAndGenerators()
    return generators


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

    class GeneratorUpload(QThread):
        def __init__(self, parent, port, generator):
            QThread.__init__(self, parent)
            self.port = port
            self.generator = generator
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind(('',self.port))
            self.s.listen(1)

        def run(self):
            channel, addr = self.s.accept()
            for chunk in self.generator():
                if channel.recv(1024).decode('utf-8') == 'more please':
                    channel.send(chunk)
                else:
                    break
            channel.close()
            self.s.close()

    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', 8885))
        self.s.listen(1)
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
        if channel.recv(1024).decode('utf-8') == 'threads please':
            channel.send(str(Config.data['THREADS']).encode('utf-8'))
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
    class Download(QThread):
        def __init__(self,parent, port, ip, file_path):
            QThread.__init__(self,parent)
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((ip,port))
            self.f = open(file_path, 'wb')
        def run(self):
            data = b'some'
            got = 0
            while data != b'':
                data = self.s.recv(CHUNK_SIZE)
                got += len(data)
                self.f.write(data)

    #Class to manage single downloading threads
    class DownloadManager():
        def __init__(self, ip, main_socket, folder_path):
            self.ip = ip
            self.main_socket = main_socket
            self.folder_path = folder_path
        def getData(self):
            self.main_socket.send(b'name please')
            self.name = self.s.recv(1024).decode('utf-8')
            print('Nazwa pliku: ', self.name)
            self.main_socket.send(b'size please')
            self.size = int(self.s.recv(1024).decode('utf-8'))
            print('Ilość bajtów: ', self.size)
            self.main_socket.send(b'threads please')
            self.threads = self.s.recv(1024).decode('utf-8')

    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.emiter = Emiter()
        self.emiter.start()
        QObject.connect(self.emiter, SIGNAL('wakeup()'), self.czas)

    def config(self, ip, path=None):
        self.ip = ip
        if path is not None:
            self.path = path
        else:
            self.path = None
        self.s.connect((self.ip, 8885))
        print('IP address set for ', self.ip)

    def prepareFileToWrite(self):
        if self.path is not None:
            self.f = open(self.path + '/' + self.name, 'wb')
        else:
            self.f = open(self.name, 'wb')

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

            #Get information about the file from server and prepare file to write


    def run(self):
        self.getData()
        self.s.send(b'file please')
        got = 0
        while not got >= self.size:
            time_a = time.time()
            data = self.s.recv(CHUNK_SIZE)
            got += len(data)
            self.f.write(data)
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