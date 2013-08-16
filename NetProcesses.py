# -*- coding: UTF-8 -*-

__author__ = 'Jerzy Spendel'
import pdb
import socket
import time
import os
import hashlib
from Utils import Config
from PyQt4.QtCore import *
from multiprocessing import Process


#The size of chunk sendalling through sockets
CHUNK_SIZE = 1024

#Function return list of generators
#Each of generator is used to sendall part of file to corresposnding input socket to recipient
def intoChunks(file_path, amount_of_generators):
    generators = []

    def generatorForFile(path_to_file):
        f = open(path_to_file, 'rb')

        def generator():
            while True:
                data = f.read(CHUNK_SIZE)
                if data != b'':
                    yield data
                else:
                    break

        return generator

    def preparePartFilesAndGenerators():
        path = file_path
        each_size = os.path.getsize(path) // amount_of_generators #No, this is not a comment
        fr = open(path, 'rb')
        bytes = 0
        for i in range(amount_of_generators - 1):
            filePath = path + '.part' + str(i)
            fw = open(filePath, 'wb')
            data = fr.read(each_size)
            bytes += len(data)
            fw.write(data)
            generators.append(generatorForFile(filePath))
        delta = os.path.getsize(path) - bytes
        if delta != 0:
            filePath = path + '.part' + str(amount_of_generators - 1)
            fw = open(filePath, 'wb')
            fw.write(fr.read(delta))
            generators.append(generatorForFile(filePath))
    preparePartFilesAndGenerators()
    return generators


#Calculate percents :]
def percent(my, all):
    return int((my / all) * 100)

#Thread beeing resposible for sendalling next chunks to recipient
#also for sendalling singals which gives GUI information about the progress


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
        def __init__(self, port, generator, parent=None):
            QThread.__init__(self, parent)
            self.port = port
            self.generator = generator
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind(('',self.port))
            self.s.listen(10)

        def run(self):
            print('Waiting on port', self.port)
            channel, addr = self.s.accept()
            for chunk in self.generator():
                if channel.recv(1024).decode('utf-8') == 'more please':
                    sent = channel.sendall(chunk)
            channel.recv(1024)
            channel.send(b'No MoRe bYYtes!#$@!df so sad :<')
            channel.close()
            self.s.close()

    def __init__(self):
        QThread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', 8880))
        self.s.listen(10)
        self.computeMD5 = self.ComputeMD5(self)
        self.md5_checksum = None

        self.references = []
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
            channel.sendall(self.name.encode('utf-8'))
        if channel.recv(1024).decode('utf-8') == 'size please':
            channel.sendall(str(bytes).encode('utf-8'))
        if channel.recv(1024).decode('utf-8') == 'threads please':
            channel.sendall(str(Config.data['THREADS']).encode('utf-8'))
        if channel.recv(1024).decode('utf-8') == 'file please':
            i = 1
            for gen in intoChunks(self.path, int(Config.data['THREADS'])):
                UP = self.GeneratorUpload(8880+i, gen)
                self.references.append(UP)
                UP.start()
                i += 1
            channel.sendall(b'sockets created')
        if channel.recv(1024).decode('utf-8') == 'checksum please':
            channel.sendall(str(self.md5_checksum).encode('utf-8'))
            channel.sendall(b'end')


class DownloadProcess(QThread):

    #Class representing single downloading thread
    class Download(QThread):
        def __init__(self, port, ip, file_path, DM):
            print('port: ', port, ' ip:', ip, ' file_path:', file_path)
            QThread.__init__(self)
            self.port = port
            self.ip = ip
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('Download start for port ', port)
            self.s.connect((self.ip,self.port))
            self.f = open(file_path, 'wb')
            self.DM = DM

        def run(self):
            print('Download at port ', str(self.port), 'started')
            self.s.send(b'more please')
            data = self.s.recv(CHUNK_SIZE)
            while data != b'No MoRe bYYtes!#$@!df so sad :<':
                self.DM.got += len(data)
                self.f.write(data)
                self.s.sendall(b'more please')
                data = self.s.recv(CHUNK_SIZE)
            self.f.flush()
            self.f.close()
            self.s.close()
            print('Thread no',str(self.port - 8880),'finished downloading')
            self.DM.dones[self.port - 8881] = True
            print(self.DM.dones)

    #Class to manage single downloading threads
    class DownloadManager(QObject):

        class DownloadChecker(QThread):
            def __init__(self, DM):
                QThread.__init__(self)
                self.DM = DM

            def run(self):
                while True:
                    if self.DM.dones == [True]*self.DM.threads:
                        f = open(self.DM.folder_path + '/' + self.DM.name, 'wb')
                        part_files = []
                        for i in range(1, self.DM.threads + 1):
                            part_files.append(self.DM.folder_path + '/' + 'filepart.' + str(i))
                        for file in part_files:
                            fr = open(file,'rb')
                            f.write(fr.read())
                        f.flush()
                        f.close()
                        break
                    else:
                        time.sleep(0.5)

        class ProgressCalculator(QThread):
            def __init__(self, DM):
                QThread.__init__(self)
                self.DM = DM

            def run(self):
                while self.DM.dones != [True]*self.DM.threads:
                    speed = self.calculateSpeed()
                    self.DM.speed = speed
                    QObject.emit(self.DM, SIGNAL('percentUpdate(int)'), percent(self.DM.got, self.DM.size))
                    print(speed, 'kb/s')

            def calculateSpeed(self):
                got1 = self.DM.got
                time.sleep(1)
                got2 = self.DM.got
                d_got = got2 - got1 #Delta of got bytes
                return d_got/1000 #Return in kbps

            def est_time(self):
                size = self.DM.size
                t = size/self.calculateSpeed()
                return t/60 #Return in minutes

        #Download Manager constructor
        def __init__(self, ip=None, main_socket=None, folder_path=None):
            QObject.__init__(self)
            self.ip = ip
            self.main_socket = main_socket
            self.folder_path = folder_path
            self.references = []
            self.size = 0
            self.got = 0
            self.speed = 0
            self.est_time = 0
            self.progress = self.ProgressCalculator(self)


        def getData(self):
            self.main_socket.sendall(b'name please')
            self.name = self.main_socket.recv(1024).decode('utf-8')
            print('File name: ', self.name)
            self.main_socket.sendall(b'size please')
            self.size = int(self.main_socket.recv(1024).decode('utf-8'))
            print('Amount of bytes: ', self.size)
            self.main_socket.sendall(b'threads please')
            self.threads = int(self.main_socket.recv(1024).decode('utf-8'))
            print('Threads: ', self.threads)
            self.dones = [False]*self.threads
            self.DC = self.DownloadChecker(self)

        def startDownload(self):
            self.main_socket.sendall(b'file please')
            self.DC.start()
            self.progress.start()
            if self.main_socket.recv(1024).decode('utf-8') == 'sockets created':
                print('Download is starting')
                for i in range(1, int(self.threads)+1):
                    download = DownloadProcess.Download(8880+i, self.ip, self.folder_path+'/filepart.'+str(i), self)
                    self.references.append(download)
                    download.start()
    def __init__(self):
        QObject.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.DM = self.DownloadManager()

    def config(self, ip, path=None):
        self.ip = ip
        if path is not None:
            self.path = path
        else:
            self.path = Config.data['CWD']
        self.s.connect((self.ip, 8880))
        print('IP address set for ', self.ip)

    def run(self):
        self.DM.ip = self.ip
        self.DM.main_socket = self.s
        self.DM.folder_path = self.path
        self.DM.getData()
        self.DM.startDownload()
        self.s.close()