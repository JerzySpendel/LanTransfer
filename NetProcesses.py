# -*- coding: UTF-8 -*-

__author__ = 'Jerzy Spendel'
import socket
import time
import os
import hashlib
from Utils import Config
from PyQt4.QtCore import *

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
        def __init__(self, file):
            QThread.__init__(self)
            self.file = file

        def run(self):
            f = open(self.file, 'rb')
            m = hashlib.md5()
            for chunk in f:
                m.update(chunk)
            self.emit(SIGNAL('md5checksum(PyQt_PyObject)'),m.hexdigest())
    class GeneratorUpload(QThread):
        def __init__(self, port, generator, parent=None):
            QThread.__init__(self, parent)
            self.port = port
            self.generator = generator
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.s.bind(('',self.port))
                self.s.listen(10)
            except OSError:
                print('Couldn\'t assign port (might be already in use), try again')

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
        try:
            self.s.bind(('', 8880))
        except OSError:
            print('Some socket is already using port 8880. Try later.')
            print('QUITTING')
            quit()
        self.s.listen(10)

        self.references = []
    def config(self, path_to_file):
        self.path = path_to_file
        self.name = os.path.basename(self.path)

    def run(self):
        QObject.emit(self, SIGNAL('makeBusy()'))
        channel, addr = self.s.accept()
        QObject.emit(self, SIGNAL('unmakeBusy()'))
        f = open(self.path, 'rb')
        sent = 0
        bytes = os.path.getsize(self.path)
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
            md5computer = self.ComputeMD5(self.path)
            self.references.append(md5computer)
            md5computer.start()
            QObject.connect(self.references[len(self.references)-1], SIGNAL('md5checksum(PyQt_PyObject)'), self.sendmd5)
            channel.sendall(b'sockets created')
        if channel.recv(1024).decode('utf-8') == 'checksum please':
            channel.sendall(str(self.md5_checksum).encode('utf-8'))
            channel.sendall(b'end')

    def sendmd5(self,checksum):
        print(checksum)

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
            self.file = open(file_path, 'wb')
            self.DM = DM

        def run(self):
            print('Download at port ', str(self.port), 'started')
            self.s.send(b'more please')
            data = self.s.recv(CHUNK_SIZE)
            while data != b'No MoRe bYYtes!#$@!df so sad :<':
                self.DM.got += len(data)
                self.file.write(data)
                self.s.sendall(b'more please')
                data = self.s.recv(CHUNK_SIZE)
            self.file.flush()
            self.file.close()
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

            def checkMD5(self):
                pass

            def run(self):
                while True:
                    if self.DM.dones == [True]*self.DM.threads:
                        f = open(self.DM.folder_path + '/' + self.DM.name, 'wb')
                        part_files = []
                        for i in range(1, self.DM.threads + 1):
                            part_files.append(self.DM.folder_path + '/' + 'filepart.' + str(i))
                        for file in part_files:
                            fr = open(file,'rb')
                            try:
                                os.remove(file)
                            except IOError:
                                print('I do not have acces to delete part files. Do it yourself.')
                            except Exception:
                                print('Error while deleting files')
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
                while not self.DM.isDone():
                    speed = self.calculateSpeed()
                    time = self.est_time(speed)
                    QObject.emit(self.DM, SIGNAL('speedUpdate(int)'), speed)
                    QObject.emit(self.DM, SIGNAL('timeUpdate(PyQt_PyObject)'), time)
                    QObject.emit(self.DM, SIGNAL('percentUpdate(int)'), percent(self.DM.got, self.DM.size))
                    print(speed, 'kb/s')

            def calculateSpeed(self):
                got1 = self.DM.got
                time.sleep(1)
                got2 = self.DM.got
                d_got = got2 - got1 #Delta of got bytes
                return d_got/1000 #Return in kbps

            def est_time(self, speed):
                if speed != 0:
                    return int((self.DM.size-self.DM.got)/(speed*1000))
                else:
                    return '...'

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

        #self.dones contains list of done thread
        def isDone(self):
            if self.dones == [True]*self.threads:
                return True
            else:
                return False

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

    def config(self, ip, folderpath=None, filepath=None):
        self.ip = ip
        if folderpath is not None:
            self.folderpath = folderpath
        else:
            self.folderpath = Config.data['CWD']
        if filepath is not None:
            self.filepath = filepath
        else:
            self.filepath = None
        try:
            self.s.connect((self.ip, 8880))
        except Exception:
            print('[Info] Already connected')
        print('IP address set for ', self.ip)

    def run(self):
        #Both folder_path and file_path will be given to DM, but file_path has precedence and DM will use folder_path only if file_path == None
        self.DM.ip = self.ip
        self.DM.main_socket = self.s
        self.DM.folder_path = self.folderpath
        self.DM.file_path = self.filepath
        self.DM.getData()
        self.DM.startDownload()
        self.s.close()