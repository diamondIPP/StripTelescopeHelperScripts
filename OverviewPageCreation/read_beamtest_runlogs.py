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
        for runlog in runlogs:
            self.read_runlog(runlog)

    def get_list_of_runlogs(self):
        dir = self.config.get('RunLogs','directory')
        print 'find all runlogs:'
        runlogs = filter(lambda x:x.endswith('.txt'),os.listdir(dir))
        for runlog in runlogs:
            print ' * ',runlog
        return runlogs
    def read_runlog(self,runlog):
        runlog_no = int(runlog[0:2])
        print 'runlog_no',runlog_no
        path = self.config.get('RunLogs','directory')
        if not path.endswith('/'):
            path+='/'
        path+=runlog
        print path
        f = open(path)
        for line in f.readlines():
            if str(runlog_no) in line:
                splitted = line.split()
                valid = False
                try:
                    int(splitted[0])
                    valid = True
                except:
                    pass
                try:
                    int(splitted[1])
                    valid = True
                    splitted = splitted[1:]
                except
                    pass
                if valid:
                    print splitted


if __name__ == "__main__":
    r = runLogReader('config/')
    r.update_runlogs()
