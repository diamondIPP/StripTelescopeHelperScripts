import math
import os
import ConfigParser

import utilities
import glob

verbosity = 0


def get_crosstalk_factor_map(dir):
    # crossTalkCorrectionFactors.17100.txt
    print '    - get crosstalk factor map,"%s"' % dir
    # fileList = utilities.list_files(dir, 'crossTalkCorrectionFactors',indentation=9)
    l1 = glob.glob('*/crossTalkCorrectionFactors*')#results_[0,1,2,3,4,5,6,7,8,9]*.res')
    l2 = glob.glob('*/left/crossTalkCorrectionFactors*')#/results_[0,1,2,3,4,5,6,7,8,9]*.res')
    l3 = glob.glob('*/rigth/crossTalkCorrectionFactors*')#/results_[0,1,2,3,4,5,6,7,8,9]*.res')
    fileList = l1+l2+l3
    print '    - list: ', fileList
    crosstalks = {}
    for fileName in fileList:
        # if '19008' in fileName:
        #     print i
        f = open(fileName)
        lines = f.readlines()
        runNo = fileName.replace('/', '.').split('.')[-2]
        runDes = '0'
        if '-' in runNo:
            runNo = runNo.split('-')
            if verbosity: print '    - ',runNo
            runDes = runNo[-1]
            runNo = runNo[0]
        runNo = int(runNo)

        lines = [i.replace('\t', ' ').replace('\n', '').split() for i in lines]
        lines = filter(lambda x: len(x) > 1, lines)

        corrections = [float(i[1].strip('%')) / 100 for i in lines]
        diaCorrection = corrections[-1]
        silCorrections = corrections[:-1]
        silCor = reduce(lambda x, y: x + y, silCorrections) / len(silCorrections)
        silCor2 = reduce(lambda x, y: x + y, map(lambda x: x ** 2, silCorrections)) / len(silCorrections)
        sigSil = math.sqrt(silCor2 - silCor * silCor)
        sigSil = round(sigSil, 5) * 100.
        silCor = round(silCor, 5) * 100.
        diaCorrection = round(diaCorrection, 5) * 100.
        key = "%s-%s" % (runNo, runDes)
        crosstalks[key] = {'meanSil': silCor, 'sigSil': sigSil, 'meanDia': diaCorrection, 'fileName': fileName,
                           'runDes': runDes}
        if verbosity:  print '    - ',runNo, crosstalks[key]
        # if '19008' in fileName:
        #     print '    - ',runNo, crosstalks[key]
        #     raw_input()
    return crosstalks


def create_new_results_res_file(runNo, crosstalk):
    print 'create file for ',runNo
    if runNo in [19008,190080] or  verbosity: 
        print '    - create new results res file for %s' % runNo
        raw_input()
    fileName = crosstalk['fileName']
    if verbosity:     print '    - ',fileName
    fileName = fileName.replace('crossTalkCorrectionFactors.', 'results_')
    if crosstalk['runDes'] != '0':
        fileName = fileName.replace('results', '%s/results' % crosstalk['runDes'])
        fileName = fileName.replace('-left', '')
        fileName = fileName.replace('-right', '')
    fileName = fileName.replace('.txt', '.res')

    if verbosity: print '    - ',fileName
    try:
        res = ConfigParser.ConfigParser()
        res.read(fileName)
    except:
        print '    - cannot find %s' % fileName
        return
    if 'Feed_Through_Correction' not in res.sections():
        res.add_section('Feed_Through_Correction')
    res.set('Feed_Through_Correction', 'corsil', crosstalk['meanSil'])
    res.set('Feed_Through_Correction', 'sigsil', crosstalk['sigSil'])
    res.set('Feed_Through_Correction', 'cordia', crosstalk['meanDia'])
    newFileName = fileName.replace('_', '_new_')
    if not os.path.isfile(newFileName):
        print 'create ',newFileName
    f = open(newFileName, 'w')
    res.write(f)
    return


    def create_new_results_text_file(runNo, crosstalk):
        if verbosity: print '    - create new results file for %s' % runNo
        fileName = crosstalk['fileName']
        if verbosity: print '    - ',fileName
        fileName = fileName.replace('crossTalkCorrectionFactors.', 'results_')

        if crosstalk['runDes'] != '0':
            fileName = fileName.replace('results', '%s/results' % crosstalk['runDes'])
            fileName = fileName.replace('-left', '')
            fileName = fileName.replace('-right', '')

        if verbosity: print'    - ', fileName
        try:
            resFile = open(fileName)
        except:
            print '    - cannot find %s' % fileName
            return
        lines = resFile.readlines()
        line = lines[-1].split()
        line[5] = '%s' % crosstalk['meanSil']
        line[6] = '%s' % crosstalk['sigSil']
        line[7] = '%s' % crosstalk['meanDia']
        lines[-1] = '\t'.join(line)
        newFileName = fileName.replace('_', '_new_')
        print line[5],line[6],line[7],line[-1]
        if not os.path.isfile(newFileName):
            print 'create ',newFileName
        newResFile = open(newFileName, 'w')
        for line in lines:
            newResFile.write(line)


def update_crosstalk_factors(dir):
    print 'update_crosstalk_factors',os.path.abspath(dir)
    crosstalks = get_crosstalk_factor_map(dir)
    print 'founfd ',len(crosstalks),'crosstalk files'
    print 'create_new_results_res_file'
    for runNo in crosstalks:
        # create_new_results_text_file(runNo, crosstalks[runNo])
        create_new_results_res_file(runNo, crosstalks[runNo])


if __name__ == "__main__":
    update_crosstalk_factors('.')
    pass

