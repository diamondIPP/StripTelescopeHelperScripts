import HTML
import ConfigParser
import math
import utilities
from operator import itemgetter, attrgetter
import os
import dictCreater

def read_result_config(file_list):
    results = []
    verbose = False
    for i in file_list:
        config = ConfigParser.ConfigParser()
        config.read(i)
        if verbose:
            for section_name in config.sections():
                print 'Section:', section_name
                #print '  Options:', config.options(section_name)
                for name, value in config.items(section_name):
                    print '  %s = %s' % (name, value)
                print
        results.append(config)
    return results

def read_result_files(file_list):
    header = None
    results = []
    for i in  file_list:
        f = open(i,'r')
        for line in f.readlines():
            if not line.startswith('#'):
                if line != '':
                    result = line.split()
                    result = convertNumbers(result)
                    results.append(result)
            else:
                result = line.split()
                if header == None:
                    header = result
                    #print i
                    #print line
                elif len(result)>len(header):
                    header = result
                    #print i
                    #print line
                #elif len(result) != len(header):
                #print i,len(result),len(header)

                pass
        f.close()
    return header,results



def create_html_overview_table(newResults,html_file_name,mapping):
    #print mapping
    kinder = 'http://kinder.ethz.ch/output/new/'
    j = 0
    headers =[]
    rows = []
    oldrows = []
    #newResults = sorted(newResults,key=itemgetter(mapping['dia'],mapping['RunNo'],mapping['corrected']))
    newResults = sorted(newResults,key=itemgetter(mapping['RunNo'],mapping['descr.'],mapping['corrected']))
    link = '%s/results_testBeams.html'%kinder
    htmlcode = HTML.link('Test Beam Overview',link)
    
    oldtestbeam = 0
    for i in newResults:
        desc = i[mapping['descr.']]
        realRunNo = i[mapping['#RunNo']]
        if desc =='0' or desc == 0:
            mainLink ='%s/%s'%(kinder,realRunNo)
        else:
            mainLink ='%s/%s/%s'%(kinder,realRunNo,desc)
        row = []
        
        runNo = i[mapping['RunNo']]
        testbeam = int(int(runNo)/100)
        if j ==0:
            oldtestbeam = testbeam
            pass
        if oldtestbeam != testbeam:
            rows.append(['']*len(headers))
        oldtestbeam = testbeam

        link = '%s/overview.html'%mainLink
        row.append( HTML.link('%s'%runNo,link))
        #row.append('%s'%runNo)
        if j==0: headers.append(HTML.link('RunNo','results.html'))

        cor = i[mapping['corrected']]
        row.append('%s'%cor)
        if j==0: headers.append('cor')

        row.append('%s'%desc)
        if j==0: headers.append('Descr.')

        row.append('%s'%i[mapping['dia']])
        if j==0: headers.append('Diamond')

        row.append('%s'%i[mapping['voltage']])
        if j==0: headers.append('Voltage')

