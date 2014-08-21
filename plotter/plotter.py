#! /usr/bin/python
import ROOT
import sys
import os
import ConfigParser
from rd42Style import rd42Style


class plotter(object) :

	def __init__(self, config, path, run_no) :
		self.config = config
		self.run_no = run_no
		if not path.endswith('/') : path += '/'
		self.path = path + self.run_no + '/'
		rd42Style()


	def plot(self, histo_type) :
		canvas = ROOT.TCanvas('canvas', 'canvas')
		rd42Style()
		histo = self.get_histo(histo_type)
		canvas.cd()
		histo.Draw()
		histo.GetXaxis().SetTitle(self.config.get(histo_type, 'xTitle'))
		histo.GetYaxis().SetTitle(self.config.get(histo_type, 'yTitle'))
		self.draw_rd42Line()
		canvas.Update()
		raw_input('ok?')
		canvas.Print('%s.pdf' % self.config.get(histo_type, 'histo_name'))


	def get_histo(self, histo_type) :
		file_path  = self.path + self.config.get(histo_type, 'root_file')
		histo_name = self.config.get(histo_type, 'histo_name')
#		histo_file = ROOT.TFile('histograms.root', 'READ')
#		histo_file = ROOT.TFile('cDiaTranspAnaPulseHeightOf2HighestIn10Strips.root', 'READ')
		histo_file = ROOT.TFile(file_path, 'READ')
		histo = histo_file.Get('c%s' % histo_name).GetPrimitive('h%s' % histo_name)
		if not self.config.getboolean(histo_type, 'fit') :
			histo.GetFunction('Fitfcn_h%s' % histo_name).SetBit(ROOT.TF1.kNotDraw)
		histo.GetFunction('fMeanCalculationArea').SetBit(ROOT.TF1.kNotDraw)
		return histo


	def draw_rd42Line(self) :
		latex = ROOT.TLatex()
		latex.SetNDC()
		latex.SetTextFont(62)
		latex.SetTextSize(0.04)
		latex.SetTextAlign(13)
		latex.DrawLatex(0.15, 0.93, 'RD42')


if __name__ == '__main__' :
	args = sys.argv
	run_no = -1

	if ('--help' in args) or ('-h' in args) :
		print 'usage: ..'
		sys.exit(1)

	if ('-r' in args) :
		run_no = args[args.index('-r')+1]

	if ('-c' in args) and (args.index('-c')+1 < len(args)) and (not args[args.index('-c')+1].startswith('-')) :
		config_file = args[args.index('-c')+1]
	else :
		config_file = '%s/config.cfg' % os.path.dirname(os.path.realpath(__file__))
	config = ConfigParser.ConfigParser()
	config.read(config_file)
	pl = plotter(config, './', run_no)
	pl.plot('PulseHeight')
#	pl.plot('Noise')

##	name = 'DiaTranspAnaPulseHeightOf2HighestIn10Strips'
##	file = ROOT.TFile('c%s.root' % name, 'READ')
##	#TCanvas *can = (TCanvas*)file->Get('cDiaTranspAnaPulseHeightOf2HighestIn10Strips')
##	#TH1F* histo = (TH1F*)can->GetPrimitive('hDiaTranspAnaPulseHeightOf2HighestIn10Strips')
##	canvas = file.Get('c%s' % name)
##	histo = canvas.GetPrimitive('h%s' % name)
##	#TH1F* histo = (TH1F*)can->GetPrimitive('hDiaTranspAnaPulseHeightOf2HighestIn10Strips')
##	canvas = ROOT.TCanvas('bla', 'bla', 600, 600)
##	histo.GetFunction('Fitfcn_h%s' % name).SetBit(ROOT.TF1.kNotDraw)
##	histo.GetFunction('fMeanCalculationArea').SetBit(ROOT.TF1.kNotDraw)
##	#histo->GetMaximum()
##	#histo->SetMaximum(1.4*5.21000000000000000e+02)
##	#histo->GetMaximum()
##	canvas.SetLeftMargin(0.12)
##	canvas.SetRightMargin(0.04)
##	canvas.SetTopMargin(0.04)
##	canvas.SetBottomMargin(0.12)
##	ROOT.gPad.SetTicks(1,1)
##	canvas.cd()
##	histo.Draw()
##	ROOT.gStyle.SetOptTitle(0)
##	ROOT.gStyle.SetOptStat(0)
##	ROOT.gStyle.SetOptFit(0)
##	histo.SetXTitle('ADC Counts')
##	histo.SetYTitle('Events')
##	histo.GetXaxis().SetTitleOffset(1.25)
##	histo.GetYaxis().SetTitleOffset(1.25)
##	histo.GetXaxis().SetTitleSize(0.046)
##	histo.GetYaxis().SetTitleSize(0.046)
##	histo.GetXaxis().SetLabelSize(0.04)
##	histo.GetYaxis().SetLabelSize(0.04)
##	histo.GetXaxis().SetLabelOffset(0.012)
##	histo.GetYaxis().SetLabelOffset(0.012)
##	histo.Draw()
##	canvas.Print('%s.pdf' % name)
##	raw_input('ok?')
##	raw_input('ok?')
