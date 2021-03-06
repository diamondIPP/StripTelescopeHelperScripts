#!/usr/bin/env python
import time
import pickle
import csv
import re
import ConfigParser

import HTML


# import math
import utilities
import results_utilities
# from operator import itemgetter, attrgetter
import os
import dictCreater
import correctionFactor
import resultsCreation
from collections import *
import ResultReader
# import re


class HTMLGenerator:
    def __init__(self, config_dir):
        self.verbosity = 5
        if self.verbosity:
            print 'ResultReader - Initialisation'
        self.config_dir = config_dir
        self.config_file_name = config_dir + '/creation.ini'
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file_name)
        self.update_crosstalk_factors = True
        self.map = None
        self.results = None
        self.file_list = None
        self.csv_mapping = None
        self.headers = None
        self.header_mapping = None

    def create_tables(self):
        print 'Create Tables: '
        if self.update_crosstalk_factors:
            print ' * update correction factors'
            correctionFactor.update_crosstalk_factors(self.config.get('Results', 'inputDir'))

        print ' * read dictionaries'
        mapper = dictCreater.dictCreater(self.config_dir)
        self.map = mapper.get_combined_list()

        print ' * get file list'
        result_reader = ResultReader.ResultReader(self.config,self.map)
        self.results = result_reader.GetResults()
        #raw_input(self.results)
        self.set_csv_mapping()

    # def get_result_key(self, config):
    #     key = ''
    #     keyNames = self.config.get('Results', 'key').split(';')
    #     for i in keyNames:
    #         if i.startswith('<') and i.endswith('>'):
    #             i = i.strip('<>').strip()
    #             keyName = i.split(',')
    #             keyName = [i.strip() for i in keyName]
    #             # print 'check for : ',keyName
    #             # print config.sections()
    #             # if config.has_section(keyName[0]):
    #             # print config.options(keyName[0])
    #             if config.has_option(keyName[0], keyName[1]):
    #                 value = config.get(keyName[0], keyName[1])
    #                 key += value
    #             else:
    #                 print 'cannot finde key "%s"'%keyName[0],keyName[1]
    #                 if config.has_section(keyName[0]):
    #                     print 'options:',config.options(keyName[0])
    #                 else:
    #                     print 'sections',config.sections()
    #                 key += 'unnown'
    #         else:
    #             key += i
    #     #print'get result kediay', key
    #     #print key
    #     return key

    # def read_result_config(self):
    #     results = {}
    #     print self.file_list
    #     #raw_input()
    #     for i in self.file_list:
    #         runno = i.rsplit('_', 1)[1].split('.')[0]
    #         config = ConfigParser.ConfigParser()
    #         if self.verbosity or True:
    #             print 'reading ', runno,'i: ', i
    #         config.read(i)
    #         #print config.sections()
    #         if not config.has_section('RunInfo'):
    #             print 'section "RunInfo" does not exist....'
    #             continue
    #         config.set('RunInfo', 'realRunNo', runno)
    #         print config.get('RunInfo', 'realRunNo')
    #         #config.set('RunInfo', 'runno', runno)
    #         if self.verbosity:
    #             for section_name in config.sections():
    #                 # print 'Section:', section_name
    #                 # print '  Options:', config.options(section_name)
    #                 for name, value in config.items(section_name):
    #                     print '  %s = %s' % (name, value)
    #                     pass
    #                 # print
    #                 pass
    #         path = os.path.abspath(i)
    #         if not config.has_section('additional'):
    #             config.add_section('additional')
    #             pass
    #
    #         config.set('additional', 'resultsPath', path)
    #         key = self.get_result_key(config)
    #         config.set('additional', 'key', key)
    #         config = self.add_missing_items(config)
    #         if self.verbosity or True:
    #             print 'key', key, config.get('RunInfo', 'runno'), \
    #                 config.get('RunInfo', 'realRunNo'),\
    #                 config.get('RunInfo', 'cor') , config.get('RunInfo', 'realrunno')
    #         results[key] = config
    #
    #         with open(path, 'w') as configfile:
    #             #print 'write ', path
    #             config.write(configfile)
    #     return results
    #
    # def add_missing_items(self, config):
    #     print 'HTML GEN: addMissing items to config'
    #     isCorrected = resultsCreation.is_corrected(config)
    #     runno = config.getint('RunInfo', 'runno')
    #     config.set('RunInfo', 'realRunNo', '%d' % runno)
    #     config.set('RunInfo', 'cor', '%s' % isCorrected)
    #     newRunNo = runno
    #     print ' * runno ',config.get('RunInfo', 'runno')
    #     print ' * realRunNo ',config.get('RunInfo', 'realRunNo')
    #     print ' * cor',config.get('RunInfo', 'cor')
    #     if isCorrected:
    #         newRunNo = int(newRunNo / 10)
    #
    #     if newRunNo in self.map:
    #         config.set('RunInfo', 'repeatercardno', '%s' % self.map[newRunNo]['repeaterCard'])
    #         config.set('RunInfo', 'voltage', '%+4d' % self.map[newRunNo]['biasVoltage'])
    #         config.set('RunInfo', 'currentbegin', '%s' % (self.map[newRunNo]['currentBegin']))
    #         config.set('RunInfo', 'currentend', '%s' % (self.map[newRunNo]['currentEnd']))
    #         if not config.has_option('RunInfo','events'):
    #             try:
    #                 config.set('RunInfo', 'events', '%s' % (self.map[newRunNo]['events']))
    #             except:
    #                 print 'cannot find events in map'
    #                 print self.map[newRunNo].keys()
    #                 pass
    #     else:
    #         print 'cannot find %s' % newRunNo
    #     config.set('RunInfo', 'runno', '%d' % newRunNo)
    #     if config.has_option('TimeDependence', 'landauclusterfitoffsetsize10'):
    #         if config.has_option('TimeDependence', 'landauclusterfitslopesize10'):
    #             offset = config.getfloat('TimeDependence', 'landauclusterfitoffsetsize10')
    #             slope = config.getfloat('TimeDependence', 'landauclusterfitslopesize10')
    #             try:
    #                 config.set('TimeDependence', 'LinFitRelChange', '%s' % (slope / offset * 100.))
    #             except:
    #                 config.set('TimeDependence', 'LinFitRelChange', '%s' % slope)
    #
    #     m2 = float(config.get('Landau_normal', 'm2/2_normal', 0))
    #     m4 = float(config.get('Landau_normal', 'm4/4_normal', -1))
    #     convergence = m2 / m4 * 100.
    #     config.set('Landau_normal', 'convergence', '%6.2f' % convergence)
    #     runDesc = config.get('RunInfo', 'descr.')
    #     dia = self.geth(newRunNo, runDesc)
    #     try:
    #         dia = json.dumps(dia)
    #         # dia = dia.split(dia[1:-1])
    #     except:
    #         pass
    #     if type(dia)==list and len(dia) ==1:
    #         dia = dia[0]
    #     config.set('RunInfo', 'dia', dia)
    #     if '?' in config.get('RunInfo', 'dia'):
    #         config.set('RunInfo', 'dia', 'unknown')
    #     return config

    def set_csv_mapping(self):
        #print 'set csv map'
        mapping = OrderedDict()
        headers = []
        header_list = self.config.options('CSV-header')
        for opt in header_list:
            content = self.config.get('CSV-header', opt).split(';')
            headers.append(content[0])
            key = content[0]

            content = content[1:]
            newcontent = {}
            keylist = -1
            k = 0
            for i in content:
                if i.startswith('<') and i.endswith('>'):
                    k = i.strip('<>').strip().split(',')
                    newcontent['key'] = [j.strip() for j in k]
                    keylist = content.index(i)
                elif content.index(i) == keylist + 1 and keylist != -1:
                    newcontent['valueType'] = i
                elif content.index(i) == keylist + 2 and keylist != -1:
                    newcontent['default'] = i
                elif i.startswith('TITLE[') and i.endswith(']'):
                    newcontent['title'] = i.strip('TITLE[]').strip("'")
                else:
                    newcontent['info_%d' % k] = i
                    k += 1
            mapping[key] = newcontent
            pass
        self.csv_mapping = mapping

    def set_header(self):
        headers = []
        header_keys = []
        mapping = OrderedDict()
        header_list = self.config.options('HTML-header')
        # print list
        for i in header_list:
            content = self.config.get('HTML-header', i).split(';')
            header_keys.append(content[0])
            if content[0] == 'RunNo':
                headers.append(HTML.link('RunNo', 'results.html'))
            elif content[0] == 'Diamond':
                headers.append(HTML.link('Diamond', 'results_diamonds.html'))
            else:
                headers.append(content[0])
            key = content[0]
            content = content[1:]
            newcontent = {}
            keylist = -1
            k = 0
            for j in content:
                if j.startswith('<') and j.endswith('>'):
                    m = j.strip('<>').strip().split(',')
                    newcontent['key'] = [l.strip() for l in m]
                    keylist = content.index(j)
                elif content.index(j) == keylist + 1 and keylist != -1:
                    newcontent['valueType'] = j
                elif content.index(j) == keylist + 2 and keylist != -1:
                    newcontent['default'] = j
                elif j.startswith('TITLE[') and j.endswith(']'):
                    newcontent['title'] = j.strip('TITLE[]').strip("'")
                else:
                    newcontent['info_%d' % k] = j
                    k += 1
            mapping[key] = newcontent

        for i in headers:
            if 'href' in i:
                pass
            else:
                pass
        self.headers = headers
        self.header_mapping = mapping
        self.header_keys = header_keys
        # print header_keys
        # print mapping
        # raw_input('Headers: %s'%headers)

    @staticmethod
    def get_link(value, string_format, haslink, result):
        mainLink = result.get('RunInfo', 'mainLink')
        if haslink != 'None':
            # print haslink
            if '%(mainLink' in haslink and haslink.endswith('>)'):
                divided = haslink.rsplit('%', 1)
                # print 'divided "%s"'%divided
                entries = divided[1].strip('()')
                entries = entries.rsplit('<')
                entry = entries[-1].strip('<>').split(',')
                # print entry
                link = divided[0].strip("'") % (mainLink, result.get(entry[0], entry[1]))
            elif '%mainLink' in haslink:
                links = haslink.rsplit('%', 1)
                # replace('%mainLink','')%mainLink
                link = links[0].strip("'") % mainLink
            elif '%diamondName' in haslink:
                links = haslink.rsplit('%', 1)
                # replace('%mainLink','')%mainLink
                link = links[0].strip("'") % result.get('RunInfo','dia')
            else:
                link = haslink
            try:
                website = string_format % value
            except:
                print 'ERROR could not convert "%s"' % string_format
                website = string_format
            ouput_link = HTML.link(website, link)
            return ouput_link
        try:
            website = string_format % value
        except:
            print 'ERROR could not convert "%s"' % string_format
            website = string_format
        return website

    def get_cell(self, value, key, result):
        haslink = self.config.get('LINKS', key, 'None')
        # print key,haslink
        format_string = self.config.get('FORMAT', key, '%s')
        content = self.get_link(value, format_string, haslink, result)
        return resultsCreation.get_colored_cell(key, content, value, result)

    def get_content(self, result):
        row = []
        verbosity = False
        if verbosity:
            print self.header_keys
        for key in self.header_mapping:
            if verbosity:
                print ' ',key,
            mainLink = resultsCreation.get_mainLink(result, self.config.get('HTML', 'absolutePath'))
            result.set('RunInfo', 'mainLink', mainLink)
            if self.header_mapping[key].has_key('key'):
                default = self.header_mapping[key]['default']
                configKeys = self.header_mapping[key]['key']
                if result.has_section(configKeys[0]):
                    if result.has_option(configKeys[0], configKeys[1]):
                        value = result.get(configKeys[0], configKeys[1], 0)
                    else:
                        value = default
                else:
                    value = default
                if type(value) == list and len(value) == 1:
                    value = value[0]
                value_type = self.header_mapping[key]['valueType']
                value = utilities.get_value(value, value_type, default)
                if verbosity:
                    print key,configKeys,value
            elif self.header_mapping[key].has_key('title'):
                value = self.header_mapping[key]['title']
                if verbosity:
                    print key,configKeys,value,'TITLE'
            else:
                value = 'UNKNOWN'
                if verbosity:
                    print key,configKeys,value,'UNKNOWN'
            pass
            row.append(self.get_cell(value, key, result))
        if verbosity:
            raw_input()
        return row

    def get_content_rows(self, newResults, sorted_keys):
        rows = []
        for key in sorted_keys:
            # print 'KEY' ,key
            # print self.map[int(key.split('-')[0])]
            # print newResults[key].get('RunInfo','dia')
            content = self.get_content(newResults[key])
            if '16005' in key and False:
                print key
                config = newResults[key]
                print '\t', config.get('Noise', 'cmc_noise_dia')
                if config.has_option('TransparentNoise', 'noisecmnvsclustersizeslope'):
                    print '\t', config.get('TransparentNoise', 'noisecmnvsclustersizeslope')
                print '\t', config.get('Landau_clustered', 'mean2outof10_clustered')
            if key.startswith('19') and False:
                print key
                print self.map[int(key.split('-')[0])]
                print newResults[key].get('RunInfo','dia')
                # raw_input()
            rows.append(content)
        return rows

    def sort_results(self, newResults):
        f = lambda x: (self.results[x].getint('RunInfo', 'runno'), self.results[x].get('RunInfo', 'descr.'),
                       self.results[x].getint('RunInfo', 'cor') )
        return sorted(newResults, key=f)

    def sort_results_svn(self, newResults):
        g = lambda x: self.results[x]
        f = lambda x: (
            results_utilities.svn_version(x), x.get('RunInfo', 'svn_rev'), x.getint('RunInfo', 'runno'), x.get('RunInfo', 'descr.'),
            x.getint('RunInfo', 'cor'))
        h = lambda x: f(g(x))
        return sorted(newResults, key=h)

    @staticmethod
    def get_linFit_rel_change(config):
        if config.has_option('TimeDependence', 'linfitrelchange'):
            return config.getfloat('TimeDependence', 'linfitrelchange')
        return 0

    def sort_results_time(self, newResults):
        g = lambda x: self.results[x]
        f = lambda x: (self.get_linFit_rel_change(x), x.get('RunInfo', 'svn_rev'), x.getint('RunInfo', 'runno'),
                       x.get('RunInfo', 'descr.'), x.getint('RunInfo', 'cor') )
        h = lambda x: f(g(x))
        return sorted(newResults, key=h)

    def create_html_overview_table(self, newResults, html_file_name, sort='standard'):
        absolutePath = self.config.get('HTML', 'absolutePath')
        link = '%s/results_testBeams.html' % absolutePath
        htmlcode = HTML.link('Test Beam Overview', link)
        self.set_header()
        if sort == 'svn':
            sortedKeys = self.sort_results_svn(newResults)
        elif sort == 'time':
            sortedKeys = self.sort_results_time(newResults)
        else:
            sortedKeys = self.sort_results(newResults)
        rows = self.get_content_rows(newResults, sortedKeys)
        htmlcode += HTML.table(rows, header_row=self.headers)
        # html_file_name = html_file_name.replace('/','_')
        if 'XX' in html_file_name:
            try:
                testBeam = html_file_name.split('_')[-1].split('.')[0]
                htmlcode += '<BR>'
                htmlcode += HTML.link('Run_Log_%s' % testBeam,
                                      '%s/%s.txt' % (self.config.get('HTML', 'RunLog'), testBeam))
            except:
                print 'could not create link for %s' % html_file_name
        utilities.save_html_code(html_file_name, htmlcode)

    def create_diamond_html_pages(self):
        diamonds = self.get_list_of_diamonds(self.results)
        diamondLinkList = []
        for diamond in diamonds:
            print 'Create Page for diamond: "%s"' % diamond
            results = filter(lambda x: self.results[x].get('RunInfo', 'dia') == diamond, self.results)
            results = {key: self.results[key] for key in results}
            fileName = '%s/results_%s.html' % (self.config.get('HTML', 'outputDir'), diamond)
            diamondLinkList.append(HTML.link(diamond, 'results_%s.html' % diamond))
            self.create_html_overview_table(results, fileName)
        htmlcode = HTML.list(diamondLinkList)
        fileName = '%s/results_diamonds.html' % self.config.get('HTML', 'outputDir')
        if self.verbosity:
            print 'save diamond file to: "%s"' % fileName
        utilities.save_html_code(fileName, htmlcode)
        pass

    def get_list_of_diamonds(self, results):
        diamonds = [self.results[x].get('RunInfo', 'dia') for x in results]
        #raw_input(diamonds)
        dia = []
        for x in diamonds:
            if type(x) ==list:
                for y in x:
                    dia.append(y)
            else:
                dia.append(x)
        try:
            diamonds = sorted(list(set(dia)))
        except:
            print 'problem with sorting diamonds list...',
            print diamonds, type(diamonds)
            raw_input('press a key')
        return diamonds

    def create_testbeam_html_pages(self):
        testbeams = [self.results[x].getint('RunInfo', 'runno') / 100 for x in self.results]
        testbeams = sorted(list(set(testbeams)))
        testbeamDate = utilities.get_dict_from_file('%s/testBeamDates.cfg' % self.config_dir)
        for testbeam in testbeams:
            key = '%s' % testbeam
            if not key in testbeamDate:
                testbeamDate[key] = 'unkown'
            irr = utilities.get_dict_from_file('%s/irradiationType.cfg' % self.config_dir)
        allDiamonds = self.get_list_of_diamonds(self.results)
        allDiamonds = sorted(allDiamonds, key=lambda z: '%s-%s' % (irr.get(z, 'unkown'), z))
        allDiamondLinks = map(lambda z: HTML.link('%s (%s)' % (z, irr.get(z, 'unknown')), 'results_%s.html' % z),
                              allDiamonds)
        testBeamLinkTable = []
        header = [HTML.link('Test Beam', 'results.html')] + allDiamondLinks

        for testbeam in testbeams:
            results = filter(lambda z: self.results[z].getint('RunInfo', 'runno') / 100 == testbeam, self.results)
            results = {key: self.results[key] for key in results}
            diamonds = self.get_list_of_diamonds(results)
            # results = sorted(results,key=itemgetter(mapping['RunNo'],mapping['dia'],mapping['corrected']))

            print testbeam, len(results), diamonds
            fileName = '%s/results_%sXX.html' % (self.config.get('HTML', 'outputDir'), testbeam)
            fileName = fileName.replace('//', '/')
            # raw_input(fileName)
            self.create_html_overview_table(results, fileName)
            fileName = 'results_%sXX.html' % testbeam
            row = [HTML.link('%sXX - %s ' % (testbeam, testbeamDate['%s' % testbeam]), fileName)] + map(
                lambda z: z in diamonds, allDiamonds)
            testBeamLinkTable.append(row)
        htmlcode = HTML.table(testBeamLinkTable, header_row=header)
        fileName = '%s/results_testBeams.html' % self.config.get('HTML', 'outputDir')
        utilities.save_html_code(fileName, htmlcode)


    def create_csv_file(self):
        print 'Creating csv file'
        sortedKeys = self.sort_results(self.results)
        # data = ["value %d" % i for i in range(1,4)]
        f = open("%s/results.csv" % self.config.get('HTML', 'outputDir'), "w")
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONE)
        for key in sortedKeys:
            data = self.get_csv_row(self.results[key])
            writer.writerow(data)
        f.close()

    def get_csv_row(self, config):
        row = []
        # result = self.results
        for key in self.csv_mapping:
            if 'event' in key:
                pass
                #print 'get csv row',key,self.csv_mapping.keys(),self.csv_mapping[key]
            result = config
            if 'key' in self.csv_mapping[key]:
                if 'event' in key:
                    print 'get csv row',self.csv_mapping[key]
                try:
                    default = self.csv_mapping[key]['default']
                except:
                    default = 'unknown'
                configKeys = self.csv_mapping[key]['key']
                if result.has_section(configKeys[0]):
                    if result.has_option(configKeys[0], configKeys[1]):
                        value = result.get(configKeys[0], configKeys[1], 0)
                    else:
                        if 'event' in key:
                            print 'need to take default'
                        value = default
                else:
                    if 'event' in key:
                        print 'need to take default'
                    value = default
                try:
                    value_type = self.csv_mapping[key]['valueType']
                except:
                    value_type = 'string'
                value = utilities.get_value(value, value_type, default)
                if 'event' in key:
                    print key,configKeys,value
            else:
                if 'event' in key:
                    # print 'cannot find mapping',key
                    pass
                try:
                    if 'title' in self.header_mapping[key]:
                        value = self.csv_mapping[key]['title']
                except:
                    value = 'UNKOWN'
            pass
            try:
                string_format = self.config.get('FORMAT', key, '%s')
            except:
                print 'cannot find format for key', key
                string_format = '%s'
            if 'event' in key:
                print key,string_format, value,
            try:
                out = string_format % value
            except:
                print 'cannot format "%s"/"%s" for key %s"' % (string_format, value, key),default
                out = None
            if out is None:
                try:
                    out = value
                except:
                    out = 'UNKNOWN'

            out = out.strip('"')
            row.append(out)
        return row
        pass

    # NewRunKeys_Extended = [
    # "RunNumber",
    # "Diamond",
    # "Corrected",
    # "Voltage",
    # "Repeater card",
    # "Current start",
    # "Current end",
    # "irradiation",
    # "RunNumber_x",
    # "Descr",
    # "Noise", "Noise CMC","CMN", "Feed through SIL","sigma feed through Sil","Feed through DIA",
    # "Mean PH clustered","Most Probable PH clustered","width clustered","gs_clustered",
    # "Mean PH 2 out 10 transparent","Most Probable 2 out 10 transparent","width 2 out 10 transparent",
    # "sigma 2 out 10 transparent",
    # "Mean 2 channels transparent","Mean PH 4 channels transparent",
    # "Mean PH 2 out 10 transparent allign","Most Probable 2 out 10 transparent allign",
    # "width 2 out 10 transparent allign"
    # ,"sigma 2 out 10 transparent allign",
    # "Mean 2 channels transparent allign","Mean PH 4 channels transparent allign",
    # "Res_DG1n", "Res_DG2n", "Res_SGSn", "Res_SGNn", "Res_SGFn",
    # "Res_DG1t","Res_DG2t", "Res_SGSt", "Res_SGNt", "Res_SGFt",
    # "REV","REV"]

    def create_all_html_tables(self):
        # print 'RESULTS',self.results
        self.create_html_overview_table(self.results, '%s/results.html' % self.config.get('HTML', 'outputDir'))
        self.create_html_overview_table(self.results, '%s/resultsSVN.html' % self.config.get('HTML', 'outputDir'),
                                        sort='svn')
        self.create_html_overview_table(self.results, '%s/resultsTime.html' % self.config.get('HTML', 'outputDir'),
                                        sort='time')
        self.create_diamond_html_pages()
        self.create_testbeam_html_pages()
        # print 'RESULTS',self.results
        # self.create_csv_file()
        #

if __name__ == "__main__":
    full_path = os.path.realpath(__file__)
    directory = os.path.dirname(full_path)

    generator = HTMLGenerator('%s/config/' % directory)
    generator.update_crosstalk_factors = False
    generator.create_tables()
    generator.create_all_html_tables()
    with  open('data.pkl', 'wb') as output:
        pickle.dump(generator.results, output)