#repeaterCardMap[runNo][1]repeaterCardMap[runNo][1]'repeaterCard','current_begin','current_end'
        if mapping.has_key('repeaterCard'):
            row.append('%s'%i[mapping['repeaterCard']])
        else:
            colored_cell = HTML.TableCell('-1', bgcolor=Red)
            row.append(colored_cell)
        if j==0: headers.append('rep. card')

        if mapping.has_key('current_begin'):
            row.append('%s'%i[mapping['current_begin']])
        else:
            row.append('??')
        if j==0: headers.append('cur. begin')

        if mapping.has_key('current_end'):
            row.append('%s'%i[mapping['current_end']])
        else:
            row.append('??')
        if j==0: headers.append('cur. end')



        try:
            if mapping.has_key('Noise'):
                noise = i[mapping['Noise']]
            else:
                noise = i[mapping['noise']] 
        except:
            print 'cannot find  noise in mapping',mapping
            noise = -1
        link = '%s/pedestalAnalysis///hNoiseDistributionOfAllNonHitChannels_Dia.png'%mainLink
        row.append( HTML.link('%4.2f'%noise,link))
        if j==0: headers.append('noise')

        cmcnoise= i[mapping['CMCnoi']]
        link = '%s/pedestalAnalysis/hNoiseDistributionOfAllNonHitChannels_Dia_CMNcorrected.png'%mainLink
        row.append( HTML.link('%4.2f'%cmcnoise,link))
        if j==0: headers.append('noise CMC')

        cmn= i[mapping['CMN']]
        link = '%s/pedestalAnalysis/hCMNoiseDistribution.png'%mainLink
        row.append( HTML.link('%4.2f'%cmn,link))
        if j==0: headers.append('CMN')
    
        corSil = i[mapping['CorSil']]
        sigSil = i[mapping['sigSil']]
        link = '%s/clustering/clustering.html#C4'%mainLink
        if abs(corSil) > 10.0:
            color = 'red'
        else:
            color = 'white'
        row.append(HTML.TableCell(HTML.link('%4.2f +/- %4.2f'%(corSil,sigSil),link), bgcolor=color))
        if j==0: headers.append('feed through SIL')

        corDia = i[mapping['CorDia']]
        link = 
        if abs(corDia) > 10.0:
            color = 'red'
        else:
            color = 'white'
        row.append(HTML.TableCell(HTML.link('%4.2f'%(corDia),link), bgcolor=color))
        if j==0: headers.append('feed through DIA')

        if mapping.has_key('m_clus'):
            m_clus = i[mapping['m_clus']]
        else:
            m_clus = -1
        m2_10 = i[mapping['m2/10']]

        link = '%s//transparentAnalysis//cLandau_Clustered.png'%mainLink
        if m_clus < 0:
            colored_cell = HTML.TableCell(HTML.link('%7.2f'%m_clus,link), bgcolor='red')
        elif m_clus < 10:
            colored_cell = HTML.TableCell(HTML.link('%7.2f'%m_clus,link), bgcolor='pink')
        elif m_clus > m2_10:
            colored_cell = HTML.TableCell(HTML.link('%7.2f'%m_clus,link), bgcolor='yellow')
        else:
            colored_cell = HTML.TableCell(HTML.link('%7.2f'%m_clus,link), bgcolor='white')
        row.append(colored_cell )
        if j==0: headers.append('Mean clustered')

        link = '%s//transparentAnalysis//cDiaTranspAnaPulseHeightOf2HighestIn10Strips.png'%mainLink
        if m2_10 < 0:
            color = 'red'
        elif m2_10 < 10:
            color = 'pink'
        elif m2_10 < m_clus:
            color = 'yellow'
        else:
            color = 'white'
        row.append(HTML.TableCell(HTML.link('%7.2f'%m2_10,link), bgcolor=color))
        if j==0: headers.append('Mean {2/10} trans')

        #mp2_10 = i[mapping['mp2/10']]
        #link = '%s//transparentAnalysis//cDiaTranspAnaPulseHeightOf2HighestIn10Strips.png'%mainLink
        #row.append( HTML.link('%7.2f'%mp2_10,link))
        #if j==0: headers.append('MP_{2/10},trans')

        #w2_10 = i[mapping['w2/10']]
        #link = '%s//transparentAnalysis//cDiaTranspAnaPulseHeightOf2HighestIn10Strips.png'%mainLink
        #row.append( HTML.link('%7.2f'%w2_10,link))
        #if j==0: headers.append('LandauWidth_{2/10},trans')

        #sig2_10 = i[mapping['sig2/10']]
        #link = '%s//transparentAnalysis//cDiaTranspAnaPulseHeightOf2HighestIn10Strips.png'%mainLink
        #row.append( HTML.link('%7.2f'%sig2_10,link))
        #if j==0: headers.append('GausWidth_{2/10},trans')

        try:
            if mapping.has_key('m4/4'):
                m4 = i[mapping['m4/4']]
            else:
                m4 = i[mapping['m4']]
        except:
            m4 = -1

        link = '%s//transparentAnalysis//cDiaTranspAnaPulseHeightOf4Strips.png'%mainLink
        if m4 < 0:
            color = 'red'
        elif m4<10:
            color = 'pink'
        else:
            color = 'white'
        row.append(HTML.TableCell(HTML.link('%7.2f'%m4,link), bgcolor=color))
        if j==0: headers.append('Mean {4/4} trans')

        try:
            if mapping.has_key('m2/2'):
                m2 = i[mapping['m2/2']]
            else:
                m2 = i[mapping['m2']]
        except:
            m2 = -1

        link = '%s//transparentAnalysis//cDiaTranspAnaPulseHeightOf2Strips.png'%mainLink
        if m2 < 0:
            color = 'red'
        elif m2 <10:
            color = 'pink'
        else:
            color = 'white'
        row.append(HTML.TableCell(HTML.link('%7.2f'%m2,link), bgcolor=color))
        if j==0: headers.append('Mean {2/2} trans')

        link = '%s/transparentAnalysis/hDiaTranspAnaPulseHeightOf2HighestMean.png'%mainLink
        if m4 == 0: m4 = -1
        conv = m2/m4*100   
        if abs(conv) < 50.0:
            color = 'red'
        else:
            color = 'white'
        row.append(HTML.TableCell(HTML.link('%4.1f %%'%conv,link), bgcolor=color))
        if j ==0: headers.append('conv.')
        #http://kinder.ethz.ch/output/new//16000/left//transparentAnalysis//hDiaTranspAnaPulseHeightOf2HighestMean.png

        row.append(HTML.link('Results','%s/results_%s.res'%(mainLink,realRunNo)))
        if j==0: headers.append('Results table')

        row.append('%s'%i[-1])
        if j==0: headers.append('SVN REV')
        #print row,headers
        j+=1
        if i[-1] == '956M':
            oldrows.append(row)
            continue
        rows.append(row)
        pass
    rows += oldrows
    htmlcode += HTML.table(rows,header_row=headers)
    #print htmlcode
    html_file_name = html_file_name.replace('/','_')
    if 'XX' in html_file_name :
        try:
            testBeam = html_file_name.split('_')[-1].split('.')[0]
            htmlcode += '<BR>'
            htmlcode += HTML.link('Run_Log_%s'%testBeam,'./RunLogs/%s.txt'%testBeam)
        except:
            print 'coudl not create link for %s'%html_file_name
    f = open(html_file_name,'w')
    f.write(htmlcode)
    f.close()

