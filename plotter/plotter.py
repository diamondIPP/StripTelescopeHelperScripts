#! /usr/bin/python
import ROOT
import sys
import os
import ConfigParser
from rd42Style import rd42Style
import helper


class plotter(object) :

	def __init__(self, config_file, path, output_path, run_no, position, histo_type) :
		self.config = ConfigParser.ConfigParser()
		self.config.optionxform = str # case sensitive options
		self.config.read(config_file)
		self.run_no = run_no
		self.position = position
		self.histo_type = histo_type
		if not path.endswith('/') : path += '/'
		self.path = '%s%s' % (path, self.run_no)
		if self.position != '' :
			self.path += '/%s/' % self.position
		else : self.path += '/'
		if not output_path.endswith('/') : output_path += '/'
		self.output_path = '%s%s/' % (output_path, self.run_no)
		helper.mkdir(self.output_path)
		rd42Style()

		for key, value in self.config.items(histo_type) :
			setattr(self, key, value)
		self.file_path = self.path + self.root_file
		self.rand = ROOT.TRandom3(0)


	def plot(self) :
		rd42Style()
		if self.histo_type == 'PulseHeight' :
			ROOT.gStyle.SetOptStat('m')
		if self.histo_type == 'Noise' :
			ROOT.gStyle.SetOptFit(01111)
#		ROOT.gStyle.SetDrawOption('colz')
#		ROOT.gStyle.SetCanvasDefW(1200)
		canvas = ROOT.TCanvas('%s_%s' % (self.histo_name, self.rand.Integer(10000)), 'canvas')
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
#		raw_input('ok?')
		canvas.Print('%s%s.pdf' % (self.output_path, self.histo_name))
		canvas.Print('%s%s.tex' % (self.output_path, self.histo_name))
		if self.return_value == 'mean' :
			mean = histo.GetMean()
			print 'Mean: %f' % mean
			return mean
		elif self.return_value == 'sigma' :
			fit = histo.GetListOfFunctions().FindObject('histofitx')
			sigma = fit.GetParameter(2)
			print 'Sigma: %f' % sigma
			return sigma
		else :
			return -1.


	def get_histo(self) :
		histo_file = helper.open_rootFile(self.file_path, 'READ')
		histo = histo_file.Get('%s%s' % (self.canvas_prefix, self.histo_name)).GetPrimitive('%s%s%s' % (self.histo_prefix, self.histo_name, self.histo_suffix)).Clone()

		# remove functions
		if not eval(self.fit) :
			histo.GetFunction('Fitfcn_%s%s' % (self.histo_prefix, self.histo_name)).SetBit(ROOT.TF1.kNotDraw)
		if self.histo_type == 'PulseHeight' :
			histo.GetFunction('fMeanCalculationArea').SetBit(ROOT.TF1.kNotDraw)
		histo.SetDirectory(0)
		histo_file.Close()
		return histo


	def get_fidCut(self) :
		histo_file = helper.open_rootFile(self.file_path, 'READ')
		fid_cut = histo_file.Get('%s%s' % (self.canvas_prefix, self.histo_name)).GetPrimitive('fidCut_0').Clone()
		#fid_cut.SetDirectory(0)
		histo_file.Close()
		return fid_cut		


	def draw_rd42Line(self) :
		latex = ROOT.TLatex()
		latex.SetNDC()
		latex.SetTextFont(62)
		latex.SetTextSize(0.04)
		latex.SetTextAlign(13)
		x_pos = ROOT.gStyle.GetPadLeftMargin() + 0.03
		y_pos = 1. - ROOT.gStyle.GetPadTopMargin() - 0.03
		latex.DrawLatex(x_pos, y_pos, 'RD42')


if __name__ == '__main__' :
	args = sys.argv
	run_no = -1
	path = './'
	position = ''

	if ('--help' in args) or ('-h' in args) :
		print 'usage: ..'
		sys.exit(1)

	if ('-r' in args) :
		run_no = args[args.index('-r')+1]

	if ('-i' in args) :
		path = args[args.index('-i')+1]

	if ('-p' in args) :
		position = args[args.index('-p')+1]

	if ('-c' in args) and (args.index('-c')+1 < len(args)) and (not args[args.index('-c')+1].startswith('-')) :
		config_file = args[args.index('-c')+1]
	else :
		config_file = '%s/config.cfg' % os.path.dirname(os.path.realpath(__file__))

	if ('-o' in args) :
		output_path = args[args.index('-o')+1]
	else :
		output_path = './'

	plots = ['FidCut', 'PulseHeight', 'Noise']
	for plot in plots :
#		if plot != 'FidCut' : continue
#		if plot != 'PulseHeight' : continue
#		if plot != 'Noise' : continue
		pl = plotter(config_file, path, output_path, run_no, position, plot)
		pl.plot()
