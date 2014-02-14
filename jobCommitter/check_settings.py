import time
import subprocess
import os
import RunListReader
from random import randrange
from pickle import NONE

runningJobs = {}

logfiles = {}
mainDir  ='/scratch/analysis/'
nMaxJobs = 2

filename ='RunList-new.csv'
reader  = RunListReader.RunListReader()
rd42Analysis = '~/sdvlp/rd42/branches/3dAnalysis/diamondAnalysis'
settingsDir = '~/sdvlp/rd42/trunk/run_settings/'
inputDir = '/scratch/testbeamdata'
outputDir = '/scratch/analysis/output/new'
reader.outputDir = outputDir
reader.settingsDir = settingsDir
reader.correctionMacro = '~/sdvlp/rd42/trunk/createAsymmetricEtaSample.C'
reader.read_csv_RunList(filename)
leftJobs = 0

def ensure_dir(f):
    d = os.path.dirname(f)
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
    print output
    ofile.write(output)
    ofile.close()


def start_run(row,counter):
    print 'start_run',counter
    count = counter
    directory='%s/ana%d/'%(mainDir,reader.runningCounter%nMaxJobs)
    print directory
    create_RunList(row,directory)
    sleepTime =  randrange(0, 3)
    print 'start', count,counter,row
    
    if True:
        command = 'cd %s;'%directory
        command += ' %s -s %s -i %s -o %s'%(rd42Analysis,settingsDir,inputDir,outputDir)
        print command
    else:
        command  = 'echo TEST; sleep %s'%sleepTime
        if randrange(0,2):
            command += '; echo "DONE_ALL %s"'%counter
        else:
            command += '; echo "FAILED %s"'%counter
        print command
#     print 'start subprocess "%s"'%counter
    runnumber = reader.get_run_number(counter)
    i = 0
    while True:
        filename = 'std-%d-%d_%d.out'%(runnumber,count,i)
        if not os.path.exists(filename):
            break
        i += 1
    print 'open %s'%filename
    logfile = open(filename,'wb')
    child =  subprocess.Popen(command, shell = True,universal_newlines=True, stderr=subprocess.STDOUT, stdout=logfile)
#     childs.append(child)

    return child,logfile

def flush_logfiles():
    if logfiles == None:
        print 'logfiles is of type NONE'
        return
    for i in logfiles:
        logfiles[i].flush()

def is_finished(child):
    return child.poll()!=None

def succeded(child,counter):
    print 'succeded',counter
    err =None
    out =None
    if child == None:
        out, err = child.communicate()
    runnumber = reader.get_run_number(counter)
    i = 0
    #ofile.close()
    count = reader.get_count(counter)
    name = None
    if logfiles != None:
        if logfiles.has_key(count):
            logfiles[count].close()
            name = logfiles[count].name
#             print 'del logfile %s %s'%(count,name)
            del logfiles[count]
    filename = 'std-%d-%d_%d.out'%(runnumber,counter,i)
    filename = filename.replace('.out', '.err')
    if err != None:
        ofile = open(filename,'wb')
        ofile.write(err)
        ofile.close()

    if name == None:
        print 'cannot read from child'
        return False
    else:
        logfile = open(name,'rb')
        for line in logfile.readlines():
            if 'DONE_ALL' in line:
                print 'suceeded with child'
                logfile.close()
                return True
        print 'problem with child'
        logfile.close()
    return False

def check_running_jobs(running_jobs):
    if running_jobs == None:
        print 'running jobs == None'
        return
    keys = running_jobs.keys()
    for counter in keys:
        child = running_jobs[counter]
        if is_finished(child):
#             print 'run finished! %s'%counter
            if succeded(child,counter):
                reader.succeded(counter)
                reader.add_corrected_runs()
            print 'del counter'
            del running_jobs[counter]
    return running_jobs

def print_status():
    print '\n\n******\nLeft Jobs:          %3d,\nRunning Jobs:       %3d,\nUser input needed:  %3d,\nTotal Obs:          %3d'%(reader.get_left_runs(),len(runningJobs),reader.get_runs_with_user_input_needed(),len(reader.rows))

def start_job(rowNo):
#     print_status()
    print "start_job",rowNo
    row = reader.started_run()
#     print row
    child,logfile = start_run(row,reader.counter)
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
            print 'left jobs' %leftJobs
        time.sleep(.1)
    print ' last run finished'


rownum = 0
nColumns = 0
entryNo = []
lastCheck = time.time()

try:
    missingSettings =[]
    for runNo in reader.runList:
        run = reader.runList[runNo]
        if not reader.has_settings(run):
            missingSettings.append(run)
    print '\n Missing Settings files: '
    for i in missingSettings:
        print '\t',i.get_settings_file_name('.')
except Exception,e:
    print Exception,e
    pass


# reader.write_csv_RunList(filename)


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