def create_testbeam_html_pages(newResults,mapping):
    testbeams = map(lambda x: int(x[mapping['RunNo']])/100,newResults)
    testbeams = sorted(list(set(testbeams)))
    testbeamDate = {110:'Aug 2007', 120: 'Oct 2007',130:'Aug 2008', 
            140: 'June 2009',141: 'Sept 2009',142:'Nov 2009',
            150:'june 2010',151:'Aug 2010',152:'Oct 2010',
            160:'June 2011', 161:'Aug 2011',162:'Sept 2011',163:'Oct 2011',
            170:'July 2012', 171:'Aug 2012',172:'Oct 2012',173:'Nov 2012'}
    for testbeam in testbeams:
        if not testbeamDate.has_key(testbeam):
            testbeamDate[testbeam] = 'unkown'
    allDiamonds = map(lambda x: x[mapping['dia']], newResults)
    irr = utilities.get_dict_from_file('irradiationType.cfg')
    allDiamonds = sorted(list(set(allDiamonds)))
    allDiamonds = sorted(allDiamonds,key = lambda x:'%s-%s'%(irr.get(x,'??'),x))
    allDiamondLinks = map(lambda x: HTML.link('%s (%s)'%(x,irr.get(x,'?')),'results_%s.html'%x),allDiamonds)
    print testbeams
    testBeamLinkTable= []
    header = [HTML.link('Test Beam','results.html')] + allDiamondLinks
    for testbeam in testbeams:
        results = filter(lambda x: int(x[mapping['RunNo']])/100 == testbeam,newResults)
        diamonds = list(set(map(lambda x:x[mapping['dia']],results)))
        results = sorted(results,key=itemgetter(mapping['RunNo'],mapping['dia'],mapping['corrected']))

        print testbeam,len(results),diamonds
        fileName = 'results_%sXX.html'%testbeam
        create_html_overview_table(results,fileName,mapping)
        row = [HTML.link('%sXX - %s '%(testbeam,testbeamDate[testbeam]),fileName)] + map(lambda x: x in diamonds,allDiamonds)
        testBeamLinkTable.append(row)
    htmlcode = HTML.table(testBeamLinkTable,header_row = header)
    fileName = 'results_testBeams.html'
    with open(fileName, "w") as f:
        f.write('%s'%htmlcode)

    pass

def create_diamond_html_pages(newResults,mapping):
    diamonds = map(lambda x: x[mapping['dia']],newResults)
    diamonds = sorted(list(set(diamonds)))
    diamondLinkList = []

    for diamond in diamonds:
        results = filter(lambda x: x[mapping['dia']]==diamond,newResults)
        fileName = 'results_%s.html'%diamond
        diamondLinkList.append(HTML.link(diamond,fileName))
        create_html_overview_table(results,fileName,mapping)
        print diamond
    htmlcode = HTML.list(diamondLinkList) 
    fileName = 'results_diamonds.html'
    with open(fileName, "w") as f:
        f.write('%s'%htmlcode)
    pass


def get_results(results):
    newResults2 = []
    irradiationMap = utilities.get_dict_from_file('irradiationType.cfg')
    for result in results:
        return
        print result, result.sections()
        result['RunInfo']

        runNo = result['RunInfo']['RunNo']
        runDes= result['RunInfo']['descr.']
        corrected = result['RunInfo']['corrected']
        diamond = result['RunInfo']['dia']
        voltage = result['RunInfo']['Voltage']
        repeaterCard = result['RunInfo']['RepeaterCardNo']
        currentBegin = result['RunInfo']['currentBegin']
        currentEnd   = result['RunInfo']['currentEnd']
        if irradiationMap.has_key(diamond):
            irradiation = irradiationMap[diamond]
        else:
            irradiation = ''
        result['RunInfo']['Irradiation'] = irradiation
        newResults2.append(['%s'%runNo,diamond,'%s'%corrected,'%s'%voltage,'%s'%repeaterCard,'%s'%currentBegin,'%s'%currentEnd,irradiation])
    return newResults2

