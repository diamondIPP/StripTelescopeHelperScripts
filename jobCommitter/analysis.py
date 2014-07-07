#! /usr/bin/env python
# encoding: utf-8
import time
import subprocess
import os
import RunListReader
import sys
from random import randrange
from pickle import NONE
import argparse

def extant_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.exists(x):
        raise argparse.ArgumentError("{0} does not exist".format(x))
    return x

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true",dest='verbose')
parser.add_argument("-t", "--test", help="testing mode, do not start diamondAnalysis",
                    action="store_true",dest='testing')
parser.add_argument("--no-write", help="do not write new RunList.csv",
                    action="store_true")
parser.add_argument('-f', metavar='file', type=extant_file,
                     default='RunList.csv',
                     help='file to process (defaults to RunList.csv)')
parser.add_argument('-c','--add-correction',help="checks for feed over corrections and adds the runs",
                    action="store_true",dest='add_correction')
parser.add_argument('--reset',help='RunList.csv reset level.\nLevel:\n\t 0:\t none,\n\t 1:\t reset tries,\n\t 2:\t reset status,\n\t 3:\t reset both', 
        type=int,default=0,choices=range(0,4),metavar='LEVEL')
parser.add_argument('-j','--jobs',help='Number of running jobs',
        type=int,default=3,choices=range(1,9),metavar='NJOBS')
args = parser.parse_args()
print 'filename:', args.f
print 'correctino: ',args.add_correction
print 'write: ',args.no_write
print 'test: ',args.testing
print args.verbose
print args.reset
runningJobs = {}
childs = []

logfiles = {}
mainDir  ='/scratch/analysis/'
nMaxJobs = args.jobs

freeJobs = range(0,nMaxJobs)

filename =args.f
filename  = os.path.abspath(filename)
run_analysis = False
rd42Analysis = '~/sdvlp/rd42/branches/3dAnalysis/diamondAnalysis'
settingsDir = '~/sdvlp/rd42/trunk/run_settings/'
inputDir = '/scratch/testbeamdata'
outputDir = '/scratch/analysis/output/new'
if args.add_correction:
    correctionMacro = '~/sdvlp/rd42/trunk/createAsymmetricEtaSample.C'
else:
    correctionMacro = ''
reader  = RunListReader.RunListReader(not args.no_write,correctionMacro)
reader.outputDir = outputDir
reader.settingsDir = settingsDir
reader.read_csv_RunList(filename,args.reset)
leftJobs = 0
stdOutDir = './stdOut/'

def ensure_dir(f):
    d = os.path.dirname(f)
    d = os.path.expandvars(d)
    d = os.path.abspath(d)
#     print 'ensure %s'%d
    if not os.path.exists(d):
        os.makedirs(d)
        
def create_RunList(row,directory):
#     print 'create dir'
    ensure_dir(directory)
    filename = directory + '/RunList.ini'
    while filename.find('//') != -1:
        filename = filename.replace('//','/')
#     print filename
    ofile = open(filename,'wb')
    output = '\t'.join(['%s'%i for i in row])
    #print output
    ofile.write(output)
    ofile.close()


def flush_logfiles():
    if logfiles == None:
        print 'logfiles is of type NONE'
        return
    for i in logfiles:
        logfiles[i].flush()

def is_finished(child):
    return child.poll()!=None

def succeded(child,counter):
    if args.verbose:
        print 'succeded',counter
    err =None
    out =None
    if child == None:
        out, err = child.communicate()
    runnumber = reader.get_run_number(counter[1])
    i = 0
    #ofile.close()
    count = reader.get_count(counter[1])
    name = None
    if logfiles != None:
        if logfiles.has_key(count):
            logfiles[count].close()
            name = logfiles[count].name
            if args.verbose: print 'del logfile %s %s'%(count,name)
            del logfiles[count]
    filename = 'std-%d-%d_%d.out'%(runnumber,counter[1],i)
    filename = filename.replace('.out', '.err')
    if err != None:
        try:
            ofile = open(filename,'wb')
            ofile.write(err)
            ofile.close()
        except:
            pass
    if name == None:
        print 'cannot read from child'
        return False
    else:
        try:
            logfile = open(name,'rb')
            for line in logfile.readlines():
                if 'DONE_ALL' in line:
                    print 'suceeded with child',runnumber
                    logfile.close()
                    return True
    #       print 'problem with child'
            logfile.close()
        except: 'cannot find name %s'%name
    return False

