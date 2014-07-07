import ConfigParser
import csv
import pickle
import dictCreater

class csvCreater:
    def __init__(self):
        self.read_pickle()
        self.runList = self.read_run_list_map('runlist.csv')
        self.add_log()
        self.find_runs()
        self.get_missing_runs()
        pass

    def read_pickle(self):
        print 'get result data from pickle file'
        self.results = pickle.load(open('data.pkl','rb'))

    def read_run_list_map(self,filename):
        with open(filename,'rb') as csvfile:
            reader =  csv.reader(csvfile, delimiter=',')
            runList = {}
            for row in reader:
                runno = int(row[0])
                events = int(row[1])
                if runno/10000>0:
                    if not runList.has_key(runno):
                        runList[runno]= {}
                    runList[runno]['events'] = events
                    runList[runno]['keys']=[]
        return runList

    def find_runs(self):
        for key in self.results:
            runno = self.results[key].getint('RunInfo','runno')
            if not self.runList.has_key(runno):
                print 'cannot find runnno',runno
                continue
            if not self.runList[runno].has_key('keys'):
                self.runList[runno]['keys']=[]
            self.runList[runno]['keys'].append(key)
            # print self.runList[runno]
        pass

    def add_log(self):
        print 'add log'
        r = dictCreater.dictCreater('config/')
        listed = r.get_combined_list()
        for key in listed:
            if self.runList.has_key(key):
                self.runList[key].update(listed[key])
                print '\n',key,self.runList[key]
                if self.runList[key]['keys']:
                    self.runList[key]['keys'] = []
            else:
                print 'no key ',key
        raw_input()


    def get_missing_runs(self):
        missingRuns = []
        missingParts = []
        for runno in self.runList:
            try:
                nKeys = len(self.runList[runno]['keys'])
            except:
                nKeys = 0
            if not nKeys:
                if not self.runList[runno].has_key('diamond'):
                    print
                diamonds = self.runList[runno].get('diamond',['unknown'])
                missingRuns.append((runno,len(diamonds)))
            if nKeys%2==1:
                missingParts.append((runno,nKeys,self.runList[runno]['keys']))
            print runno,nKeys
        print len(missingRuns),'missing Runs are',missingRuns
        print len(missingParts),'partially missing Parts are',missingParts

    def write_run_list(self,outputfile,outputList):
        with open (outputfile,'wb') as csvfile:
            writer = csv.writer(csvfile,delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(outputList)

    def has_to_rerun(self,key):
        svnrev = self.results[key].get('RunInfo','svn_rev')
        svnrev = int(svnrev.strip('M'))
        if self.results[key].get('RunInfo','svn_rev').endswith('M'):
            svnrev+=.5
        if svnrev <1141:
            print 'needs to be rerun: ',key,self.results[key].get('RunInfo','svn_rev')
            return True
        return False

    def is_valid_run(self,run,dia):

        return True

    def get_list_entry(self, run,events,descr):
        return ['',run,descr,0,events]

    def get_n_diamonds(self,run):
        return 1

    def get_description(self,dia,nDias):
        if nDias == 2:
            if dia == 0:
                return 'left'
            else:
                return 'right'
        return '0'


    def get_runs_to_rerun(self):
        reruns = []
        runs =[]
        for key in self.results:
            if self.has_to_rerun(key):
                reruns.append(key)
                runno = self.results[key].get('RunInfo','realrunno')
                if self.results[key].has_option('RunInfo','events'):
                    events = self.results[key].get('RunInfo','events')
                else:
                    no = self.results[key].getint('RunInfo','runno')
                    if  self.runList.has_key(no):
                        events = self.runList.get(no).get('events',-1)
                    else:
                        events = -1
                descr =  self.results[key].get('RunInfo','descr.')
                runs.append([runno,descr,events])
                if events <=0:
                    print runs[-1],runno,descr
        return runs



    def create_list(self):
        print 'to be rerun: ',self.get_runs_to_rerun()
        print 'create output list'
        outputList=[]
        for run in sorted(self.runList.keys()):
            if run /10000==0:
                continue
            nDias = self.get_n_diamonds(run)
            for dia in range(nDias):
                if self.is_valid_run(run,dia):
                    events = self.runList[run]
                    descr = self.get_description(dia,nDias)
                    outputList.append(self.get_list_entry(run,events,descr))
        outputfile= 'test.csv'
        self.write_run_list(outputfile,outputList)
        pass
   


if __name__=="__main__":
    creator = csvCreater()
    creator.create_list()




