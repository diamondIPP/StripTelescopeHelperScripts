import utilities
import os
import ConfigParser
import resultsCreation
import json

class ResultReader:
    def __init__(self,config,map):
        self.verbosity = 1
        self.main_config = config
        self.map = map

    def GetResults(self):
        # get list of files wich starts with 'results'
        inputDir = self.main_config.get('Results', 'inputDir')
        file_list = utilities.list_files(inputDir, 'results')
        if self.verbosity:
            print ' *  staring list', file_list
        file_list = [i for i in file_list if i.endswith('.res') and '_new' in i]
        # print 'updated file list ', self.file_list
        print ' * get result config'
        results = self.read_result_config(file_list)
        return results

    def read_result_config(self,file_list):
        results = {}
        print file_list
        for i in file_list:
            runno = i.rsplit('_', 1)[1].split('.')[0]
            result_config = ConfigParser.ConfigParser()
            if True:
                print 'reading ', i
            result_config.read(i)
            #print result_config.sections()
            if not result_config.has_section('RunInfo'):
                print 'section "RunInfo" does not exist....'
                continue
            result_config.set('RunInfo', 'realRunNo', runno)
            #result_config.set('RunInfo', 'runno', runno)
            if self.verbosity:
                for section_name in result_config.sections():
                    # print 'Section:', section_name
                    # print '  Options:', result_config.options(section_name)
                    for name, value in result_config.items(section_name):
                        print '  %s = %s' % (name, value)
                        pass
                    # print
                    pass
            path = os.path.abspath(i)
            if not result_config.has_section('additional'):
                result_config.add_section('additional')
                pass

            result_config.set('additional', 'resultsPath', path)
            key = utilities.get_result_key(self.main_config,result_config)
            result_config.set('additional', 'key', key)
            result_config = self.add_missing_items(result_config)
            if self.verbosity:
                print 'key', key, result_config.get('RunInfo', 'runno'), result_config.get('RunInfo', 'realRunNo')
            results[key] = result_config

            with open(path, 'w') as configfile:
                result_config.write(configfile)
        return results

    def add_missing_items(self,config):
        isCorrected = resultsCreation.is_corrected(config)
        runno = config.getint('RunInfo', 'runno')
        config.set('RunInfo', 'realRunNo', '%d' % runno)
        config.set('RunInfo', 'cor', '%s' % isCorrected)
        newRunNo = runno
        if isCorrected:
            newRunNo = int(newRunNo / 10)

        if newRunNo in self.map:
            try:
                config.set('RunInfo', 'repeatercardno', '%s' % self.map[newRunNo]['repeaterCard'])
                config.set('RunInfo', 'voltage', '%+4d' % self.map[newRunNo]['biasVoltage'])
                config.set('RunInfo', 'currentbegin', '%s' % (self.map[newRunNo]['currentBegin']))
                config.set('RunInfo', 'currentend', '%s' % (self.map[newRunNo]['currentEnd']))
            except Exception as e:
                print 'repeatercardno',self.map[newRunNo]['repeaterCard']
                print 'voltage',self.map[newRunNo]['biasVoltage']
                print 'current',self.map[newRunNo]['currentBegin'],self.map[newRunNo]['currentEnd']
                print self.map[newRunNo]
                raise e
            if not config.has_option('RunInfo','events'):
                try:
                    config.set('RunInfo', 'events', '%s' % (self.map[newRunNo]['events']))
                except:
                    print 'cannot find events in map'
                    print self.map[newRunNo].keys()
                    pass
        else:
            print 'cannot find %s' % newRunNo
        config.set('RunInfo', 'runno', '%d' % newRunNo)
        if config.has_option('TimeDependence', 'landauclusterfitoffsetsize10'):
            if config.has_option('TimeDependence', 'landauclusterfitslopesize10'):
                offset = config.getfloat('TimeDependence', 'landauclusterfitoffsetsize10')
                slope = config.getfloat('TimeDependence', 'landauclusterfitslopesize10')
                try:
                    config.set('TimeDependence', 'LinFitRelChange', '%s' % (slope / offset * 100.))
                except:
                    config.set('TimeDependence', 'LinFitRelChange', '%s' % slope)

        m2 = float(config.get('Landau_normal', 'm2/2_normal', 0))
        m4 = float(config.get('Landau_normal', 'm4/4_normal', -1))
        convergence = m2 / m4 * 100.
        config.set('Landau_normal', 'convergence', '%6.2f' % convergence)
        runDesc = config.get('RunInfo', 'descr.')
        dia = utilities.getDiamond(self.map,newRunNo, runDesc)
        config.set('RunInfo', 'dia', dia)
        if '?' in config.get('RunInfo', 'dia'):
            config.set('RunInfo', 'dia', 'unknown')
        return config

# @staticmethod

