import json
import scandir
import time

def list_files(dir, name, level=0, indentation=0,followlinks=True):
    str_ind = ' '*indentation
    print str_ind+'list_files in "%s" with name "%s"' % (dir, name)
    r = []
    walk = scandir.walk(dir, followlinks=followlinks)
    for root, dirs, files in walk:
        if '/root' in root:
            continue
        if (len(files) > 0):
            for file in files:
                if name in file:
                    r.append(root + "/" + file)
    print str_ind+'found %d files' % len(r)
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
        if len(line) > 2:
            line = [line[0], ' '.join(line[1:])]
        elif len(line) < 2:
            continue
        myDict[line[0]] = line[1]
    return myDict


def convertNumber(s):
    if s == '-nan':
        s = -99
    try:
        try:
            a = int(s)
            if a > 5e7:
                a = -99
            elif a < -999:
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
        raise Exception('wrong type of input_list: %s' % type(input_list))
    output_list = []
    for s in input_list:
        a = convertNumber(s)
        output_list.append(a)
    return output_list


def get_value(input, convert, default=''):
    """

    :rtype : object
    """

    # print 'convert ' , input,convert
    if '/' in input:
        input = input.split('/')
        retVal = [get_value(i, convert, default) for i in input]
    elif 'list' in convert:
        input = input.split('/')
        convert = convert.replace('list', '')
        retVal = [get_value(i, convert, default) for i in input]
    elif convert == 'int':
        try:
            retVal = int(input)
        except:
            retVal = get_value(default, 'int', '-9999')
    elif convert == 'float':
        try:
            retVal = float(input)
        except:
            retVal = get_value(default, 'float', '-9999')
        if abs(retVal) > 1e10:
            retVal = get_value(default, 'float', '-9999')
    else:
        retVal = input
    return retVal


def analze_link(haslink):
    return
				
def getDiamond(map, runno, descr):
    dia = 'unknown'
    print 'getDiamond: ',runno,descr,'-->',
    if runno in map:
        dias = map[runno]['diamond']
        print dias
        if type(dias) == list:
            if len(dias) > 1:
                if 'left' in descr or '1' in descr:
                    dia = dias[0]
                elif 'right' in descr or '2' in descr:
                    dia = dias[1]
                else:
                    dia = dias[0]
                pass
            else:
                dia = dias[0]
        else:
            dia = dias
    if type(dia) == list:
        if len(dia) == 1:
            dia = dia[0]
        else:
            raise Exception('invalid Diamond name')
    dia = dia.strip('"')
    return dia

def get_result_key(main_config,config):
        key = ''
        keyNames = main_config.get('Results', 'key').split(';')
        for i in keyNames:
            if i.startswith('<') and i.endswith('>'):
                i = i.strip('<>').strip()
                keyName = i.split(',')
                keyName = [i.strip() for i in keyName]
                # print 'check for : ',keyName
                # print config.sections()
                # if config.has_section(keyName[0]):
                # print config.options(keyName[0])
                if config.has_option(keyName[0], keyName[1]):
                    value = config.get(keyName[0], keyName[1])
                    key += value
                else:
                    print 'cannot finde key "%s"'%keyName[0],keyName[1]
                    if config.has_section(keyName[0]):
                        print 'options:',config.options(keyName[0])
                    else:
                        print 'sections',config.sections()
                    key += 'unknown'
            else:
                key += i
        return key

def save_html_code(html_file_name, htmlcode):
    # raw_input('html_file_name: %s'%html_file_name)
    htmlcode += '\n<br>\ncreated on %s' % time.ctime()

    f = open(html_file_name, "w")
    f.write('%s' % htmlcode)
    f.close()