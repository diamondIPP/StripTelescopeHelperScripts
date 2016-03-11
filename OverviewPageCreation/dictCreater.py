import ConfigParser
import csv

import utilities
import read_beamtest_runlogs

class dictCreater:
    def __init__(self, configdir):
        self.verbosity = False
        self.configdir = configdir
        self.configFileName = configdir + '/creation.ini'
        print '    - read', self.configFileName
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.configFileName)
        for i in self.config.sections():
            # if self.verbosity:
            print '        - ',i, self.config.options(i)
        contentDesc = self.config.get('RepeaterCards', 'content')
        self.contentDescRepCard = [i.split('/') for i in contentDesc.strip('[]').split(',')]
        contentDesc = self.config.get('RunInfo', 'content')
        self.contentDescRunInfo = [i.split('/') for i in contentDesc.strip('[]').split(',')]
        contentDesc = self.config.get('RunList', 'content')
        self.contentDescRunList = [i.split('/') for i in contentDesc.strip('[]').split(',')]

        r = read_beamtest_runlogs.runLogReader(configdir)
        self.all_runlogs = r.update_runlogs()
        print 'all_runlogs',len(self.all_runlogs)



    def add_default(self, item, contentDesc):
        for i in contentDesc:
            item[i[0]] = utilities.get_value(i[2], i[1], i[2])
            pass
        return item

    @property
    def getRunInfo(self):
        logfiles = self.config.get('RunInfo', 'fileName')
        logfiles = self.configdir + '/' + logfiles
        contentDesc = self.contentDescRunInfo
        key = self.config.get('RunInfo', 'key')
        runInfo = {}
        f = open(logfiles)
        for line in f.readlines():
            if line != '':
                line = line.split()
                content = line
                thisInfo = {}
                unknown = 0
                for i in range(len(content)):
                    if i <= len(contentDesc):
                        if len(contentDesc[i]) > 2:
                            thisInfo[contentDesc[i][0]] = utilities.get_value(content[i], contentDesc[i][1],
                                                                              contentDesc[i][2])
                        else:
                            thisInfo[contentDesc[i][0]] = utilities.get_value(content[i], contentDesc[i][1])
                    else:
                        thisInfo['unknown%s' % unknown] = content[i]
                        unkown += 1
                if self.verbosity: print thisInfo
                if thisInfo.has_key(key):
                    runInfo[thisInfo[key]] = thisInfo
        return runInfo

    def get_ignored_testbeams(self):
        fileName = self.config.get('IgnoredTestBeams', 'fileName')
        fileName = self.configdir + '/' + fileName
        runs = []
        with open(fileName, 'rb') as listfile:
            for line in listfile.readlines():
                try:
                    testbeam = int(line)
                except:
                    continue
                runs.append(testbeam)
        return runs

    def get_ignored_runs(self):
        fileName = self.config.get('IgnoredRuns', 'fileName')
        fileName = self.configdir + '/' + fileName
        runs = []
        with open(fileName, 'rb') as listfile:
            for line in listfile.readlines():
                try:
                    runno = int(line)
                except:
                    continue
                runs.append(runno)
        return runs


    def get_runlist_map(self):
        fileName = self.config.get('RunList', 'fileName')
        fileName = self.configdir + '/' + fileName
        runList = {}
        contentDesc = self.contentDescRunList
        key = self.config.get('RunList', 'key')
        out = '    - Reading RunListMap with the following keys '+str(key)+' and '+str(contentDesc)
        # raw_input(out)
        with open(fileName, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            l = 0
            for row in reader:
                thisRun = {}
                for i in range(len(row)):
                    if len(contentDesc[i]) > 2:
                        thisRun[contentDesc[i][0]] = utilities.get_value(row[i], contentDesc[i][1], contentDesc[i][2])
                    else:
                        print '    - ',row[i], type(row[i])
                        thisRun[contentDesc[i][0]] = utilities.get_value(row[i], contentDesc[i][1])

                if thisRun.has_key(key):
                    runList[thisRun[key]] = thisRun
                else:
                    print 'cannot find key, ', key, 'in thisRun', thisRun
                if l == 0:
                    print '    - ',thisRun
                    # raw_input('Row %s'%row)
                    l+=1
        return runList


    def get_repeaterCard_map(self):
        fileName = self.config.get('RepeaterCards', 'fileName')
        fileName = self.configdir + '/' + fileName
        contentDesc = self.contentDescRepCard
        if self.verbosity: print contentDesc
        key = self.config.get('RepeaterCards', 'key')

        repeaterCard_and_current_File = open(fileName)
        repeaterCardMap = {}
        i = 0
        for line in repeaterCard_and_current_File.readlines():
            i += 1
            if line.startswith('#'):
                continue
            line = line.replace('\n', '').replace('\r', '')
            content = line.split(',')
            thisRepeaterCard = {}
            if i == 1:
                continue
            unknown = 0
            for i in range(len(content)):
                if i <= len(contentDesc):
                    if len(contentDesc[i]) > 2:
                        thisRepeaterCard[contentDesc[i][0]] = utilities.get_value(content[i], contentDesc[i][1],
                                                                                  contentDesc[i][2])
                    else:
                        thisRepeaterCard[contentDesc[i][0]] = utilities.get_value(content[i], contentDesc[i][1])
                else:
                    thisRepeaterCard['unknown%s' % unknown] = content[i]
                    unkown += 1
            if self.verbosity: print thisRepeaterCard
            if thisRepeaterCard.has_key(key):
                repeaterCardMap[thisRepeaterCard[key]] = thisRepeaterCard
        return repeaterCardMap

    def get_irradiation_map(self):
        fileName = self.config.get('Irradiations', 'fileName')
        return utilities.get_dict_from_file(fileName)

    def get_combined_list(self):
        repeaterCards = self.get_repeaterCard_map()
        runInfos = self.getRunInfo
        runList = self.get_runlist_map()
        combinedList = {}
        missingRepeaterCards = []
        missingRunInfo = []
        missingKeys = []
        for key in set().union(repeaterCards.keys(), runInfos.keys(), runList.keys()):
            item = {}
            if repeaterCards.has_key(key) and runInfos.has_key(key) and runList.has_key(key):
                item = dict(repeaterCards[key].items() + runInfos[key].items() + runList[key].items())
            else:
                missingKeys.append(key)
                # print '    - no key %s in runList' % key
                if repeaterCards.has_key(key) and runInfos.has_key(key):
                    item = dict(repeaterCards[key].items() + runInfos[key].items())
                elif repeaterCards.has_key(key):
                    item = dict(repeaterCards[key].items())
                    item = self.add_default(item, self.contentDescRunInfo)
                    missingRunInfo.append(key)
                    if self.verbosity: print 'no key %s in runInfo' % key
                    if self.verbosity: print item
                elif runInfos.has_key(key):
                    item = dict(runInfos[key])
                    item = self.add_default(item, self.contentDescRepCard)
                    missingRepeaterCards.append(key)
                    if self.verbosity: print 'no key %s in repeaterCards' % key
                    if self.verbosity: print item
                else:
                    continue
            combinedList[key] = item
        if len(missingKeys):
            print 'There are %s missing keys: \n\t%s'%(len(missingKeys),sorted(missingKeys))
        if len(missingRepeaterCards):
            print 'There are %s runs with missing repeatercard information: \n\t %s' % (
            len(missingRepeaterCards), sorted(missingRepeaterCards))

        if len(missingRunInfo):
            print 'There are %s runs with missing missing RunInfo: \n\t %s' % (
            len(missingRunInfo), sorted(missingRunInfo))
        return combinedList


if __name__ == "__main__":
    r = dictCreater('config/')
    r.get_runlist_map()
    r.get_irradiation_map()
    r.get_repeaterCard_map()
    r.get_ignored_runs()
    map = r.get_combined_list()
    print map
