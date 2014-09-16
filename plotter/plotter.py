#! /usr/bin/python
import ROOT
import sys
import os
import ConfigParser
from rd42Style import rd42Style
import helper


class plotter(object) :

	def __init__(self, config, path, run_no, histo_type) :
		self.config = config
		self.run_no = run_no
		self.histo_type = histo_type
		if not path.endswith('/') : path += '/'
		self.path = path + self.run_no + '/'
		rd42Style()

		for key, value in self.config.items(histo_type) :
			setattr(self, key, value)
		self.file_path = self.path + self.root_file


	def plot(self) :
		rd42Style()
		if self.histo_type == 'PulseHeight' :
			ROOT.gStyle.SetOptStat('m')
		if self.histo_type == 'Noise' :
			ROOT.gStyle.SetOptFit(01111)
#		ROOT.gStyle.SetDrawOption('colz')
#		ROOT.gStyle.SetCanvasDefW(1200)
		canvas = ROOT.TCanvas(self.histo_name, 'canvas')
		histo = self.get_histo()
		canvas.cd()
		histo.Draw(self.draw_opt)
		histo.GetXaxis().SetTitle(self.xTitle)
		histo.GetYaxis().SetTitle(self.yTitle)
		self.draw_rd42Line()
		canvas.UseCurrentStyle()
		if histo.GetListOfFunctions().FindObject('palette') == None :
			histo.SetMaximum(1.4 * histo.GetMaximum())
		else :
#			canvas.SetWindowSize(1200, 600)
			canvas.SetRightMargin(canvas.GetRightMargin() + 0.08)
			pal = histo.GetListOfFunctions().FindObject('palette')
			pal_offset = 0.012
			pal.SetX1NDC(1. - canvas.GetRightMargin() + pal_offset)
			pal.SetX2NDC(1. - canvas.GetRightMargin() + pal_offset + 0.82*histo.GetZaxis().GetTickLength())
			pal.SetY1NDC(canvas.GetBottomMargin())
			pal.SetY2NDC(1. - canvas.GetTopMargin())
		if self.histo_type == 'FidCut' :
			fid_cut = self.get_fidCut()
			fid_cut.SetLineColor(ROOT.kRed)
#			fid_cut.Dump()
			canvas.cd()
			fid_cut.Draw('same')
		canvas.Update()
#		ROOT.gPad.Update()
#		canvas.Dump()
		raw_input('ok?')
		canvas.Print('%s.pdf' % self.histo_name)


	def get_histo(self) :
		histo_file = helper.open_rootFile(self.file_path, 'READ')
#		print   histo_file.Get('%s%s' % (self.canvas_prefix, self.histo_name)).ls()
		histo = histo_file.Get('%s%s' % (self.canvas_prefix, self.histo_name)).GetPrimitive('%s%s%s' % (self.histo_prefix, self.histo_name, self.histo_suffix)).Clone()

		# remove functions
		if not eval(self.fit) :
			histo.GetFunction('Fitfcn_%s%s' % (self.histo_prefix, self.histo_name)).SetBit(ROOT.TF1.kNotDraw)
		if self.histo_type == 'PulseHeight' :
			histo.GetFunction('fMeanCalculationArea').SetBit(ROOT.TF1.kNotDraw)
		return histo


	def get_fidCut(self) :
		histo_file = helper.open_rootFile(self.file_path, 'READ')
		fid_cut = histo_file.Get('%s%s' % (self.canvas_prefix, self.histo_name)).GetPrimitive('fidCut_0').Clone()
		return fid_cut		


	def draw_rd42Line(self) :
		latex = ROOT.TLatex()
		latex.SetNDC()
		latex.SetTextFont(62)
		latex.SetTextSize(0.04)
		latex.SetTextAlign(13)
		print ROOT.gStyle.GetPadLeftMargin()
		x_pos = ROOT.gStyle.GetPadLeftMargin() + 0.03
		y_pos = 1. - ROOT.gStyle.GetPadTopMargin() - 0.03
		latex.DrawLatex(x_pos, y_pos, 'RD42')


if __name__ == '__main__' :
	args = sys.argv
	run_no = -1
	path = './'

	if ('--help' in args) or ('-h' in args) :
		print 'usage: ..'
		sys.exit(1)

	if ('-r' in args) :
		run_no = args[args.index('-r')+1]

	if ('-i' in args) :
		path = args[args.index('-i')+1]

	if ('-c' in args) and (args.index('-c')+1 < len(args)) and (not args[args.index('-c')+1].startswith('-')) :
		config_file = args[args.index('-c')+1]
	else :
		config_file = '%s/config.cfg' % os.path.dirname(os.path.realpath(__file__))
	config = ConfigParser.ConfigParser()
	config.optionxform = str # case sensitive options
	config.read(config_file)


#	cfg = parse.samples(config_file)
#
#	print config_file
#	print cfg['root_file']
#
#	print [plot.fit for plot in cfg]
#	print cfg['FidCut'].draw_opt
#
#	sys.exit(0)

	plots = ['FidCut', 'PulseHeight', 'Noise']
	for plot in plots :
#		if plot != 'FidCut' : continue
#		if plot != 'PulseHeight' : continue
		if plot != 'Noise' : continue
		pl = plotter(config, path, run_no, plot)
		pl.plot()

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
