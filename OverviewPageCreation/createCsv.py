# import ConfigParser
import csv
import pickle

import dictCreater


class CsvCreater:
    def __init__(self, *argv):
        self.results = []
        self.keys = []
        self.read_pickle()
        self.runList = self.read_run_list_map('config/runlist.csv')
        self.add_log()
        self.find_runs()
        self.get_missing_runs()
        self.all_keys = self.create_list_of_all_keys()
        self.run_parameters = []
        if argv is not None:
            for arg in argv:
                self.run_parameters.append(arg)
        pass

    def read_pickle(self):
        print 'get result data from pickle file'
        self.results = pickle.load(open('data.pkl', 'rb'))
        self.update_results_keys()

    def update_results_keys(self):
        for key in self.results:
            new_key = self.results[key].get('RunInfo', 'runno') + '-' + self.results[key].get('RunInfo', 'descr.')
            new_key += '-' + self.results[key].get('RunInfo', 'corrected')
            if new_key == key:
                continue
            self.results[new_key] = self.results.pop(key)

    def read_run_list_map(self, filename):
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            run_list = {}
            for row in reader:
                runno = int(row[0])
                events = int(row[1])
                if runno / 10000 > 0:
                    if not runno in run_list:
                        run_list[runno] = {}
                    run_list[runno]['events'] = events
                    run_list[runno]['keys'] = []
        return run_list

    def find_runs(self):
        for key in self.results:
            runno = self.results[key].getint('RunInfo', 'runno')
            if not runno in self.runList:
                print 'cannot find runnno', runno
                continue
            if not 'keys' in self.runList[runno]:
                self.runList[runno]['keys'] = []
            self.runList[runno]['keys'].append(key)
            # print self.runList[runno]
        pass

    def add_log(self):
        print 'add log'
        r = dictCreater.dictCreater('config/')
        self.ignored_runs = r.get_ignored_runs()
        self.ignored_testbeams = r.get_ignored_testbeams()
        listed = r.get_combined_list()
        for key in listed:
            if key in self.runList:
                self.runList[key].update(listed[key])
                print '\n', key, self.runList[key]
                if self.runList[key]['keys']:
                    self.runList[key]['keys'] = []
            else:
                print 'no key ', key

    def get_missing_keys_of_run(self, runno):
        nkeys = len(self.runList[runno]['keys'])
        diamonds = self.runList[runno].get('diamond', ['unknown'])
        missing_keys = []

        print runno, diamonds, self.runList[runno]['keys']
        if len(diamonds) == 2:
            descr = ['left', 'right']
        else:
            descr = ['0']
        for des in descr:
            for corrected in range(0, 2):
                key = '%s-%s-%s' % (runno, des, corrected)
                if not key in self.runList[runno]['keys']:
                    missing_keys.append(key)
        return missing_keys

    def get_missing_runs(self):
        missing_runs = []
        missing_parts = []
        missing_keys = []
        for runno in self.runList:
            if not self.is_valid_run(runno):
                continue
            try:
                nkeys = len(self.runList[runno]['keys'])
            except:
                nkeys = 0
            if not nkeys:
                diamonds = self.runList[runno].get('diamond', ['unknown'])
                missing_runs.append((runno, len(diamonds)))
                self.runList[runno]['keys'] = []
                if diamonds == 2:
                    key = '%s-0-left' % runno
                    self.runList[runno]['keys'].append(key)
                    self.keys.append(key)
                    key = '%s-0-right' % runn   o
                    self.runList[runno]['keys'].append(key)
                    self.keys.append(key)
                else:
                    key = '%s-0-0' % runno
                    self.runList[runno]['keys'].append(key)
                    self.keys.append(key)
            missing_keys.append(self.get_missing_keys_of_run(runno))
            if nkeys % 2 == 1:
                missing_parts.append((runno, nkeys, self.runList[runno]['keys']))
        print '\n', len(missing_runs), 'missing Runs are', missing_runs
        print len(missing_parts), 'partially missing Parts are', missing_parts

    def create_list_of_all_keys(self):
        keys = []
        for result in self.results:
            keys.append(result)
        for run in self.runList:
            for key in self.runList.get('keys', []):
                keys.append(key)
        keys = sorted(keys)
        return keys


    def write_run_list(self, outputfile, outputList):
        with open(outputfile, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(outputList)

    def has_to_rerun(self, key):
        svnrev = self.results[key].get('RunInfo', 'svn_rev')
        svnrev = int(svnrev.strip('M'))
        if self.results[key].get('RunInfo', 'svn_rev').endswith('M'):
            svnrev += .5
        if svnrev < 1141:
            # print 'needs to be rerun: ', key, self.results[key].get('RunInfo', 'svn_rev')
            return True
        return False

    def is_valid_run(self, run):
        retVal = run in self.ignored_runs
        testBeam = run / 1000
        while testBeam / 100 > 0:
            testBeam /= 10
        retVal2 = testBeam in self.ignored_testbeams
        retVal = retVal or retVal2
        return not retVal

    def get_run_parameters(self, correction):
        output = []
        # NStart  Ped Clus    Sel DoAlig  AnaAli  TransAna
        n_start = 0
        pedestal = int('pedestal' in self.run_parameters)
        clustering = int('clustering' in self.run_parameters)
        selection = int('selection' in self.run_parameters)
        alignment = int('alignment' in self.run_parameters)
        ana_alignment = int('ana_alignment' in self.run_parameters)
        transparent_ana = int('transparent_ana' in self.run_parameters)
        status = 0
        n_tries = 0
        return [n_start, pedestal, clustering, selection, alignment, ana_alignment, transparent_ana, n_tries, status,
                int(correction)]

    def get_list_entry(self, key):
        keys = key.split('-')
        if key in self.results:
            realrun = self.results[key].getint('RunInfo', 'realrunno')
            run = self.results[key].getint('RunInfo', 'runno')
            descr = self.results[key].get('RunInfo', 'descr.')
            correction = realrun == run
        else:
            run = int(keys[0])
            realrun = run
            descr = int(keys[1])
            if descr:
                run = realrun / int(run)
                raw_input('run  %s - %s' % (run, realrun))
            correction = realrun == run
        if int(run) in self.runList:
            events = self.runList[run]['events']
        else:
            events = -1
            print run, descr
            raw_input('no information about no of events for %s' % key)
        if events == 0:
            raw_input('%s - no events %s' % (key, events))
        output = ['', realrun, descr, 0, events]
        output2 = self.get_run_parameters(correction)
        output.extend(output2)
        return output

    def get_n_diamonds(self, run):
        return 1

    def get_description(self, dia, nDias):
        if nDias == 2:
            if dia == 0:
                return 'left'
            else:
                return 'right'
        return '0'

    def get_runs_to_rerun(self):
        reruns = []
        runs = []
        for key in self.results:
            if self.has_to_rerun(key):
                reruns.append(key)
                runno = self.results[key].get('RunInfo', 'realrunno')
                if self.results[key].has_option('RunInfo', 'events'):
                    events = self.results[key].get('RunInfo', 'events')
                else:
                    no = self.results[key].getint('RunInfo', 'runno')
                    if no in self.runList:
                        events = self.runList.get(no).get('events', -1)
                    else:
                        events = -1
                descr = self.results[key].get('RunInfo', 'descr.')
                runs.append([runno, descr, events])
                if events <= 0:
                    print runs[-1], runno, descr
        return runs

    def not_existing_run(self, key):

        return not key in self.results

    def to_be_analyzed(self, key):
        if self.not_existing_run(key):
            print key, ' not existing'
            return True
        if self.has_to_rerun(key):
            print key, ' neet to rerun'
            return True

        return False

    @property
    def create_list(self):
        print self.all_keys
        #raw_input()
        runs = self.get_runs_to_rerun()
        print 'to be rerun: ', runs
        print 'create output list'
        outputList = []
        for run in sorted(self.runList.keys()):
            runno = run
            if runno / 10000 == 0:
                continue
            if not self.is_valid_run(runno):
                continue
            for key in self.runList[run].get('keys', []):
                if self.to_be_analyzed(key):
                    outputList.append(key)
        # nDias = self.get_n_diamonds(run)
        #     for dia in range(nDias):
        #         if self.is_valid_run(run):
        #             events = self.runList[run]
        #             descr = self.get_description(dia, nDias)
        print outputList
        print len(outputList)
        return outputList

    def save_list(self, output_list):
        output = []
        print 'save list'
        for item in output_list:
            # runno = self.results[item].get('RunInfo','realrunno')
            # run = self.results[item].get('RunInfo','runno')
            # descr = self.results[item].get('RunInfo','descr.')
            # events = self.runList[run]['events']
            entry = self.get_list_entry(item)
            print item, entry
            output.append(entry)
        outputfile = 'test.csv'
        self.write_run_list(outputfile, output)


if __name__ == "__main__":
    creator = CsvCreater('pedestal', 'clustering', 'selection')
    output_list = creator.create_list
    creator.save_list(output_list)
