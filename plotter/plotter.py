#! /usr/bin/python
import ROOT
import sys
import os
import ConfigParser
from rd42Style import rd42Style
import helper
import roundNumbers as rn


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
		histos = {}
		histos['data'] = histo
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
			self.save_TH2histo2table(histo, path = '%s%s.dat' % (self.output_path, self.histo_name))
			fid_cut = self.get_fidCut()
			fid_cut.SetLineColor(ROOT.kRed)
#			fid_cut.Dump()
			canvas.cd()
			fid_cut.Draw('same')
		canvas.Update()
#		ROOT.gPad.Update()
#		canvas.Dump()
#		raw_input('ok?')
		processes = ['data',]
		if self.return_value == 'mean' :
			mean = histo.GetMean()
			print 'Mean: %f' % mean
		elif self.return_value == 'sigma' :
			fit = histo.GetListOfFunctions().FindObject('histofitx')
			histos['fit'] = ROOT.TH1F('%s_fit' % self.histo_type, 'fit', histo.GetNbinsX(), 0., 1.)
			for i in [0, 1, 2] :
				histos['fit'].SetBinContent(i+1, fit.GetParameter(i))
				histos['fit'].SetBinError  (i+1  , fit.GetParError(i))
			processes.append('fit')
			mean  = (fit.GetParameter(1), fit.GetParError(1))
			sigma = (fit.GetParameter(2), fit.GetParError(2))
			print 'Mean : %s +- %s' % rn.get_roundedNumber(*mean )
			print 'Sigma: %s +- %s' % rn.get_roundedNumber(*sigma)
			entries = []
			entries.append(('$\\chi^2 / \\ndof$', '{%.0f / %d}' % (fit.GetChisquare(), fit.GetNDF())))
			entries.append(('Mean' , '%s +- %s' % rn.get_roundedNumber(fit.GetParameter(1), fit.GetParError(1))))
			entries.append(('Sigma', '%s +- %s' % rn.get_roundedNumber(fit.GetParameter(2), fit.GetParError(2))))
			print entries
#			ROOT.gStyle.SetOptFit(0)
#			self.draw_statbox(entries)
		if self.histo_type != 'FidCut' :
			self.save_histo2table(histos = histos, processes = processes, path = '%s%s.dat' % (self.output_path, self.histo_name), var = self.histo_type, bin_width = False)
		canvas.Print('%s%s.pdf' % (self.output_path, self.histo_name))
		canvas.Print('%s%s.tex' % (self.output_path, self.histo_name))
		return -1.


	def save_histo2table(self, histos, processes, path, var = 'bincentre', lumi = '', bin_width = True, last_bin = True, asymmErr = False) :
		if lumi != '' :
			lumi_str   = '\t%4.1f' % lumi
			lumi_title = '\tlumi'
		else :
			lumi_str   = ''
			lumi_title = ''
		if asymmErr != False :
			histos_tmp = {}
			for process in asymmErr :
				histos_tmp[process] = histos[process].Clone()
				histos_tmp[process].SetBinErrorOption(ROOT.TH1.kPoisson)
		nbins = histos[processes[0]].GetNbinsX()
		with open(path, 'w') as file :
			file.write('binlow\t%s\t%s\t%s_err' % (var, '\t'.join(processes), '_err\t'.join(processes)))
			if asymmErr != False :
				file.write('\t%s_uerr\t%s_derr' % ('\t_uerr'.join(asymmErr), '_derr\t'.join(asymmErr)))
			if bin_width : file.write('\tbinwidth')
			file.write('%s\n' % lumi_title)
			for bin in range(1, nbins+1) :
				file.write('%f\t%f' % (histos[processes[0]].GetXaxis().GetBinLowEdge(bin), histos[processes[0]].GetXaxis().GetBinCenter(bin)))
				for process in processes :
					file.write('\t%f' % histos[process].GetBinContent(bin))
				for process in processes :
					file.write('\t%f' % histos[process].GetBinError(bin))
				if asymmErr != False :
					for process in asymmErr :
						file.write('\t%f' % histos_tmp[process].GetBinErrorUp(bin))
					for process in asymmErr :
						file.write('\t%f' % histos_tmp[process].GetBinErrorLow(bin))
				if bin_width :
					file.write('\t%f' % histos[processes[0]].GetBinWidth(bin))
				file.write('%s\n' % lumi_str)
			if last_bin :
				file.write('%f\t%f' % (histos[processes[0]].GetXaxis().GetBinUpEdge(nbins), histos[processes[0]].GetXaxis().GetBinCenter(nbins)))
				for process in processes :
					file.write('\t%f' % histos[process].GetBinContent(nbins))
				for process in processes :
					file.write('\t%f' % histos[process].GetBinError(nbins))
				if asymmErr != False :
					for process in asymmErr :
						file.write('\t%f' % histos_tmp[process].GetBinErrorUp(nbins))
					for process in asymmErr :
						file.write('\t%f' % histos_tmp[process].GetBinErrorLow(nbins))
				if bin_width :
					file.write('\t%f' % histos[processes[0]].GetBinWidth(nbins))
				file.write('%s\n' % lumi_str)


	def save_TH2histo2table(self, histo, path) :
		nbinsx = histo.GetNbinsX()
		nbinsy = histo.GetNbinsY()