def get_crosstalk_factor_map():
    #    crossTalkCorrectionFactors.17100.txt
    print 'get crosstalk factor map'
    fileList = list_files('.','crossTalkCorrectionFactors')
    crosstalks = {}
    for fileName in fileList:
        f = open(fileName)
        lines = f.readlines()
        runNo = int(fileName.replace('/','.').split('.')[-2])
        corrections = [float(i.replace('\t',' ').replace('\n','').split()[1].strip('%'))/100 for i in lines]
        diaCorrection = corrections[-1]
        silCorrections = corrections[:-1]
        silCor = reduce(lambda x, y: x + y, silCorrections)/len(silCorrections)
        silCor2 = reduce(lambda x, y: x + y, map(lambda x:x**2,silCorrections))/len(silCorrections)
        sigSil = math.sqrt(silCor2-silCor*silCor)
        crosstalks[runNo] = {'meanSil': silCor, 'sigSil':sigSil, 'meanDia':diaCorrection}
    print fileList
    return crosstalks


if __name__ == "__main__":
    logfiles = '/scratch/dmitry/rd42_beamtest_logfiles/all_log.txt'
    runInfo = dictCreater.getRunInfo(logfiles)
    repeaterCardFileName = './repeaterCard_Currents.csv'
    repeaterCardMap = dictCreater.get_repeaterCard_map(repeaterCardFileName)
    irradiationMap = dictCreater.get_irradiation_map('irradiationType.cfg')
    
    file_list = list_files('.','results')
    file_list2 = [i for i in file_list if i.endswith('.res') ]
    file_list = [i for i in file_list if i.endswith('.txt') and '_new_' in i ]
    print 'file lists created'
    header, results = read_result_files(file_list)
    results2 = read_result_config(file_list2)
    
    header.append('REV')
    print header

    newResults = []
    newResults2 =[]
    newResults2 = get_results(results2)
    results = sorted(results,key=itemgetter(0))
    for i in results:
        try:
            runNo = int(i[0])
        except:
            print 'could not extract',i
            continue
        runDes = i[1]
        found = False
        corrected = 0
        if runInfo.has_key(runNo):
            found = True
        elif int(runNo/1e5) == 0:
            pass
        else:
            runNo = int(runNo/10)
            if runInfo.has_key(runNo):
                found = True
            corrected = 1  

        if found:
            voltage = runInfo[runNo][1]
            diamond = runInfo[runNo][0]
            if type(runDes) == str:
                diamond = diamond.split('/')
                if len(diamond) == 2:
                    if runDes == 'left':
                        diamond = diamond[0]
                    elif runDes == 'right':
                        diamond = diamond[1]
                    else:
                        print 'cannot find ',runDes
                    if type(diamond)==list:
                        diamond = diamond[0]
                else:
                    diamond = diamond[0]
                    print 'cannot split ',diamond,runDes
        else:
            #print 'cannot find %6s\t %5s %d'%(i[0],i[1],len(i))
            voltage = -1
            diamond = '??'

        print '%6s/%s\t%7s\t %5s %d'%(i[0],runNo,diamond,i[1],len(i))

        if repeaterCardMap.has_key(runNo):
            repeaterCard = repeaterCardMap[runNo][2]
            currentBegin = repeaterCardMap[runNo][0]
            currentEnd = repeaterCardMap[runNo][1]
        else:
            repeaterCard =''
            currentBegin = ''
            currentEnd = ''
        if irradiationMap.has_key(diamond):
            irradiation = irradiationMap[diamond]
        else:
            irradiation = ''

        newResults.append(['%s'%runNo,diamond,'%s'%corrected,'%s'%voltage,'%s'%repeaterCard,'%s'%currentBegin,'%s'%currentEnd,irradiation] + i)


    header = ['RunNo','dia','corrected','voltage','repeaterCard','current_begin','current_end','irradiation']+header


    f = open('results.csv','w')
    f.write(';'.join(header)+'\n')
    for i in newResults:
        k = ['%s'%j for j in i]
        f.write(';'.join(k)+'\n')
    f.close()

    mapping = {}
    for i in range(0,len(header)):
        key = header[i]
        key = key.replace('\x04','')
        if mapping.has_key(key):
            key+='_1'
        mapping[key] = i 
        print '%3d\t"%s"'%(i,key)

    newResults = sorted(newResults,key=itemgetter(mapping['RunNo'],mapping['corrected']))
    create_html_overview_table(newResults,'results.html',mapping)
    create_diamond_html_pages(newResults,mapping)
    create_testbeam_html_pages(newResults,mapping)
