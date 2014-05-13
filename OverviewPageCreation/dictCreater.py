import utilities
import ConfigParser



class dictCreater:
    def __init__(self,configDir):
        self.verbosity = 0
    	self.configDir = configDir
        self.configFileName = configDir+'/creation.ini'
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.configFileName)
        for i in self.config.sections():
            if self.verbosity: print i, self.config.options(i)
        contentDesc = self.config.get('RepeaterCards','content')
        self.contentDescRepCard = [i.split('/') for i in contentDesc.strip('[]').split(',')]
        contentDesc = self.config.get('RunInfo','content')
        self.contentDescRunInfo = [i.split('/') for i in contentDesc.strip('[]').split(',')]
        
    def add_default(self,item,contentDesc):
        for i in contentDesc:
            item[i[0]] = utilities.get_value(i[2],i[1],i[2])
            pass
        return item
        
    def getRunInfo(self):
        logfiles = self.config.get('RunInfo','fileName')
        logfiles = self.configDir+'/'+logfiles
        contentDesc = self.contentDescRunInfo
        key = self.config.get('RunInfo','key')
        runInfo = {}
        f = open(logfiles)
        for line in f.readlines():
            if line!='':
                line = line.split()
                content = line
                thisInfo = {}
                unknown=0
                for i in range(len(content)):
                    if i <= len(contentDesc):
                        if len(contentDesc[i])>2:
                            thisInfo[contentDesc[i][0]] = utilities.get_value(content[i],contentDesc[i][1],contentDesc[i][2])
                        else:
                            thisInfo[contentDesc[i][0]] = utilities.get_value(content[i],contentDesc[i][1])
                    else:
                        thisInfo['unknown%s'%unknown] = content[i]
                        unkown+=1
                if self.verbosity: print thisInfo
                if thisInfo.has_key(key):
                    runInfo[thisInfo[key]] = thisInfo
        return runInfo

    def get_repeaterCard_map(self):
        fileName =  self.config.get('RepeaterCards','fileName')
        fileName = self.configDir+'/'+fileName
        contentDesc = self.contentDescRepCard
        if self.verbosity: print contentDesc
        key = self.config.get('RepeaterCards','key')
        
        repeaterCard_and_current_File = open(fileName)
        repeaterCardMap = {}
        i = 0
        for line in repeaterCard_and_current_File.readlines():
            i+=1
            if line.startswith('#'):
                continue
            line = line.replace('\n','').replace('\r','')
            content = line.split(',')
            thisRepeaterCard = {}
            if i == 1:
                continue
            unknown=0
            for i in range(len(content)):
                if i <= len(contentDesc):
                    if len(contentDesc[i])>2:
                        thisRepeaterCard[contentDesc[i][0]] = utilities.get_value(content[i],contentDesc[i][1],contentDesc[i][2])
                    else:
                        thisRepeaterCard[contentDesc[i][0]] = utilities.get_value(content[i],contentDesc[i][1])
                else:
                    thisRepeaterCard['unknown%s'%unknown] = content[i]
                    unkown+=1
            if self.verbosity: print thisRepeaterCard
            if thisRepeaterCard.has_key(key):
                repeaterCardMap[thisRepeaterCard[key]] = thisRepeaterCard
        return repeaterCardMap

    def get_irradiation_map(self):
        fileName =  self.config.get('Irradiations','fileName')
        return utilities.get_dict_from_file(fileName)

    def get_combined_list(self):
        repeaterCards = self.get_repeaterCard_map()
        runInfos = self.getRunInfo()
        combinedList = {}
        missingRepeaterCards =[]
        missingRunInfo = []
        for key in set().union(repeaterCards.keys(),runInfos.keys()):
            item = {}
            if repeaterCards.has_key(key) and runInfos.has_key(key):
                item = dict(repeaterCards[key].items() + runInfos[key].items())
            elif repeaterCards.has_key(key):
                item = dict(repeaterCards[key].items())
                item = self.add_default(item,self.contentDescRunInfo)
                missingRunInfo.append(key)
                if self.verbosity: print 'no key %s in runInfo'%key
                if self.verbosity: print item
            else:
                item = dict(runInfos[key])
                item = self.add_default(item,self.contentDescRepCard)
                missingRepeaterCards.append(key)
                if self.verbosity: print 'no key %s in repeaterCards'%key
                if self.verbosity: print item
            combinedList[key]=item
        if len(missingRepeaterCards):
            print 'There are %s runs with missing repeatercard information: \n\t %s'%(len(missingRepeaterCards),sorted(missingRepeaterCards))
            
        if len(missingRunInfo):
            print 'There are %s runs with missing missing RunInfo: \n\t %s'%(len(missingRunInfo),sorted(missingRunInfo))
        return combinedList

if __name__ == "__main__":
    r = dictCreater('creation.ini')
    r.get_irradiation_map()
    r.get_repeaterCard_map()
    map = r.get_combined_list()
    print map