#		nbinsx = 51
#		nbinsy = 101
		xmin = histo.FindFirstBinAbove(0,1)
		ymin = histo.FindFirstBinAbove(0,2)
		xmax = histo.FindLastBinAbove(0,1)
		ymax = histo.FindLastBinAbove(0,2)
		
		xmin = 180
		xmax = 270
		ymin = 130
		ymax = 270
		
		xmin = 170
		xmax = 270
		ymin = 120
		ymax = 220

#		histo.Rebin2D()
		xmin = 85
		xmax = 150
		ymin = 65
		ymax = 200

#		histo.Rebin2D(3,3)
		xmin = 50
		xmax = 130
		ymin = 40
		ymax = 130

		xmin = 33
		xmax = 133
		ymin = 33
		ymax = 133

		histo.Rebin2D(4,4)
		xmin = 25
		xmax = 110
		ymin = 25
		ymax = 110

#		histo.Rebin2D(2,2)
#		xmin = 25  * 2
#		xmin = 25  * 2
#		xmax = 110 * 2
#		ymin = 25  * 2
#		ymax = 110 * 2
		print '%d x %d = %d' % (xmax-xmin, ymax-ymin, (xmax-xmin)*(ymax-ymin))

		switch = True
		matrix = False

		with open(path, 'w') as file :
			file.write('x y data\n')
			for ybin in range(ymin, ymax+1) :
				ylow = histo.GetYaxis().GetBinLowEdge(ybin)
				yup  = histo.GetYaxis().GetBinUpEdge(ybin)
				if matrix :
					ylow = histo.GetYaxis().GetBinCenter(ybin)
				for xbin in range(xmin, xmax+1) :
					xlow = histo.GetXaxis().GetBinLowEdge(xbin)
					xup  = histo.GetXaxis().GetBinUpEdge(xbin)
					if matrix :
						xlow = histo.GetXaxis().GetBinCenter(xbin)
					content = histo.GetBinContent(xbin, ybin)
					if switch :
						if content != 0. and (content > 17. or True) or True :
							file.write('%f %f %f\n' % (xlow, ylow, content))
						else :
							file.write('%f %f %s\n' % (xlow, ylow, 'nan'))
					else :
						if content != 0. :
							file.write('%f %f %f\n' % (xlow, ylow, content))
							file.write('%f %f %f\n' % (xlow, yup , content))
							file.write('%f %f %f\n' % (xup , yup , content))
							file.write('%f %f %f\n' % (xup , ylow, content))


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


	def draw_statbox(self, entries) :
#		table = '\\begin{tabular}{cc}bla & blup \\\\ \\end{tabular}'
		table = '\\begin{tabular}{\n\tl\n\tS[table-alignment = center, table-format = -1.4(2)]\n}\n'
		for item in entries :
			print item
			table += '\t%-5s & %s \\\\\n' % item
		table += '\\end{tabular}\n'
		print table
		latex = ROOT.TLatex()
		latex.SetNDC()
		latex.SetTextFont(62)
		latex.SetTextSize(0.04)
		latex.SetTextAlign(33)
		x_pos = ROOT.gStyle.GetPadLeftMargin() + 0.5
		y_pos = 1. - ROOT.gStyle.GetPadTopMargin() - 0.03
		
		x_pos = ROOT.gStyle.GetStatX()
		y_pos = ROOT.gStyle.GetStatY()
		latex.DrawLatex(x_pos, y_pos, table)

#		text = ROOT.TText()
#		text.SetNDC()
#		text.DrawText(0.5, 0.5, table)


if __name__ == '__main__' :
	args = sys.argv
	run_no = -1
	path = './'
	position = ''

	if ('--help' in args) or ('-h' in args) :
		print 'usage: plotter.py -r <RUN_NO> -i <DATA_PATH> - p <POSITION> -c <CONFIG_FILE> -o <OUTPUT_PATH>'
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
