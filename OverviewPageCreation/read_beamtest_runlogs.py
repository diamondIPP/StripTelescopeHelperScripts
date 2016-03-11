import ConfigParser
import csv
import os
import utilities


class  runLogReader:
    def __init__(self,configdir):
        self.verbosity = False
        self.configdir = configdir
        self.configFileName = configdir + '/creation.ini'
        print '    - read', self.configFileName
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.configFileName)
        for i in self.config.sections():
            # if self.verbosity:
            print '        - ',i, self.config.options(i)
    def update_runlogs(self):
        runlogs = self.get_list_of_runlogs()

    def get_list_of_runlogs(self):
        dir = self.config.get('RunLogs','directory')
        print 'find all runlogs:'
        runlogs = filter(lambda x:x.endswith('.txt'),os.listdir(dir))
        for runlog in runlogs:
            print ' * ',runlog


if __name__ == "__main__":
    r = runLogReader('config/')
    r.update_runlogs()
