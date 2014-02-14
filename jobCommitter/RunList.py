import time
import math
import os
from _pyio import open

class RunList:
    nMaxTries = 4
    def __init__(self,**kwargs):
        self.use = False
        self.runNo = -1
        self.verb = 0
        self.runDes = '0'
        self.nEvents = 0
        self.nStart = 0
        self.doPed = True
        self.doClus = True
        self.doSel = True
        self.doAlign = True
        self.doAnaAlign = True
        self.doTransAna = True
        self.nTries = 0
        self.status = 0
        self.correction = False
        self.isInvalid = False
        self.rowNo = -1
        self.row = None
        if kwargs.has_key('row') and kwargs.has_key('rowNo'):
            row = kwargs['row']
            self.read_from_row(row,kwargs['rowNo'])
        if kwargs.has_key('data') and kwargs.has_key('rowNo'):
            row = kwargs['data']
            self.read_from_row(row,kwargs['rowNo'])
                                 
    def read_from_row(self,row,rowNo):
        self.row = row
        verbose = False
        for i in row:
            if '15005' in i: 
                verbose = True
        if verbose: 
            print row
        if len(row)<11:
            self.isInvalid = True
            return 
        self.rowNo = rowNo
        if row[0].startswith('#'):
            self.use = False
        elif row[0] =='':
            self.use = True
        else:
            try:
                self.use = bool(int(row[0]))
            except:
                pass
        if verbose: print self.use
        try:
            self.runNo = int(row[1])
            self.runDes = row[2]
            self.verb = int(row[3])
            self.nEvents = int(row[4])
            self.nStart = int(row[5])
            self.doPed = bool(int(row[6]))
            self.doClus = bool(int(row[7]))
            self.doSel = bool(int(row[8]))
            self.doAlign = bool(int(row[9]))
            self.doAnaAlign = bool(int(row[10]))
            self.doTransAna = bool(int(row[11]))
            if len(row) >= 12:
                self.nTries = int(row[12])
            if len(row) >= 13:
                self.status = int(row[13])
            if len(row) >= 14:
                self.correction = bool(int(row[14]))
        except:
            self.isInvalid = True
            pass
        
        if verbose: 
            print self.runNo,self.isInvalid,self.is_valid()
        pass
    
    def __str__(self):
        return '%s-%s'%(self.runNo,self.runDes)

    def get_key(self):
        key = (self.runNo,self.runDes)
        return key
    
    def has_settings(self,settingsDir):
        settingsFileName = self.get_settings_file_name(self.settingsDir)
        retVal =  os.path.exists(settingsFileName)
        return retVal
            
    def get_csv_output(self):
        if self.isInvalid:
            return self.row
        retVal = [int(self.use),self.runNo,self.runDes,self.verb,self.nEvents,self.nStart,int(self.doPed),int(self.doClus),int(self.doSel),int(self.doAlign),int(self.doAnaAlign),int(self.doTransAna),self.nTries,self.status,int(self.correction)]
        if self.use_Run():
            retVal[0] = ''
        else:
            retVal[0] ='#'
        return ['%s'%i for i in retVal]

    def is_valid(self):
        if self.isInvalid:
            return False
        if self.runNo < 0:
            return False
        if self.rowNo < 0:
            return False
        return True
    
    def use_Run(self):
        return self.use
    
    def do_correction(self):
        return self.correction
    
    def get_tries(self):
        return self.nTries
    
    def is_finished(self):
        return self.status >= 4
    
    def do_corrections(self):
        return self.correction and self.status >= 2
    
    def needs_user_input(self):
        return self.status%2 ==1
    
    def check_run(self):
#         print 'check run %s'%self.runNo
        if not self.is_valid():
            return False
        if not self.use_Run():
            return False
        if self.get_tries() > self.nMaxTries:
            return  False
        if self.is_finished():
            return False
        if self.needs_user_input():
            return False
        return True
    
    def first_try(self):
#         if self.status == 0:
#             return True
        return False
    
    def get_crosstalk_correction_file_name(self,outputDir):
        fileName = outputDir+ '/%s/crossTalkCorrectionFactors.%d'%(self.runNo,self.runNo)
        if self.runDes !='' and self.runDes != '0':
            fileName += '-%s'%self.runDes
        fileName += '.txt'
        return fileName
    
    def has_valid_crosstalk_corrections(self,outputDir):
        src = self.get_crosstalk_correction_file_name(outputDir)
        return os.path.exists(src)
        
    def get_settings_file_name(self,settingsDir):
        runNo = self.get_run_number()
        src = '%s/settings.%s'%(settingsDir,runNo)
        if self.runDes != '' and self.runDes !='0':
            src += '-%s'%self.runDes
        src += '.ini'
        src = self.clean_file_name(src)
        return src

    def clean_file_name(self,src):
        src = os.path.expanduser(src)
        while src.find('//')!=-1:
            src = src.replace('//','/')
        return src
            
    def get_crosstalk_corrections(self,outputDir):
        fileName = self.get_crosstalk_correction_file_name(outputDir)
        f = open(fileName)
        lines = [line.encode('ascii','replace').replace(':','').replace('%','').split() for line in f.readlines()]
        corrections = [line[1] for line in lines]
#         percentages = [cor.endswith('%')*.01 for cor in corrections]
#         factor  = [cor.strip('%') for cor in corrections]
        corrections = [float(cor) for cor in corrections]
        diamondCor = corrections[-1]
        siliconCor = corrections[:-1]
#         print diamondCor
#         print siliconCor
        meanSil = sum(siliconCor)/len(siliconCor)
        sigmaSil = math.sqrt(sum([x**2 for x in siliconCor])/len(siliconCor) - meanSil**2)
#         print meanSil,sigmaSil
#         print corrections
#         print lines
        f.close()     
        return meanSil,diamondCor
     
    def run(self):
        self.nTries+=1
        #print '%3d: left tries %s'%(self.runNo,self.nMaxTries-self.nTries)
        retVal = [self.runNo,self.runDes,self.verb,self.nEvents,self.nStart,int(self.doPed),int(self.doClus),int(self.doSel),int(self.doAlign),int(self.doAnaAlign),int(self.doTransAna)]
        if self.first_try():
            retVal[7] = 0 # doSel
            retVal[8] = 0 # deAlign
            retVal[9] = 0 # doAnaAlign
            retVal[10] = 0 #doTransAna
        return retVal
            
    def succeded(self):
        self.status+=1
        
    def get_corrected_run_number(self):
        if 'left' in self.runDes.lower():
            i = 1
        elif 'right' in self.runDes.lower():
            i = 2
        else:
            i = 0 
        return self.runNo*10+i
    
    def get_run_number(self):
        return self.runNo
