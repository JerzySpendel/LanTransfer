__author__ = 'Jerzy Spendel'
import os
import re
import lzma

#Simple regex to extract ip address and name from saved contacts
regex = re.compile(r'(?P<IP>([0-9]{1,3}\.){3}[0-9]{1,3}) - (?P<NAME>.*)')
OPTIONS = ('CHUNK_SIZE', 'THREADS', 'DOWNLOAD_MAX', 'UPLOAD_MAX', 'COMPRESS')


class Config(object):
    data = {}

    def init():
        Config.data = {}
        Config.path = os.path.expanduser('~') + '/.lantransfer.conf'
        path = Config.path
        if not os.path.exists(path):
            Config.file = open(path, 'w')
            lines = ['CHUNK_SIZE:NONE\n','THREADS:NONE\n', 'DOWNLOAD_MAX:NONE\n', 'COMPRESS:False\n', 'UPLOAD_MAX:NONE\n', '-----CONTACTS-----\n']
            Config.file.writelines(lines)
            Config.file.close()
        Config.file = open(path, 'r+')
        Config.parse()
        Config.openContacts()

    def parse():
        lines = []
        for line in open(Config.path,'r'):
            if line.split(':')[0] in OPTIONS:
                lines.append(line)
        for line in lines:
            data = line.split(':')
            Config.data[data[0]] = data[1].strip()
        Config.data['CWD'] = os.path.dirname(__file__)
        Config.initResourcePaths()

        if Config.data['THREADS'] == 'NONE':
            Config.data['THREADS'] = 1
        if (True if Config.data['COMPRESS'] =='True' else False) == True:
            Config.data['COMPRESS'] = True
        else:
            Config.data['COMPRESS'] = False

    def initResourcePaths():
        cwd = Config.data['CWD']
        Config.data['EXIT_PNG'] = cwd + '/resources/exit.png'
        Config.data['CONFIGURE_PNG'] = cwd + '/resources/configure.png'
        Config.data['ABOUT_PNG'] = cwd + '/resources/about.png'
        Config.data['GNU_PNG'] = cwd + '/resources/gnu.png'
        Config.data['GENERAL_SETTINGS'] = cwd + '/resources/general.png'
        Config.data['NETWORK_SETTINGS'] = cwd + '/resources/network.png'

    def changeProperty(name,value):
        configF = open(Config.path, 'r')
        lines = configF.readlines()
        for line in lines:
            property = line.strip().split(':')[0]
            if name == property:
                index = lines.index(line)
                lines[index] = property+':'+str(value)+('\n' if line.count('\n')>0 else '')
        configF = open(Config.path, 'w')
        configF.writelines(lines)
        configF.close()

    def saveContacts(data):
        all = regex.findall(data)
        tosave = []
        for line in open(Config.path, 'r'):
            if (line.split(':')[0] in OPTIONS) or (line == '-----CONTACTS-----') or (line == '-----CONTACTS-----\n'):
                tosave.append(line)
        for found in all:
            tosave.append(found[0] + ' - ' + found[len(found)-1]+'\n')
        write = open(Config.path, 'w')
        write.writelines(tosave)
        write.close()

    #Returns list like this: [(IP1,NAME1),(IP2,NAME2)...]
    def openContacts():
        all = regex.findall(open(Config.path, 'r').read())
        result = []
        for found in all:
            result.append((found[0],found[len(found)-1]))
        return result
Config.init()

class Compressor():
    def __init__(self):
        if not 'COMPRESS' in Config.data:
            Config.init()

        if Config.data['COMPRESS'] == True:
            print('Compressor set to compress data')
            self.comp = self.compData
        else:
            print('Compressor set to back given data')
            self.comp = self.returnData

    def compData(self, data):
        return lzma.compress(data)

    def returnData(self, data):
        return data


class Decompressor():
    def __init__(self, createDecompressor):
        if createDecompressor:
            self.comp = self.decomp
        else:
            self.comp = self.returnData

    def decomp(self, data):
        return lzma.decompress(data)

    def returnData(self, data):
        return data
