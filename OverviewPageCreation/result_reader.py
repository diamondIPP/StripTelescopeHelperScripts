import HTML
import ConfigParser
#import math
import utilities
#from operator import itemgetter, attrgetter
import os
import dictCreater
import correctionFactor
import resultsCreation
from collections import *
#import re


class result_reader:
    def __init__(self,configDir):
        self.verbosity = 0
        self.configDir = configDir
        self.configFileName = configDir+'/creation.ini'
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.configFileName)
        self.updateCrosstalkFactors = True
    
    def create_tables(self):
        if self.updateCrosstalkFactors:
            print 'update correction factors'
            correctionFactor.update_crosstalk_factors(self.config.get('Results','inputDir'))
        
        print 'read dictionaries'
        mapper = dictCreater.dictCreater(self.configDir)
        self.map = mapper.get_combined_list()
        
        print 'get file list'
        # get list of files wich starts with 'results'
        file_list = utilities.list_files(self.config.get('Results','inputDir'),'results')
        if self.verbosity: print 'staring list',file_list
        self.file_list = [i for i in file_list if i.endswith('.res') and '_new' in i]
        #print 'updated file list ', self.file_list
        self.results = self.read_result_config()

    
    
    def get_result_key(self,config):
        print config.options('RunInfo')
        key = ''
        keyNames = self.config.get('Results','key').split(';')
        for i in keyNames:
            if i.startswith('<') and i.endswith('>'):
                i = i.strip('<>').strip()
                keyName = i.split(',')
                keyName = [i.strip() for i in keyName]
