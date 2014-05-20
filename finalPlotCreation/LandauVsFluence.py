import ConfigParser
import ROOT
from ROOT import TCanvas
import utilities

class LandauVsFluence():
    def __init__(self,config=None):
        self.plots ={}
        self.canvas = None
        self.config = config

        self.set_runnos()
        self.set_conversions()
        self.set_irradiations()
        pass
    def set_runnos(self):
        self.rundes = {}
        self.runnos = []
        if not self.config:
            self.runnos = [172080]
            return
        runs = sorted([int(i) for i in self.config.options('Runs')])
        for x in runs:
            run = self.config.get('Runs','%d'%x).split()
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
        
    def create_plot(self):
        self.plots ={}
        self.normPlots={}
        c1 = TCanvas()
        title = ''
        if self.config and self.config.has_option('Plot','Title'):
            title = self.config.get('Plot','Title')

        hs = ROOT.THStack("hs",title);
        
        for runno in self.runnos:
            if self.config:
                name = self.config.get('Main','histoName')
            else:
                name = 'hDiaTranspAnaPulseHeightOf2HighestIn10Strips'

            plot = utilities.get_plot(config,runno,self.rundes[runno],name)
            if plot == 0:
                print 'cannot find plot for %s'%runno
                continue
            plot.SetName(str(plot.GetName)+'%s'%runno)
            newPlot = utilities.convert_x_to_electrons(plot,self.get_conversion(runno))
            if self.config and self.config.has_option('Plot','XTitle'):
                newPlot.GetXaxis().SetTitle(self.config.get('Plot','XTitle'))
            if self.config and self.config.has_option('Plot','YTitle'):
                newPlot.GetYaxis().SetTitle(self.config.get('Plot','YTitle'))
            if self.config and self.config.has_option('Plot','LegendTitle'):
                irr = self.get_irradiation(runno)
                newPlot.SetTitle(self.config.get('Plot','LegendTitle') + '#Phi = %.2e p/cm^{2}'%irr )
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
            self.normPlots[runno]=  normPlot
            hs.Add(newPlot)
        hs.Draw('nostack')
        if self.config and self.config.has_option('Plot','XTitle'):
                hs.GetXaxis().SetTitle(self.config.get('Plot','XTitle'))
        if self.config and self.config.has_option('Plot','YTitle'):
                hs.GetYaxis().SetTitle(self.config.get('Plot','YTitle'))
        hs.Draw('nostack')
        c1.Update()
        leg = c1.BuildLegend()
        leg.SetFillColor(ROOT.kWhite)
        c1.Update()
        self.canvas = c1
        fileName = 'PW205B_irradiation'
        c1.SaveAs('%s.png'%fileName)

        c1.SaveAs('%s.pdf'%fileName)
                


        

if __name__ == "__main__":

    config = ConfigParser.ConfigParser()
    config.read('config.cfg')


    landau = LandauVsFluence(config)
    landau.create_plot()
