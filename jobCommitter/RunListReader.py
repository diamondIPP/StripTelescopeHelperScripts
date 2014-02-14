from sets import Set
import time
import csv
import subprocess
import os
import RunList
import ROOT
import errno
import copy
import os
import shutil

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
        
class RunListReader:
    def __init__(self,write_file,correctionMacro):
        self.rows = []
        self.header = None
        self.counter = -1 
        self.rawHeader = None
        self.nMaxTries = 10
        self.runningCounter = 0
        self.runs = {}
        self.runList = {}
        self.runListKeys = []
        self.outputDir = ''
        self.settingsDir = ''
        self.verbose = False
        correctionMacro = os.path.expanduser(correctionMacro)
        if os.path.exists(correctionMacro):
            self.correctionMacro = correctionMacro
        else:
            self.correctionMacro = ''
        self.write_file = bool(write_file)
        self.add_correction = (correctionMacro!='')
        print 'DORING CORRECTION: "%s '%self.correctionMacro
        if self.add_correction:
            ROOT.gROOT.LoadMacro('%s++'%self.correctionMacro)

    def read_csv_RunList(self,filename,resetLevel=0):
        print 'reading: %s'%filename
        self.filename = filename
        rows =[]
        f = open('%s'%filename,'rU')
        reader = csv.reader(f,dialect='excel',delimiter=';')
        for row in reader:
            rows.append(row)
        f.close()
        if len (rows) >0:
            row = rows[0]
            self.rawHeader = row
            self.header = {row[i]: i for i in range(0, len(row))}
            row[0]='#' 
            pass
        if self.header:
            rows = rows[1:]
        self.read_rows(rows,resetLevel)
        self.add_corrected_runs()

    def write_csv_RunList(self,filename):
        print '\nwrite RunList file: ',filename
        if not self.write_file:
            return
        ofile = open(filename,'wb')
        writer = csv.writer(ofile, delimiter=';', dialect='excel')
        if self.header != None:
            writer.writerow(self.rawHeader)
        self.check_run_list()
        rows = [self.runList[run].get_csv_output() for run in self.runListKeys]
        for row in rows:
            writer.writerow(row)
        ofile.close()
        
    def check_run_list(self):
        for key in self.runList:
            if not run in self.runListKeys:
                print 'cannot find run %s'%key
                self.runListKeys.append(key)

        for run in self.runListKeys:
            if not self.runList.has_key(run):
                print 'cannot find run %s in runlist '%run
        
    def read_rows(self,rows,resetLevel):
#         print 'read rows %s'%len(rows)
        self.runList = {}
        self.runListKeys = []
        i =0
        nComments = 0
        for row in rows:
            run = RunList.RunList(data=row,rowNo = i)
            if not run.is_valid():
                nComments += 1
                run.runNo = -nComments
            runNo = run.get_run_number()
            runDes = run.runDes
            if (resetLevel%1==0):
                run.nTries = 0
            if (resetLevel/2==1):
                run.status = 0
            key = (runNo,runDes)
            if self.runList.has_key(key):
                print' %s already exists, skip'%key
            else:
#                     print 'add run %s %s'%(runNo, run.do_correction())
                self.runList[key] = run
                self.runListKeys.append(key)
        print 'runList consists out of %s runs\n'%len(self.runList)

    
    def get_run_number_of_count(self,count):
        count = self.get_count(count)
        runNo = self.runListKeys[count][0]
        return runNo
    
    def get_run_description_of_count(self,count):
        count = self.get_count(count)
        runDesc = self.runListKeys[count][1]
        return runDesc
#
#    def update_runs(self):
#        i = 0
#        for row in self.rows:
#            run = RunList.RunList(data=row,rowNo = i)
#            if run.is_valid():
#                self.runList.append(run)
#            if not self.is_invalid_row(row):
#                try:
#                    runNo = int(row[1])
#                except:
#                    runNo = -1
#                if runNo != -1:
#                    self.runs[runNo] = i 
#            i += 1
##         print self.runs, len(self.runs)
        
    def add_corrected_runs(self):
#         print 'add corrected runs'
        for key in self.runList.keys():
            run = self.runList[key]
            if not run.is_valid():
                continue
            if run.do_corrections:
                self.add_feed_through_corrected_run(key)
        pass
    
    def has_run(self,key):
        retVal = self.runList.has_key(key)
        return retVal

    def get_row_number(self):
        if len(self.runList) == 0:
            return -1
        return self.counter%len(self.runList)
    
    def get_left_runs(self):
        checkList = [self.runList[run].check_run() for run in self.runList]
        return sum(checkList)
    
    def createCorrectedRunDirectory(self,run):
        path = self.outputDir+'/%s/'%run.get_corrected_run_number()
        mkdir_p(path)

    def create_raw_data_link(self,run):
        corRunNo = run.get_corrected_run_number()
        dst = self.outputDir+'/%s/rawData.%d.root'%(corRunNo,corRunNo)
        src =  self.outputDir+'/%s/rawData.%d.root'%(run.get_run_number(),corRunNo)
        if not os.path.exists(src):
            print 'cannot create link: source does not exists! %s'%src
        if not os.path.exists(dst):
            if os.path.islink(dst):
                print 'is link: %s'%dst
                os.remove(dst)
                print 'removed %s'%dst
            try:
                os.symlink(src, dst)
            except:
                print 'cannot create symlink: ln -s %s %s'%(src,dst)
        
    def create_corrected_settings_file(self,run):
        corRunNo = run.get_corrected_run_number()
        runNo = run.get_run_number()
        src = run.get_settings_file_name(self.settingsDir)
        dst = src
        dst = dst.replace('%s'%runNo, '%s'%corRunNo)
        if not os.path.exists(dst):
            os.symlink(src,dst)
        print 'create settings file: %s from %s, --> %s'%(dst,src,os.path.exists(dst))
        
    def calculateCorrection(self,run): 
        corRunNo = run.get_corrected_run_number()
        runNo = run.get_run_number()
        src =  self.outputDir+'/%s/rawData.%d.root'%(runNo,corRunNo)
        if os.path.exists(src):
            print 'correction already exists: %s'%src
            return
        siliconCor,diamondCor = run.get_crosstalk_corrections(self.outputDir)
