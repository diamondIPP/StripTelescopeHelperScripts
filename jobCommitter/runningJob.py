#! /usr/bin/env python
# encoding: utf-8
import time
import subprocess
import os
import RunListReader
import sys
from random import randrange

def extant_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.exists(x):
        raise argparse.ArgumentError("{0} does not exist".format(x))
    return x

def ensure_dir(f):
    d = os.path.dirname(f)
    d = os.path.expandvars(d)
    d = os.path.abspath(d)
#     print 'ensure %s'%d
    if not os.path.exists(d):
        os.makedirs(d)
        
class runningJob:
    timeout = 0+60*(0+60*(0+24*1)
    def __init__(self):
        self.child = None
        self.jobNo = -1
        self.logfile = None
        self.logfilename = None
        self.jobStarted = 0
        self.isStarted = False
    
    def is_finished(self):
        if self.child == None:
            return True
        return self.child.poll()!=None

    def succeded(self):
#     print 'succeded',counter
        err =None
        out =None
        if self.child == None:
            out, err = self.child.communicate()
        runnumber = reader.get_run_number(counter)
        i = 0
        #ofile.close()
        if self.logfile != None:
            self.logfile.close()
    #             print 'del logfile %s %s'%(count,name)
            del self.logfile
        return self.analyzeLogfile()
    
    def analyzeLogfile(self):
        if self.logfilename == None:
            print 'cannot read from child'
            return False
        else:
            try:
                logfile = open(self.logfilename,'rb')
                for line in logfile.readlines():
                    if 'DONE_ALL' in line:
                        print 'suceeded with child'
                        logfile.close()
                        return True
        #         print 'problem with child'
                logfile.close()
            except: 'cannot find name %s'%name
        return False

def start_job(rowNo):
#     print_status()
#     print "start_job",rowNo
    row = reader.started_run()
    print 'start_run',reader.counter
    count = reader.get_count(reader.counter)
    directory='%s/ana%d/'%(mainDir,reader.runningCounter%nMaxJobs)
    print directory
    create_RunList(row,directory)
    sleepTime =  randrange(5,10)
    print 'start', count,reader.counter,row
    
    if not args.testing:
        command = 'cd %s;'%directory
        command += ' %s -s %s -i %s -o %s'%(rd42Analysis,settingsDir,inputDir,outputDir)
#         print command
    else:
        command  = 'echo TEST; sleep %s'%sleepTime
        if randrange(0,2):
            command += '; echo "DONE_ALL %s"'%reader.counter
        else:
            command += '; echo "FAILED %s"'%reader.counter
        print command
#     print 'start subprocess "%s"'%reader.counter
    runnumber = reader.get_run_number(reader.counter)
    filename = get_new_logfile_name(runnumber)
#     print 'open %s'%filename
    logfile = open(filename,'wb')
    child =  subprocess.Popen(command, shell = True,universal_newlines=True, stderr=subprocess.STDOUT, stdout=logfile)
#     childs.append(child)
    runningJobs[rowNo] = child
    logfiles[rowNo] = logfile
    


def wait_for_jobs_finish():
    global runningJobs
    print 'wait until finished'
    leftJobs = len(runningJobs)
    while leftJobs>0:
        runningJobs = check_running_jobs(runningJobs)
        if len(runningJobs)!=leftJobs:
            print_status()
            
            leftJobs = len(runningJobs)
            print ', left jobs' %leftJobs,
        time.sleep(.1)
    print ' last run finished'


rownum = 0
nColumns = 0
entryNo = []
lastCheck = time.time()

# for run in reader.runList:
#     print run

try:
    while True:
        if not reader.get_left_runs():
            break
        if len(runningJobs) < nMaxJobs:
#             print 'get next run',len(runningJobs),nMaxJobs
#             print 'get run'
            run = reader.get_next_run()
#             print 'got'
#             print run
            rowNo = reader.get_row_number()
#             print rowNo,run
            if not runningJobs.has_key(rowNo):
                start_job(rowNo)
                print '\n'
#                 print' job started'
            else:
                pass
#                 print 'there is already a running job for row %s'%rowNo
        runningJobs = check_running_jobs(runningJobs)
        flush_logfiles()
        now = time.time()
        if now - lastCheck > .5:
            print_status()
            lastCheck = now
        time.sleep(.1)
#     checkedList = [check_run(row) for row in rows]
    #print checkedList
    print' No more runs to start',runningJobs
    leftJobs = len(runningJobs)
#     print 'test'
    wait_for_jobs_finish()
except Exception,e:
    print Exception,e
    pass


reader.write_csv_RunList(filename)


exit()


#
#
#command  = 'echo TEST; sleep 10; echo ""'
#child =  subprocess.Popen(command, shell = True, stdout=subprocess.PIPE)
#childs.append(child)
#
#command  = 'echo TEST; sleep 20; echo "DONE ALL"'
#child =  subprocess.Popen(command, shell = True, stdout=subprocess.PIPE)
#childs.append(child)
#
#finished = False
#finishedList = [is_finished(child) for child in childs]
#while not finished:
#    time.sleep(.1)
#    for child in childs:
#        if is_finished(child):
#            pass
#            #succeded(child)
#    finished = all(finishedList)
#    print 'checked: ',finishedList
#
#print out,'\n\nERROR:\n',err
#
