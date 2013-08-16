__author__ = 'Jerzy Spendel'
import os


class Config(object):
    def init():
        Config.data = {}
        path = os.path.expanduser('~') + '/.lantransfer.conf'
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