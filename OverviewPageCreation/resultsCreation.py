import ConfigParser
import utilities
import HTML
import math


def is_corrected(config):
    input1 = config.get('RunInfo','realRunNo')
    input2 = config.get('RunInfo','runno')
    runNo = utilities.get_value(input2,'int','-1')
    realRunNo = utilities.get_value(input1,'int','-1')
    retVal = 0 
    if realRunNo==runNo:
        retVal =  0
    else:
        retVal =  1
    if int(runNo/1e5)==0:
        retVal = 0
    else:
        retVal =  1
    return retVal
        
def get_mainLink(result,absPath):
    desc = result.get('RunInfo','descr.')
    realRunNo = result.get('RunInfo','realrunno')
    if desc =='0' or desc == 0:
        mainLink ='%s/%s'%(absPath,realRunNo)
    else:
        mainLink ='%s/%s/%s'%(absPath,realRunNo,desc)
    return mainLink

def get_colored_cell(key,content,value,result):
    color ='white'
    if key =='rep. card' and int(value)<=0 :    
        color = 'pink'
    elif key =='feedthrough SIL' and abs(float(value))>10 : 
        color='red'
    elif key =='feedthrough DIAL' and abs(float(value))>10 :    
        color='red'
    elif key=='Mean clustered' or key =='':
        valueClustered = result.getfloat('Landau_clustered','mean2outof10_clustered')
        valueTransparent = result.getfloat('Landau_normal','mean2outof10_normal')
        if valueClustered > valueTransparent:
            color = 'yellow'
    elif key == 'noise CMC':
        try:
            normal = result.getfloat('Noise','cmc_noise_dia')
            transparent = result.getfloat('TransparentNoise','noisecmnvsclustersizeoffset')
            if normal >0 and transparent >0 and abs((transparent-normal)/normal)>.1:
                color = 'yellow'
        except:
            pass
    elif key == 'NoiseCMN Slope':
        if abs(value) > 0.1:
            color ='red'

    if color != 'white':
        return HTML.TableCell(content,bgcolor=color)
    return content