def check_running_jobs(running_jobs):
    if running_jobs == None:
        print 'running jobs == None'
        return
    keys = running_jobs.keys()
    if args.verbose: print 'runningJobs: ',keys
    for counter in keys:
        child = running_jobs[counter]
        if is_finished(child):
            if args.verbose: print 'run finished!'
            if args.verbose:
                retString =''
                for i in counter: retString += '%s '%i
                print retString
            if succeded(child,counter):
                reader.succeded(counter[1])
                reader.add_corrected_runs()
            else:
                reader.failed(counter[1])
                if args.verbose: print 'del counter'
            del running_jobs[counter]
    return running_jobs

def print_status():
    letters = ['|','/','-','\\']
    now = int(time.time()*2)
    letter = letters[now%len(letters)]
    out = '\r%s running jobs: %s %s\t'%(time.strftime("%a, %d %b %Y %H:%M:%S"),[reader.get_run_number_of_count(i[1]) for i in runningJobs],letter)
    sys.stdout.write(out)
    sys.stdout.flush()

#     print '\n\n******\nLeft Jobs:          %3d,\nRunning Jobs:       %3d,\nUser input needed:  %3d,\nTotal Obs:          %3d'%(reader.get_left_runs(),len(runningJobs),reader.get_runs_with_user_input_needed(),len(reader.rows))
    pass

def get_new_logfile_name(runnumber,runDes):
    i = 0
    count = reader.get_count(reader.counter)
    #filename = get_new_logfile_name(runnumber)
    while True:
        dirname = '%s/%s-%s/'%(stdOutDir, runnumber,runDes)
        ensure_dir(dirname)
        dirname = os.path.expanduser(dirname)
        filename = '%s/std-%d-%s-%d_%d.out'%(dirname,runnumber,runDes,count,i)
        #print 'check ', filename
        if not os.path.exists(filename):
            break
        i += 1
    return filename

def get_job_no():
    jobNo = reader.runningCounter%nMaxJobs
    jobNos = [i[0] for i in runningJobs]
    for i in range(0,nMaxJobs):
        if not i in jobNos:
            return i
    return nMaxJobs

def start_job(rowNo,run):
#     print_status()
#     print "start_job",rowNo
    row = reader.started_run()
    count = reader.get_count(reader.counter)
    jobNo = get_job_no()
    if args.verbose: print row,reader.counter,'JobNo: %s'%jobNo
#     jobNo =  
    directory='%s/ana%d/'%(mainDir,jobNo)
    if args.verbose: print row,jobNo
    create_RunList(row,directory)
    sleepTime =  randrange(5,10)
    print time.strftime("%a, %d %b %Y %H:%M:%S"),'start_job', count,reader.counter,row
    
    if not args.testing:
        command = 'cd %s;'%directory
        command += ' %s -s %s -i %s -o %s'%(rd42Analysis,settingsDir,inputDir,outputDir)
        #print command
    else:
        command  = 'echo TEST; sleep %s'%sleepTime
        if randrange(0,2):
            command += '; echo "DONE_ALL %s"'%reader.counter
        else:
            command += '; echo "FAILED %s"'%reader.counter
        #print command
    if args.verbose: print 'start subprocess "%s"'%reader.counter
    runnumber = reader.get_run_number(reader.counter)
    if args.verbose: print runnumber
    #print 'get logfile name'
    filename = get_new_logfile_name(runnumber,run.runDes)
    #print 'open %s'%filename
    logfile = open(filename,'wb')
    child =  subprocess.Popen(command, shell = True,universal_newlines=True, stderr=subprocess.STDOUT, stdout=logfile)
    childs.append(child)
    runningJobs[(jobNo,rowNo)] = child
    logfiles[rowNo] = logfile
    #print 'started job'
    


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

reader.verbose = args.verbose
try:
    while True:
        if not reader.get_left_runs():
            break
        if len(runningJobs) < nMaxJobs:
            if args.verbose: print 'get next run',len(runningJobs),nMaxJobs
#             
            runningRuns = [reader.get_run_number_of_count(i[1]) for i in runningJobs]
            if args.verbose:print 'get run',runningRuns
            run = reader.get_next_run(runningRuns)
            if args.verbose: print run.get_key()
            if run == None:
                pass
                time.sleep (.5)
            else:
                if args.verbose: print 'get row no'
                rowNo = reader.get_row_number()
                print rowNo,run
                if not runningJobs.has_key(rowNo):
                    start_job(rowNo,run)
                    if args.verbose: print' job started'
                    if args.verbose: print '\n'
                else:
                    pass
                if args.verbose: print 'there is already a running job for row %s'%rowNo
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
    #print 'test'
    wait_for_jobs_finish()
except Exception,e:
    print Exception,e
    pass


reader.write_csv_RunList(filename)


exit()