#               print 'check for : ',keyName
#               print config.sections()
#               if config.has_section(keyName[0]):
#                   print config.options(keyName[0])
                if config.has_option(keyName[0],keyName[1]):
                    key += config.get(keyName[0],keyName[1])
                else:
                    key +='??'
            else:
                key += i
        return key           
    
    def read_result_config(self):
        results = {}
        for i in self.file_list:
            runno = i.rsplit('_',1)[1].split('.')[0]
            config = ConfigParser.ConfigParser()
            if self.verbosity: print 'reading ',i
            config.read(i)
            print config.sections()
            if not config.has_section('RunInfo'):
                raw_input('section does not exist....')
                continue
            config.set('RunInfo','realRunNo',runno)
            if self.verbosity:
                for section_name in config.sections():
                    #print 'Section:', section_name
                    #print '  Options:', config.options(section_name)
                    for name, value in config.items(section_name):
                        #print '  %s = %s' % (name, value)
                        pass
                    #print
                    pass
            config = self.add_missing_items(config)
            key = self.get_result_key(config)
            if self.verbosity: print 'key',key,config.get('RunInfo','runno'),config.get('RunInfo','realRunNo')
            results[key] = config
        return results

    def getDiamond(self,runno,descr):
        dia= 'unknown'
        if self.map.has_key(runno):
            dias = self.map[runno]['diamond']
            if type(dias)==list:
                if len(dias)>1:
                    if 'left' in descr or '1' in descr:
                        dia = dias[0]
                    elif 'right' in descr or '2' in descr:
                        dia = dias[1]
                    else:
                        dia = dias[0]
                    pass
                else:
                    dia =dias[0]
            else:
                dia = dias
        return dia
    
    def add_missing_items(self,config):
        isCorrected = resultsCreation.is_corrected(config)
        runno = config.getint('RunInfo','runno')
        config.set('RunInfo','realRunNo','%d'%runno)
        config.set('RunInfo','cor','%s'%isCorrected)
        newRunNo = runno
        if isCorrected:
            newRunNo = int(newRunNo/10)
        config.set('RunInfo','runno','%d'%(newRunNo))

        m2 = float(config.get('Landau_normal','m2/2_normal',0))
        m4 = float(config.get('Landau_normal','m4/4_normal',-1))
        convergence = m2/m4*100.
        config.set('Landau_normal','convergence','%6.2f'%convergence)
        runDesc = config.get('RunInfo','descr.')
        dia = self.getDiamond(newRunNo,runDesc)
        config.set('RunInfo','dia',dia)
        if '?' in config.get('RunInfo','dia'):
            config.set('RunInfo','dia','unknown')
        return config
        
    def set_header(self):
        headers =[]
        mapping = OrderedDict()
        list = self.config.options('HTML-header')
        #print list
        for i in list:
            content = self.config.get('HTML-header',i).split(';')
            if content[0] == 'RunNo':
                headers.append(HTML.link('RunNo','results.html'))
            else: 
                headers.append(content[0])
            key = content[0]
            content = content[1:]
            newcontent={}
            keylist = -1
            k=0
            for i in content:
                if i.startswith('<') and i.endswith('>'):
                    k = i.strip('<>').strip().split(',')
                    newcontent['key'] = [j.strip() for j in k]
                    keylist = content.index(i)
                elif content.index(i) == keylist+1 and keylist!=-1:
                    newcontent['valueType'] = i
                elif content.index(i) == keylist+2 and keylist!=-1:
                    newcontent['default'] = i
                elif i.startswith('TITLE[') and i.endswith(']'):
                    newcontent['title'] = i.strip('TITLE[]').strip("'")
                else:
                    newcontent['info_%d'%k] = i
                    k+=1
                mapping[key] = newcontent

        for i in headers:
            if  'href' in i: 
                pass
            else:
                pass
        self.headers = headers
        self.header_mapping = mapping
    
    def get_link(self,value,format,haslink,result):
        mainLink = result.get('RunInfo','mainLink')
        if haslink !='None':
            #print haslink
            if '%(mainLink' in haslink and haslink.endswith('>)'):
                divided = haslink.rsplit('%',1)
                #print 'divided "%s"'%divided
                entries = divided[1].strip('()')
                entries = entries.rsplit('<')
                entry = entries[-1].strip('<>').split(',')
                #print entry
                link = divided[0].strip("'")%(mainLink,result.get(entry[0],entry[1]))
            elif '%mainLink' in haslink:
                links = haslink.rsplit('%',1)
                #replace('%mainLink','')%mainLink
                link = links[0].strip("'")%mainLink
            else:
                link = haslink
            output =  HTML.link(format%value,link)
            return output
        return format%value
        
    def get_cell(self,value,key,result):
        haslink = self.config.get('LINKS',key,'None')
        #print key,haslink
        format = self.config.get('FORMAT',key,'%s')
        content = self.get_link(value,format,haslink,result)
        return resultsCreation.get_colored_cell(key,content,value,result)
            

    def get_content(self,result):
        row = []
        for key in self.header_mapping:
            #print key
            mainLink = resultsCreation.get_mainLink(result,self.config.get('HTML','absolutePath'))
            result.set('RunInfo','mainLink', mainLink)
            if self.header_mapping[key].has_key('key'):
                default = self.header_mapping[key]['default']
                configKeys = self.header_mapping[key]['key']
                if result.has_section(configKeys[0]):
                    if result.has_option(configKeys[0],configKeys[1]):
                        value = result.get(configKeys[0],configKeys[1],0)
                    else:
                        value = default
                else:
                    value = default
                type = self.header_mapping[key]['valueType']
                value = utilities.get_value(value,type,default)
                #print key,configKeys,value
            elif self.header_mapping[key].has_key('title'):
                value = self.header_mapping[key]['title']
            else:
                value = 'UNKOWN'
            pass
            row.append(self.get_cell(value,key,result))
        return row
        
    def get_content_rows(self,newResults,sorted_keys):
        rows = []
        for key in sorted_keys:
            #print 'KEY' ,key
            #print self.map[int(key.split('-')[0])]            
            #print newResults[key].get('RunInfo','dia')
            rows.append(self.get_content(newResults[key]))

        return rows 
        
    def save_html_code(self,html_file_name,htmlcode):
#       raw_input('html_file_name: %s'%html_file_name)
        f = open(html_file_name, "w")
        f.write('%s'%htmlcode)
        f.close()
        
    def sort_results(self,newResults):
        return newResults
        
    def create_html_overview_table(self,newResults,html_file_name):
        absolutePath = self.config.get('HTML','absolutePath')
        link = '%s/results_testBeams.html'%absolutePath
        htmlcode = HTML.link('Test Beam Overview',link)
        self.set_header()
        rows= self.get_content_rows(newResults,sorted(newResults.keys()))
        htmlcode += HTML.table(rows,header_row=self.headers)
