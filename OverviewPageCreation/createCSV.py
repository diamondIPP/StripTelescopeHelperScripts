import ConfigParser
import csv
import pickle

class csvCreater:
    def __init__(self):
        self.read_pickle()
        self.runList = self.read_run_list_map('runlist.csv')
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
                    if not runList.has_key(row)
                        runList[row]= {}
                    runList[row]+
                    runList.append(row)
        results = [[int(i[0]),int(i[1])] for i in runList]
        runList = dict(results)
        return runList

    def find_runs(self):


    def write_run_list(self,outputfile,outputList):
        with open (outputfile,'wb') as csvfile:
            writer = csv.writer(csvfile,delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(outputList)

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

    def create_list(self):
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




