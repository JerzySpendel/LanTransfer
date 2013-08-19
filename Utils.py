__author__ = 'Jerzy Spendel'
import os


class Config(object):
    def init():
        Config.data = {}
        Config.path = os.path.expanduser('~') + '/.lantransfer.conf'
        path = Config.path
        if not os.path.exists(path):
            Config.file = open(path, 'w')
            lines = ['CHUNK_SIZE:NONE\n','THREADS:NONE\n', 'DOWNLOAD_MAX:NONE\n', 'UPLOAD_MAX:NONE']
            Config.file.writelines(lines)
            Config.file.close()
        Config.file = open(path, 'r+')
        Config.parse()

    def parse():
        for line in Config.file.readlines():
            data = line.split(':')
            if not data[0].strip() in ('CHUNK_SIZE','THREADS', 'DOWNLOAD_MAX', 'UPLOAD_MAX'):
                raise Exception('Wrong data in config file, please delete config file to recreate it!')
            Config.data[data[0]] = data[1].strip()
        Config.data['CWD'] = os.path.dirname(__file__)
        print(Config.data['CWD'])
        Config.initResourcePaths()

        if Config.data['THREADS'] == 'NONE':
            Config.data['THREADS'] = 1

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
            Value = line.strip().split(':')[1]
            if name == property:
                print("if")
                index = lines.index(line)
                lines[index] = property+':'+str(value)+('\n' if line.count('\n')>0 else '')
        configF = open(Config.path, 'w')
        configF.writelines(lines)
        configF.close()
        print(lines)