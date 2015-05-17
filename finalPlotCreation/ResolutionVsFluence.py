import ConfigParser
import ROOT
from ROOT import TCanvas
import utilities

class ResolutionVsFluence():
    def __init__(self,config=None,mode='positive'):
        self.plots ={}
        self.canvas = None
        self.config = config
        self.mode = mode

        self.set_runnos()
        self.set_conversions()
        self.set_irradiations()
        pass
    def set_mode(self,mode):
        self.mode = mode
        self.set_runnos()
        self.set_conversions()
        self.set_irradiations()

    def set_runnos(self):
        self.rundes = {}
        self.runnos = []
        if not self.config:
            self.runnos = [172080]
            return
        if self.mode != 'negative':
            key = 'RunsResolutionSingle'
        else:
            key = 'RunsResolutionSingle2'
        runs = sorted([int(i) for i in self.config.options(key)])
        for x in runs:
            run = self.config.get(key,'%d'%x).split()
            if len(run) == 1:
                rundes = '0'
            else:
                rundes = run[1]
            runno = int(run[0])
            self.rundes[runno] = rundes
            self.runnos.append(runno)
        print 'runnos: ',self.runnos
        print self.rundes

    def set_conversions(self):
        self.conversions={}
        for run in self.runnos:
            runno = '%d'%run
            runno = runno[:3]
            if self.config:
                if self.config.has_option('Conversion',runno):
                    conv = self.config.getfloat('Conversion',runno)
                elif self.config.has_option('Conversion','default'):
                    conv = self.config.getfloat('Conversion','default')
                else:
                    conv = 7.6
            else:
                conv = 7.6
            self.conversions[runno] = conv
        print 'conversions',self.conversions
    def set_irradiations(self):
        pass
    def get_irradiation(self,runno):

        runno = '%d'%runno
        runno = runno[:3]
        if self.config.has_option('Irradiation',runno):
            return self.config.getfloat('Irradiation',runno)
        return -1




    def get_conversion(self,runno):
        runno = '%d'%runno
        runno = runno[:3]
        return    self.conversions[runno]/100.
        
    def create_plot(self,mode='ResolutionSingle'):
        self.plots ={}
        self.normPlots={}
        ROOT.gStyle.SetOptStat('e')
        c1 = TCanvas()
        c1.SetObjectStat(False)
        title = ''
        if self.config and self.config.has_option('PlotResolutionSingle','Title'):
            title = self.config.get('PlotResolutionSingle','Title')

        hs = ROOT.THStack("hs",title);
        hs_norm = ROOT.THStack("hs_norm",title);
        
        for runno in self.runnos:
            if self.config:
                name = self.config.get('MainResolutionSingle','histoName')
            else:
                name = 'hDiaTranspAnaPulseHeightOf2HighestIn10Strips'

            section = 'Main'+mode
            plot = utilities.get_plot(config,section,runno,self.rundes[runno],name)
            if plot == 0:
                print 'cannot find plot for %s'%runno
                continue
            plot.SetName(str(plot.GetName)+'%s'%runno)
            newPlot = plot
            newPlot.SetObjectStat(False)
            if self.config and self.config.has_option('PlotResolutionSingle','XTitle'):
                newPlot.GetXaxis().SetTitle(self.config.get('PlotResolutionSingle','XTitle'))
            if self.config and self.config.has_option('PlotResolutionSingle','YTitle'):
                newPlot.GetYaxis().SetTitle(self.config.get('PlotResolutionSingle','YTitle'))
            if self.config and self.config.has_option('PlotResolutionSingle','LegendTitle'):
                irr = self.get_irradiation(runno)
                newPlot.SetTitle(self.config.get('PlotResolutionSingle','LegendTitle') + '#Phi = %.2e p/cm^{2}'%irr )
            for key in newPlot.GetListOfFunctions():
                print key
                if 'stats' in key.GetName() :
                    stats = newPlot.GetFunction(key.GetName())
                    stats.Delete()
            self.plots[runno] = newPlot
            c1.cd()
            index = self.runnos.index(runno)
            color = utilities.get_color(index)
            newPlot.SetLineColor(color)
            self.plots[runno] = newPlot
            norm = newPlot.GetBinContent(newPlot.GetMaximumBin())
            newPlot.Scale(1./norm)
            normPlot = newPlot.DrawNormalized("")
            print normPlot
            normPlot = normPlot.Clone()
            normPlot.SetObjectStat(False)
            self.normPlots[runno]=  normPlot
            hs.Add(newPlot)
            hs_norm.Add(normPlot)

        stacks = [hs,hs_norm]
        for stack in stacks:
            c1.Clear()
            c1.Update()
            c1.SetObjectStat(False)
            c1.Clear()
            stack.SetObjectStat(False)
            stack.Draw('nostack')
            print stack,type(stack)
            if stack:
                axis = stack.GetXaxis()
                if axis:
                    if self.config and self.config.has_option('PlotResolutionSingle','XTitle'):
                        axis.SetTitle(self.config.get('PlotResolutionSingle','XTitle'))
                    if self.config and self.config.has_option('PlotResolutionSingle','XMin'):
                        if self.config.has_option('PlotResolutionSingle','XMax'):
                            minX = self.config.getfloat('PlotResolutionSingle','XMin')
                            maxX = self.config.getfloat('PlotResolutionSingle','XMax')
                            axis.SetRangeUser(minX,maxX)

                if self.config and self.config.has_option('PlotResolutionSingle','YTitle'):
                    axis = stack.GetYaxis()
                    if axis:
                        axis.SetTitle(self.config.get('PlotResolutionSingle','YTitle'))
            stack.Draw('nostack')
            c1.Update()
            leg = c1.BuildLegend()
            leg.SetFillColor(ROOT.kWhite)
            c1.Update()
            self.canvas = c1
            fileName = 'PW205B_resolution_%d'%stacks.index(stack)
            c1.SaveAs('%s_%s.png'%(fileName,self.mode))
            c1.SaveAs('%s_%s.pdf'%(fileName,self.mode))
            c1.SaveAs('%s_%s.root'%(fileName,self.mode))
                


        

if __name__ == "__main__":

    config = ConfigParser.ConfigParser()
    config.read('config.cfg')


    res = ResolutionVsFluence(config)
    res.create_plot()
    res.set_mode('negative')
    res.create_plot()
