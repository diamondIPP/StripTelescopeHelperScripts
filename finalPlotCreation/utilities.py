import ROOT
from ROOT import TCanvas

def get_file(config,runno,rundes):
    print 'get file ',runno,rundes
    path  = '.'
    if config and config.has_option('Main','Path'):
        path = config.get('Main','Path')
    path += '/%d/'%runno
    if any(x in rundes for x in ['left','right']):
        path+='%s/'%rundes
    
    if config and config.has_option('Main','relPath'):
        path += config.get('Main','relPath')+'/'

    if config and config.has_option('Main','fileName'):
        path += config.get('Main','fileName')
    else:
        path += 'histograms.root'
    print path

    f =ROOT.TFile(path)
    return f

def get_color(index):
    return index
    
def get_plot(config,runno,rundes,name):


    newKey = ''
    f = get_file(config,runno,rundes)
    for key in f.GetListOfKeys():
        c = f.FindObjectAny(key.GetName())
        if c == None:
            continue
        if type(c) == ROOT.TCanvas:
            h = c.GetPrimitive(name)
        else:
            h = c
        if type(h) == None:
            continue
        if h == None:
            continue
        if h.GetName()==name:
            return h
    return 0

def convert_x_to_electrons(plot,conversion):
    name = plot.GetName()
    name+='_electrons'
    title = plot.GetTitle()
    title+= ' in electrons'
    newPlot = ROOT.TH1F(name,title,plot.GetNbinsX(),plot.GetXaxis().GetXmin()/conversion,plot.GetXaxis().GetXmax()/conversion)
    for bin in range(0,plot.GetNbinsX()+1):
        content = plot.GetBinContent(bin)
        newPlot.SetBinContent(bin,content)
    newPlot.SetEntries(plot.GetEntries())
    return newPlot

    pass

if __name__ == "__main__":
    name = 'hDiaTranspAnaPulseHeightOf2HighestIn10Strips'
    plot = get_plot(1,name)
    newPlot = convert_x_to_electrons(plot,6.8/100.)
