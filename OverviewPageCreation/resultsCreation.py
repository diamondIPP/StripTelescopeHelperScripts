import ConfigParser
import utilities
import HTML
import math


def is_corrected(config):
	input1 = config.get('RunInfo','realRunNo')
	input2 = config.get('RunInfo','runno')
	print input
	runNo = utilities.get_value(input2,'int','-1')
	realRunNo = utilities.get_value(input1,'int','-1')
	print realRunNo,runNo
	if realRunNo==runNo:
		return 0
	else:
		return 1
	if (runNo/1e5)==0:
		return 0
	else:
		return 1
		
def get_mainLink(result,absPath):
	desc = result.get('RunInfo','descr.')
	realRunNo = result.get('RunInfo','runno')
	if desc =='0' or desc == 0:
		mainLink ='%s/%s'%(absPath,realRunNo)
	else:
		mainLink ='%s/%s/%s'%(absPath,realRunNo,desc)
	return mainLink

def get_colored_cell(key,content,value,result):
	print 'KEY:', key
	color ='white'
	if key =='rep. card' and int(value)<=0 :	
		color = 'red'
	elif key =='feedthrough SIL' and abs(float(value))>10 :	
		color='red'
	elif key =='feedthrough DIAL' and abs(float(value))>10 :	
		color='red'
	elif key=='Mean clustered' or key =='':
		valueClustered = result.getfloat('Landau_clustered','mean2outof10_clustered')
		valueTransparent = result.getfloat('Landau_normal','mean2outof10_normal')
		if valueClustered < valueTransparent:
			color = 'yellow'
	if color != 'white':
		return HTML.TableCell(content,bgcolor=color)
	return content