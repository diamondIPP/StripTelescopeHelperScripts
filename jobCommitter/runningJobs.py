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
    def __init__(self):
        child = None
        position = -1
        logfile = None
        logfilename = None
    
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

    def start_job(self,command,logfilename):
#    print 'start subprocess "%s"'%reader.counter
#     print 'open %s'%filename
        self.logfilename = logfilename
        self.logfile = open(self.logfilename,'wb')
        self.child =  subprocess.Popen(command, shell = True,universal_newlines=True, stderr=subprocess.STDOUT, stdout=logfile)
    #     childs.append(child)
        runningJobs[rowNo] = child
        logfiles[rowNo] = logfile