#         print siliconCor,diamondCor
        ROOT.gSystem.cd('%s/%s/'%(self.outputDir,runNo))
#         print'ROOT gSystem directory: %s'%ROOT.gSystem.pwd()
        command = 'createAsymmetricEtaSample(%s,%2.3f,%2.3f,%d)'%(runNo,siliconCor,diamondCor,corRunNo)
        print command
        print ROOT.gSystem.pwd()
        #answer = raw_input('check command, Perform?')
        answer = 'y'
        
        if answer == 'y':
            retVal = ROOT.gROOT.ProcessLine(command)
    
    def add_feed_through_corrected_run(self,runNo):
        if not self.add_correction:
            return
        print 'add correction'
        if runNo / 1e6 > 1:
            return
        if not self.has_run(runNo):
            print 'cannot find runNo:%s '%runNo
            return 
        run = self.runList[runNo]
        if not run.do_correction():
            return
#         print 'run %s/%s: %s'%(runNo,run.get_run_number(),run.do_correction())
        corRunNo = run.get_corrected_run_number()
        if self.has_run(corRunNo):
#             print 'RUN %s has already a corrected run %s'%(runNo,corRunNo)
            return
        if run.has_valid_crosstalk_corrections(self.outputDir):
            print 'add feed through corrected run: %s'%runNo
            self.calculateCorrection(run)
            self.createCorrectedRunDirectory(run)
            self.create_raw_data_link(run)
            self.create_corrected_settings_file(run)
            newRun = copy.deepcopy(run)
            newRun.runNo = corRunNo
            newRun.correction = False
            newRun.status = 0
            newRun.tries = 0
            key = newRun.get_key()
            self.runList[key] = newRun
            
            self.runListKeys.append(key)
        else:
#             print 'ERROR: INVALID CROSS TALK CORRECTION FILE!'
            pass
#             print run
#             print self.runListKeys, self.runList[corRunNo]
        self.write_csv_RunList(self.filename)

#     def correct_feed_through(self,runNo):
#         correction = FeedThroughCorrection.FeedThroughCorrection(runNo)
#         correction.doCorrection()
#         
#     def has_settings(self,run):
#         settingsFileName = run.get_settings_file_name(self.settingsDir)
#         retVal =  os.path.exists(settingsFileName)
#         return retVal

#     def first_try(self,row):
#         if self.get_status(row) == 0:
#             return True
#         else:
#             return False
    
    def get_count(self,counter):
        return counter %len(self.runList)
    
    def succeded(self,counter):
        counter  = self.get_count(counter)
#         print counter, len(self.runListKeys),len(self.runList)
        runNo = self.runListKeys[counter]
        self.runList[runNo].status +=1
        self.write_csv_RunList(self.filename)
    
    def failed(self,counter):
#         counter  = self.get_count(counter)
# #         print counter, len(self.runListKeys),len(self.runList)
#         runNo = self.runListKeys[counter]
        self.write_csv_RunList(self.filename)

        
    
    def get_run_number(self,counter):
        if len(self.runList) == 0:
            return -1
        counter = self.get_count(counter)
        runNo = self.runListKeys[counter][0]
        return runNo
    
    def started_run(self):
#         print 'started run'
        self.runningCounter  +=1
        count = self.counter%len(self.runList)
        key = self.runListKeys[count]
        run = self.runList[key]
        row = run.run()
        return row
        
    def get_next_run(self,runningJobs):
        i = 0
        checkRunsAlreadyRunning = Set()
        while i< len(self.runListKeys)*2:
            self.counter += 1
            i+=1
            count = self.get_count(self.counter)
            if self.verbose: print 'get next ',count,len(self.runList),len(self.runListKeys)
            if  self.runList[self.runListKeys[count]].check_run():
                
                #self.rows[count]):
                runNo = self.runListKeys[count][0]
                if self.verbose: print 'found run %s %s'%(count,runNo)
                if runNo in runningJobs:
                    checkRunsAlreadyRunning.add(runNo)
#                     print 'Found: %s - Cannot Start since already runnig...'%runNo
                else:
                    if self.verbose: print 'get run %s'%runNo
                    if self.verbose: print self.runListKeys[count] 
                    retVal = self.runList[self.runListKeys[count]]
                    if self.verbose: print 'got retVal'
                    return retVal
            else:
                pass
#                 print 'checked run %s'%count
#         print 'could not find a run which is not already running...%s,%s'%(runningJobs,checkRunsAlreadyRunning)
        return None