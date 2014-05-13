import os
import scandir
import math

def list_files(dir,name,level=0):
    print 'list_files in "%s" with name "%s"'%(dir,name)
    r = []                                                                                                            
    walk = scandir.walk(dir,followlinks=True)
    for root,dirs,files in walk:
        if '/root' in root:
            continue
        if (len(files) > 0):                                                                                          
            for file in files:                                                                                        
                if name in file:
                    r.append(root + "/" + file)                                                                         
    print 'found %d files'%len(r)
    return r

def get_dict_from_file(filename):
    try:
        f = open(filename)
    except:
        print 'cannot read file', filename
        return {}
    lines = f.readlines()
    myDict = {}
    for line in lines:
        line = line.split(':')
        line = [i.strip() for i in line]
        if len(line)>2:
            line = [line[0],' '.join(line[1:])]
        elif len(line)<2:
            continue
        myDict[line[0]] = line[1]
    return myDict

def convertNumber(s):
    if s == '-nan':
        s =-99
    try:
        try:
            a = int(s)
            if a > 5e7:
                a = -99
            elif a <-999:
                a = -99
        except ValueError:
            a = float(s)
            if a > 5e7:
                a = -99
            if a < -999:
                a = -99
        if a == int(a):
            a = int(a)
    except:
        a = s
    return a
    
def convertNumbers(input_list):
    if type(input_list) == str:
        return convertNumber(input_list)
    elif type(input_list) != list:
        raise Exception('wrong type of input_list: %s'%type(input_list))
    output_list = []
    for s in input_list:
        a = convertNumber(s)
        output_list.append(a)
    return output_list
    
def get_value(input,convert,default=''):
#    print 'convert ' , input,convert
    if '/' in input:
            input = input.split('/')
            retVal = [get_value(i,convert,default) for i in input]
    
    elif convert =='int':
        try:
            retVal = int(input)
        except:
            retVal= get_value(default,'int','-9999')
    elif convert =='float':
        try:
            retVal = float(input)
        except:
            retVal= get_value(default,'float','-9999')
        if abs(retVal) >  1e10:
            retVal= get_value(default,'float','-9999')
    else:
        retVal = input
    return retVal
        
def analze_link(haslink):
	return
				
