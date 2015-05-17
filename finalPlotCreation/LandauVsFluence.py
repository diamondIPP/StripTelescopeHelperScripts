import ConfigParser
import ROOT
from ROOT import TCanvas
import utilities
import argparse

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
        key = 'RunsLandauSingle'
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
        
    def create_plot(self,mode='LandauSingle'):
        self.plots ={}
        self.normPlots={}
        c1 = TCanvas()
        title = ''
        if self.config and self.config.has_option('PlotLandauSingle','Title'):
            title = self.config.get('PlotLandauSingle','Title')

        hs = ROOT.THStack("hs",title);
        hs_norm = ROOT.THStack("hs_norm",title);
        
        for runno in self.runnos:
            if self.config:
                try:
                    name = self.config.get('MainLandauSingle','histoName')
                except Exception as e:
                    print self.config.options('MainLandauSingle')
                    raise e
            else:
                name = 'hDiaTranspAnaPulseHeightOf2HighestIn10Strips'

            section = 'Main'+mode
            plot = utilities.get_plot(config,section,runno,self.rundes[runno],name)
            if plot == 0:
                print 'cannot find plot for %s'%runno
                continue
            plot.SetName(str(plot.GetName)+'%s'%runno)
            newPlot = utilities.convert_x_to_electrons(plot,self.get_conversion(runno))
            if self.config and self.config.has_option('PlotLandauSingle','XTitle'):
                newPlot.GetXaxis().SetTitle(self.config.get('PlotLandauSingle','XTitle'))
            if self.config and self.config.has_option('PlotLandauSingle','YTitle'):
                newPlot.GetYaxis().SetTitle(self.config.get('PlotLandauSingle','YTitle'))
            if self.config and self.config.has_option('PlotLandauSingle','LegendTitle'):
                irr = self.get_irradiation(runno)
                newPlot.SetTitle(self.config.get('PlotLandauSingle','LegendTitle') + '#Phi = %.2e p/cm^{2}'%irr )
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
            hs_norm.Add(normPlot)

        stacks = [hs,hs_norm]
        for stack in stacks:
            c1.Clear()
            stack.Draw('nostack')
            if self.config and self.config.has_option('PlotLandauSingle','XTitle'):
                    stack.GetXaxis().SetTitle(self.config.get('PlotLandauSingle','XTitle'))
            if self.config and self.config.has_option('PlotLandauSingle','YTitle'):
                stack.GetYaxis().SetTitle(self.config.get('PlotLandauSingle','YTitle'))
            stack.Draw('nostack')
            c1.Update()
            leg = c1.BuildLegend()
            leg.SetFillColor(ROOT.kWhite)
            c1.Update()
            self.canvas = c1
            dia_name = self.config.get('Main','diamond')
            outputdir = './output/'
            fileName = outputdir+'%s_irradiation_%d'%(dia_name,stacks.index(stack))

            c1.SaveAs('%s.png'%(fileName))
            c1.SaveAs('%s.pdf'%(fileName))
            c1.SaveAs('%s.root'%(fileName))


        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--diamond', help='name of diamond which should be analyzed',default='PW205B')
    args = parser.parse_args()
    config = ConfigParser.ConfigParser()
    config.read('config.cfg')
    config_file = 'config_%s.cfg'%args.diamond
    print config_file
    config.read(config_file)

    landau = LandauVsFluence(config)
    landau.create_plot()
