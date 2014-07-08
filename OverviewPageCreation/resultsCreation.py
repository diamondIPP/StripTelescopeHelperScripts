import ConfigParser
import math

import HTML

import utilities


def is_corrected(config):
    input1 = config.get('RunInfo', 'realRunNo')
    input2 = config.get('RunInfo', 'runno')
    runNo = utilities.get_value(input2, 'int', '-1')
    realRunNo = utilities.get_value(input1, 'int', '-1')
    retVal = 0
    if realRunNo == runNo:
        retVal = 0
    else:
        retVal = 1
    if int(runNo / 1e5) == 0:
        retVal = 0
    else:
        retVal = 1
    return retVal


def get_mainLink(result, absPath):
    desc = result.get('RunInfo', 'descr.')
    realRunNo = result.get('RunInfo', 'realrunno')
    if desc == '0' or desc == 0:
        mainLink = '%s/%s' % (absPath, realRunNo)
    else:
        mainLink = '%s/%s/%s' % (absPath, realRunNo, desc)
    return mainLink


def get_colored_cell(key, content, value, result):
    color = 'white'
    if key == 'ADC steps':
        try:
            v = int(value)
        except:
            v = -1
        if v == 0:
            color = 'green'
        elif v > 0:
            color = 'red'
    elif key == 'rep. card' and int(value) <= 0:
        color = 'pink'
    elif key == 'feedthrough SIL' and abs(float(value)) > 10:
        color = 'red'
    elif key == 'feedthrough DIAL' and abs(float(value)) > 10:
        color = 'red'
    elif key == 'Mean clustered' or key == '':
        valueClustered = result.getfloat('Landau_clustered', 'mean2outof10_clustered')
        valueTransparent = result.getfloat('Landau_normal', 'mean2outof10_normal')
        if valueClustered > valueTransparent:
            color = 'yellow'
    elif key == 'noise CMC':
        try:
            normal = result.getfloat('Noise', 'cmc_noise_dia')
            transparent = result.getfloat('TransparentNoise', 'noisecmnvsclustersizeoffset')
            if normal > 0 and transparent > 0 and abs((transparent - normal) / normal) > .1:
                color = 'yellow'
        except:
            pass
    elif key == 'CMN':
        cmn1 = result.getfloat('Noise','cm_noise_dia')
        cmn2 = result.getfloat('Noise','cmn_sigma',-1)
        cmn_pos = result.getfloat('Noise','cmn_pos',0)
        if cmn2 >= 0:
            color = 'green'
            if abs(cmn1-cmn2)/cmn1 >.1:
                color ='red'
            elif abs(cmn1-cmn2)/cmn1 >.05:
                color = 'yellow'
        if abs(cmn_pos) >1:
            color = 'yellow'

    elif key == 'NoiseCMN Slope':
        if abs(value) > 0.1:
            color = 'red'

    if color != 'white':
        return HTML.TableCell(content, bgcolor=color)
    return content