#       html_file_name = html_file_name.replace('/','_')
        if 'XX' in html_file_name :
            try:
                testBeam = html_file_name.split('_')[-1].split('.')[0]
                htmlcode += '<BR>'
                htmlcode += HTML.link('Run_Log_%s'%testBeam,'%s/%s.txt'%(self.config.get('HTML','RunLog'),testBeam))
            except:
                print 'could not create link for %s'%html_file_name
        self.save_html_code(html_file_name,htmlcode)
        
        
    def create_diamond_html_pages(self):
        diamonds = self.get_list_of_diamonds(self.results)
        diamondLinkList = []
        for diamond in diamonds:
            print 'Create Page for diamond: "%s"'%diamond
            results = filter(lambda x: self.results[x].get('RunInfo','dia') == diamond,self.results)
            results = {key: self.results[key] for key in results}
            fileName = '%s/results_%s.html'%(self.config.get('HTML','outputDir'),diamond)
            diamondLinkList.append(HTML.link(diamond,'results_%s.html'%diamond))
            self.create_html_overview_table(results,fileName)
        htmlcode = HTML.list(diamondLinkList) 
        fileName = '%s/results_diamonds.html'%self.config.get('HTML','outputDir')
        if self.verbosity: print 'save diamond file to: "%s"'%fileName
        self.save_html_code(fileName,htmlcode)
        pass
    
    def get_list_of_diamonds(self,results):
        diamonds = [self.results[x].get('RunInfo','dia') for x in results]
        diamonds = sorted(list(set(diamonds)))
        return diamonds
    
    def create_testbeam_html_pages(self):
        testbeams = [self.results[x].getint('RunInfo','runno')/100 for x in self.results]
        testbeams = sorted(list(set(testbeams)))
        testbeamDate = utilities.get_dict_from_file('%s/testBeamDates.cfg'%self.configDir)
        for testbeam in testbeams:
            key = '%s'%testbeam
            if not testbeamDate.has_key(key):
                testbeamDate[key] = 'unkown'
            irr = utilities.get_dict_from_file('%s/irradiationType.cfg'%self.configDir)
        allDiamonds = self.get_list_of_diamonds(self.results)
        allDiamonds = sorted(allDiamonds,key = lambda x:'%s-%s'%(irr.get(x,'unkown'),x))
        allDiamondLinks = map(lambda x: HTML.link('%s (%s)'%(x,irr.get(x,'?')),'results_%s.html'%x),allDiamonds)
        testBeamLinkTable= []
        header = [HTML.link('Test Beam','results.html')] + allDiamondLinks
        
        for testbeam in testbeams:
            results = filter(lambda x: self.results[x].getint('RunInfo','runno')/100 == testbeam,self.results)
            results = {key: self.results[key] for key in results}
            diamonds = self.get_list_of_diamonds(results)
#           results = sorted(results,key=itemgetter(mapping['RunNo'],mapping['dia'],mapping['corrected']))

            print testbeam,len(results),diamonds
            fileName = '%s/results_%sXX.html'%(self.config.get('HTML','outputDir'),testbeam)
            fileName= fileName.replace('//','/')
            #raw_input(fileName)
            self.create_html_overview_table(results,fileName)
            fileName = 'results_%sXX.html'%(testbeam)
            row = [HTML.link('%sXX - %s '%(testbeam,testbeamDate['%s'%testbeam]),fileName)] + map(lambda x: x in diamonds,allDiamonds)
            testBeamLinkTable.append(row)
        htmlcode = HTML.table(testBeamLinkTable,header_row = header)
        fileName = '%s/results_testBeams.html'%self.config.get('HTML','outputDir')
        self.save_html_code(fileName,htmlcode)

        
    def create_all_html_tables(self):
        self.create_html_overview_table(self.results,'%s/results.html'%self.config.get('HTML','outputDir'))
        self.create_diamond_html_pages()
        self.create_testbeam_html_pages()
        
if __name__ == "__main__":
    full_path = os.path.realpath(__file__)
    directory = os.path.dirname(full_path)

    reader = result_reader('%s/config/'%directory)
    reader.updateCrosstalkFactors = False
    reader.create_tables()
    reader.create_all_html_tables()

