import ConfigParser
import csv
import os
import utilities
import collections


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
        all_runs = []
        for runlog in runlogs:
            all_runs.extend(self.read_runlog(runlog))
        return all_runs

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
                    runs.append(splitted)
        return self.analyze_runs(runs)
    def analyze_runs(self,runs):
        for i in range(0,len(runs)):
            runs[i] = self.analyze_run(runs[i])
            print runs[i]
        return runs

    def analyze_run(self,rundata):
        run = collections.OrderedDict()
        try:
            run['runNo'] = int(rundata[0])
            diamonds =  rundata[1]
            if ',' in diamonds:
                diamonds =  diamonds.split(',')
                diamonds = '/'.join(diamonds)
            run['diamond'] = diamonds
            voltage = rundata[2]
            # if '/' in voltage:
            #     voltage = voltage.split('/')
            #     for i in range(0,len(voltage)):
            #         voltage[i] = int(voltage[i])
            if ',' in voltage:
                voltage = voltage.split(',')
                voltage = '/'.join(voltage)
                # for i in range(0,len(voltage)):
                #     voltage[i] = int(voltage[i])
            else:
                voltage = int(voltage)
            run['biasVoltage'] = voltage
            try:
                run['filesize'] = rundata[7]
                run['events'] = rundata[8]
            except:
                print 'missing item in ',rundata
            try:
                if not rundata[9].startswith('I'):
                    print 'invalid  data for current in ',rundata
                else:
                    run['current']= rundata[9]
            except:
                # print 'missing current in ',rundata
                pass
            # print run
        except:
            print 'cannot convert',rundata
        return run



if __name__ == "__main__":
    r = runLogReader('config/')
    r.update_runlogs()
