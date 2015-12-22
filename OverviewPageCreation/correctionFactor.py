import math
import os
import ConfigParser

import utilities


verbosity = 0


def get_crosstalk_factor_map(dir):
    # crossTalkCorrectionFactors.17100.txt
    print '    - get crosstalk factor map,"%s"' % dir
    fileList = utilities.list_files(dir, 'crossTalkCorrectionFactors',indentation=9)
    print '    - list: ', fileList
    crosstalks = {}
    for fileName in fileList:
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
        if verbosity: print '    - ',runNo, crosstalks[key]
    return crosstalks


def create_new_results_res_file(runNo, crosstalk):
    if verbosity: print '    - create new results res file for %s' % runNo
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
    fileName = fileName.replace('_', '_new_');
    f = open(fileName, 'w')
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
    newResFile = open(fileName.replace('_', '_new_'), 'w')
    for line in lines:
        newResFile.write(line)


def update_crosstalk_factors(dir):
    crosstalks = get_crosstalk_factor_map(dir)

    for runNo in crosstalks:
        create_new_results_text_file(runNo, crosstalks[runNo])
        create_new_results_res_file(runNo, crosstalks[runNo])


if __name__ == "__main__":
    update_crosstalk_factors('.')
    pass

