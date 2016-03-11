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
        runlog_str = runlog[0:2]
        runlog_no = int(runlog_str)
        print 'runlog_no',runlog_no
        path = self.config.get('RunLogs','directory')
        if not path.endswith('/'):
            path+='/'
        path+=runlog
        print path
        f = open(path)
        runs = []
        for line in f.readlines():
            if str(runlog_no) in line:
                splitted = line.split()
                valid = False
                for i in range(0,2):
                    if len(splitted) >i and splitted[i].startswith(runlog_str):
                        try:
                            int(splitted[i])
                            splitted = splitted[i:]
                            valid = True
                            break
                        except:
                            pass
                if valid:
                    print splitted
                    runs.append(splitted)
        return self.analyze_runs(runs)
    def analyze_runs(self,runs):
        for i in range(0,len(runs)):
            runs[i] = self.analyze_run(runs[i])
        return runs
    def analyze_run(self,rundata):
        run = {}
        try:
            run['number'] = int(rundata[0])
            diamonds =  rundata[1]
            if ',' in diamonds:
                diamonds =  diamonds.split(',')
            elif '/' in diamonds:
                diamonds =  diamonds.split('/')
            run['diamonds'] = diamonds
            voltage = rundata[2]
            if '/' in voltage:
                voltage = voltage.split('/')
                for v in voltage:
                    v = int(v)
            else:
                voltage = int(voltage)
            try:
                run['voltage'] = voltage
                run['filesize'] = rundata[7]
                run['events'] = rundata[8]
                run['current']= rundata[9]
            except:
                pass
            print run
        except:
            print 'cannot convert',rundata
        return run


        run[0] = int()



if __name__ == "__main__":
    r = runLogReader('config/')
    r.update_runlogs()
