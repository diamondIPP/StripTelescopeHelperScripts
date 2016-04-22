import ResultReader
import pickle
import ROOT
import numpy as np
import os
import ConfigParser
import dictCreater
import radiations
from collections import OrderedDict
from math import copysign

class ResidualTable:
    def __init__(self,config_dir,pickle_file = None):
        self.config_dir = config_dir
        self.config_file_name = config_dir + '/creation.ini'
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file_name)
        self.update_crosstalk_factors = True

        print ' * read dictionaries'
        mapper = dictCreater.dictCreater(self.config_dir)
        self.beam_infos = mapper.get_combined_list()
        self.result_reader = ResultReader.ResultReader(self.config,self.beam_infos)
        self.results = self.result_reader.GetResults()
        try:
            pickle_file = open('results.pkl', 'wb')
            print pickle_file,self.results
            pickle.dump(self.results, pickle_file)
            pickle_file = open('beam_infos.pkl', 'wb')
            pickle.dump(self.beam_infos, pickle_file)
        except Exception as e:
            print e
        self.ignore_runs = [19008,19010]
        self.radiations=radiations.radiations()

    def get_runs(self,diamond='PW205B',corrected=True,min_bias=0,polarity=+1,max_bias = 0):
        runs = {}
        for key,r in self.results.iteritems():
            if not r.get('RunInfo','dia')==diamond:
                continue
            if r.getboolean('RunInfo','corrected') != corrected:
                continue
            if polarity != 0 and copysign(1,r.getfloat('RunInfo','Voltage'))!=polarity:
                continue
            if abs(r.getfloat('RunInfo','Voltage')) < abs(min_bias):
                continue
            if max_bias >0 and abs(r.getfloat('RunInfo','Voltage')) > abs(max_bias):
                continue
            if r.getint('RunInfo','RunNo') in self.ignore_runs:
                continue
            runs[key]=r
        return OrderedDict(sorted(runs.items()))

    def create_Resolution_histo(self,t='Normal',method='FWHM',diamond='PW205B',corrected=True,pars=['mean','fit'],min_bias=1000,polarity=+1,max_bias=0):
        keys = []
        runs = self.get_runs(diamond=diamond,corrected=corrected,min_bias=min_bias,polarity=polarity,max_bias=max_bias)
        missing_runs = []
        parameters = OrderedDict
        section = 'Resolution'+t
        retval = OrderedDict([('runno',[]),('corrected',[]),('fluence',[]),('voltage',[])])
        for p in pars:
            retval[p]=[]
        for key,r in runs.iteritems():
            runno = r.getint('RunInfo','RunNo')
            corrected = r.getboolean('RunInfo','corrected')
            if not r.has_section(section):
                missing_runs.append((runno,'section'))
                continue
            s = ''
            for p in pars:
                opt = method +"_"+p
                par = None
                if r.has_option(section,opt):
                    par =r.getfloat(section,opt)
                elif r.has_option(section,method +p):
                    opt = method+p
                    par =r.getfloat(section,opt)
                if par is not None:
                    s+= '{p}: {par:+.2f}um,\t'.format(p=p, par=par)
                retval[p].append(par)
            fluence = self.radiations[diamond][runno]
            voltage = r.getfloat('RunInfo','Voltage')
            retval['fluence'].append(fluence)
            retval['voltage'].append(voltage)
            retval['runno'].append(runno)
            retval['corrected'].append(corrected)
            print '{runno}: {fluence:.2f} {par} {voltage:+.1f}V'.format(
                        runno=runno,
                        fluence=fluence,
                        par=s,
                        voltage = voltage)
        print 'missing runs:',missing_runs
        return retval

    def create_latex_table(self,m):
        header = ''
        for key in m:
            if key == 'corrected': continue
            header += key + ' & '
        print header[:-2]
        for i in range(len(m.values()[0])):
            s = ''
            for key in m:
                if key == 'corrected': continue
                if type(m[key][i]) is float:
                    s += '{0:+.2f} & '.format(m[key][i])
                else:
                    s += '{0} & '.format(m[key][i])
            s= s[:-2]
            s+='\\\\'
            print s 

    def create_multigraph(self,m,x='fluence',yy=['fit'],name='mgResults',title='',xtitle='Fluence / 10^{15} p/cm^{2}',ytitle='#sigma / #mum'):
        grs = {}
        title = '{title};{xtitle};{ytitle}'.format(title=title,xtitle=xtitle,ytitle=ytitle)
        mg = ROOT.TMultiGraph(name,title)
        for y in yy:
            g = self.create_graph(m,x=x,y=y,name='g_'+y,title=y)
            mg.Add(g)
            grs[y]=g
            i=yy.index(y)
            g.SetLineColor(i+1)
            g.SetMarkerStyle(i+21)
            g.SetFillColor(0)
            g.SetFillStyle(0)
            g.SetMarkerColor(i+1)
        return mg,grs


    def create_graph(self,m,x='fluence',y='fit',name = 'gResults',title=None):
        if x not in m:
            raise Exception('Cannot find %s in %s'%(x,m.keys()))
        if y not in m:
            raise Exception('Cannot find %s in %s'%(y,m.keys()))
        x = m[x]
        y = m[y]
        gr  = ROOT.TGraph(len(x),np.array(x),np.array(y))
        gr.SetName(name)
        if not title:
            title = name
        gr.SetTitle(title)
        return gr

    def get_combined_results(self,t='Normal',diamond='PW205B',corrected=True,min_bias=1000,polarity=1,max_bias=0):
        m1 = self.create_histo_results(t=t,diamond=diamond,corrected=corrected,min_bias=min_bias,polarity=polarity,max_bias=max_bias)
        m2 = self.create_fwhm_results (t=t,diamond=diamond,corrected=corrected,min_bias=min_bias,polarity=polarity,max_bias=max_bias)
        m3 = self.create_single_gaus_results(t=t,diamond=diamond,corrected=corrected,min_bias=min_bias,polarity=polarity,max_bias=max_bias)
        m4 = self.create_fixed_double_gaus_results(t=t,diamond=diamond,corrected=corrected,min_bias=min_bias,polarity=polarity,max_bias=max_bias)
        print 'm1',m1.keys()
        m1['Mean_{Histo}']=m1['mean']
        m1['RMS_{Histo}'] =m1['rms']
        m1['#sigma_{FWHM}'] =m2['fit']
        m1['#sigma_{G}'  ] =m3['fit']
        m1['#sigma_{DG1}' ] =m4['fit1']
        m1['#sigma_{DG2}' ] =m4['fit2']
        for k in ['corrected','mean','rms']:
            m1.pop(k)
        self.create_latex_table(m1)
        return self.create_multigraph(m1,yy=['RMS_{Histo}','#sigma_{G}','#sigma_{FWHM}','#sigma_{DG1}','#sigma_{DG2}'])

    def create_histo_results(self,t='Normal',diamond='PW205B',corrected=True,min_bias=1000,polarity=1,max_bias=0):
        pars = ['Mean','RMS']
        method='Histo'
        m =  self.create_Resolution_histo(t=t,method=method,diamond=diamond,corrected=corrected,pars=pars,min_bias=min_bias,polarity=polarity,max_bias=max_bias)
        self.create_latex_table(m)
        print
        return m

    def create_fwhm_results(self,t='Normal',diamond='PW205B',corrected=True,min_bias=1000,polarity=1,max_bias=0):
        m =  self.create_Resolution_histo(t=t,method='FWHM',diamond=diamond,corrected=corrected,pars=['mean','fit'],min_bias=min_bias,polarity=polarity,max_bias=max_bias)
        self.create_latex_table(m)
        print
        return m

    def create_fixed_double_gaus_results(self,t='Normal',diamond='PW205B',corrected=True,min_bias=1000,polarity=1,max_bias=0):
        pars = ['mean','fit1','fit2']
        m =  self.create_Resolution_histo(t=t,method='FixedDoubleGaus',diamond=diamond,corrected=corrected,pars=pars,min_bias=min_bias,polarity=polarity,max_bias=max_bias)
        self.create_latex_table(m)
        return m
        grs={}
        for p in pars:
            gr = self.create_graph(m,x='fluence',y=p,name='gFixedDoubleGaus_{p}'.format(p=p),title='Fit Parameter: '+p)
            grs[p]=gr
        print
        mg = ROOT.TMultiGraph('mgFixedDoubleGaus','FixedDoubleGaus;Fluence / #upoint 10^{15} p/cm^2; Value / #mum')
        index =0
        for g in grs.values():
            g.SetLineColor(index+1)
            g.SetMarkerStyle(21+index)
            g.SetFillStyle(0)
            g.SetFillColor(0)
            mg.Add(g)
            index+=1
        c = ROOT.TCanvas('cFixedDoubleGaus','Fixed Double Gaus',1000,1000)
        mg.Draw('APL')
        leg = c.BuildLegend()
        leg.SetFillColor(0)
        return m,grs,mg,c

    def create_single_gaus_results(self,t='Normal',diamond='PW205B',corrected=True,min_bias=1000,polarity=1,max_bias=0):
        m =  self.create_Resolution_histo(t=t,method='singlegaus',diamond=diamond,corrected=corrected,pars=['mean','fit'],min_bias=min_bias,polarity=polarity,max_bias=max_bias)
        self.create_latex_table(m)
        print
        return m

    def create_histo_results(self,t='Normal',diamond='PW205B',corrected=True,min_bias=1000,polarity=1,max_bias=0):
        m =  self.create_Resolution_histo(t=t,method='histo',diamond=diamond,corrected=corrected,pars=['mean','rms'],min_bias=min_bias,polarity=polarity,max_bias=max_bias)
        self.create_latex_table(m)
        print
        return m

if __name__ == "__main__":
    full_path = os.path.realpath(__file__)
    directory = os.path.dirname(full_path)
    resTable = ResidualTable('%s/config/' % directory)

