#! /usr/bin/python
import ROOT
import sys
import os
import ConfigParser
from rd42Style import rd42Style
import helper
import roundNumbers as rn


class plotter(object) :

	def __init__(self, config_file, path, output_path, run_no, position, histo_type, run_config_file = '') :
		self.config = ConfigParser.ConfigParser()
		self.config.optionxform = str # case sensitive options
		self.config.read(config_file)
		self.run_no = int(run_no)
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
		if not hasattr(self, 'name') :
			self.name = self.histo_name
		if not hasattr(self, 'variable') :
			self.variable = histo_type
		self.root_file = self.root_file.replace('RUNNUMBER', '.%d' % self.run_no)
		self.nstrips = 0
		self.file_path = self.path + self.root_file
		self.rand = ROOT.TRandom3(0)

		self.run_config_file = run_config_file
		if self.run_config_file != '' :
			self.run_config = ConfigParser.ConfigParser()
			self.run_config.optionxform = str # case sensitive options
			self.run_config.read(run_config_file)


	def plot(self) :
		rd42Style()
		if self.histo_type == 'PulseHeight' :
			ROOT.gStyle.SetOptStat('m')
		if self.histo_type == 'Noise' :
			ROOT.gStyle.SetOptFit(01111)
#		ROOT.gStyle.SetDrawOption('colz')
#		ROOT.gStyle.SetCanvasDefW(1200)
		canvas = ROOT.TCanvas('%s_%s' % (self.name, self.rand.Integer(10000)), 'canvas')
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
		if self.histo_type == 'FidCut' or self.histo_type == 'TrackPos' :
			self.save_TH2histo2table(histo, path = '%s%s.dat' % (self.output_path, self.name), rebinx = 4, rebiny = 4, xmin = 48., ymin = 48., sfx = 0.05, sfy = 0.05)
			fid_cut = self.get_fidCut()
			fid_cut.SetLineColor(ROOT.kRed)
#			fid_cut.Dump()
			canvas.cd()
			fid_cut.Draw('same')
		if self.histo_type == 'PulseHeight_ClusterSize' :
			processes = ['data', 'stat']
			slices = self.get_histoSlices(histo, path = self.output_path)
			for projection in slices :
				if '-' in projection :
					self.nstrips = int(projection.lstrip('1-'))
				else :
					self.nstrips = int(projection)
				print self.nstrips
				histos = self.add_statistics(slices[projection])
				self.save_histo2table(histos = histos, processes = processes, path = '%s%s.dat' % (self.output_path, slices[projection].GetName()), var = self.variable, bin_width = False)
			return
		canvas.Update()
#		ROOT.gPad.Update()
#		canvas.Dump()
#		raw_input('ok?')
		processes = ['data',]
		if self.return_value == 'mean' :
			histos = self.add_statistics(histo)
			processes.append('stat')
		elif self.return_value == 'sigma' :
			histos = {}
			histos['data'] = histo
			fit = histo.GetListOfFunctions().FindObject('histofitx')
			histos['fit'] = ROOT.TH1F('%s_fit' % self.histo_type, 'fit', histo.GetNbinsX(), 0., 1.)
			histos['fit'].SetBinContent(1, self.run_no)
			histos['fit'].SetBinError  (1, 0          )
			for i in [0, 1, 2] :
				histos['fit'].SetBinContent(i+2, fit.GetParameter(i))
				histos['fit'].SetBinError  (i+2  , fit.GetParError(i))
			if self.run_config_file != '' and self.run_config.has_section('%d' % self.run_no) :
				histos['fit'].SetBinContent(5, eval(self.run_config.get('%d' % self.run_no, 'calibration'    )))
				histos['fit'].SetBinError  (5, eval(self.run_config.get('%d' % self.run_no, 'calibration_err')))
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
		if self.histo_type != 'FidCut' and self.histo_type != 'TrackPos' :
			self.save_histo2table(histos = histos, processes = processes, path = '%s%s.dat' % (self.output_path, self.name), var = self.variable, bin_width = False)
		canvas.Print('%s%s.pdf' % (self.output_path, self.name))
		canvas.Print('%s%s.tex' % (self.output_path, self.name))
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


	def save_TH2histo2table(self, histo, path, rebinx = 1, rebiny = 1, xmin = 0., ymin = 0., nxbins = 85, nybins = 85, sfx = 1., sfy = 1.) :
		nbinsx = histo.GetNbinsX()
		nbinsy = histo.GetNbinsY()
		print 'n x bins:', nbinsx
		print 'n y bins:', nbinsy

		histo.Rebin2D(rebinx, rebiny)
		print 'x bin min', histo.GetXaxis().FindBin(xmin)
		print 'y bin min', histo.GetYaxis().FindBin(ymin)
		xminbin = histo.GetXaxis().FindBin(xmin)
		xmaxbin = xminbin + nxbins
		yminbin = histo.GetYaxis().FindBin(ymin)
		ymaxbin = yminbin + nybins
		print '%d x %d = %d' % (xmaxbin-xminbin, ymaxbin-yminbin, (xmaxbin-xminbin)*(ymaxbin-yminbin))

		switch = True
		matrix = False

		with open(path, 'w') as file :
			file.write('%s %s data\n' % (self.xTitle, self.yTitle))
			for ybin in range(yminbin, ymaxbin+1) :
				ylow = histo.GetYaxis().GetBinLowEdge(ybin)
				yup  = histo.GetYaxis().GetBinUpEdge(ybin)
				if matrix :
					ylow = histo.GetYaxis().GetBinCenter(ybin)
				for xbin in range(xminbin, xmaxbin+1) :
					xlow = histo.GetXaxis().GetBinLowEdge(xbin)
					xup  = histo.GetXaxis().GetBinUpEdge(xbin)
					if matrix :
						xlow = histo.GetXaxis().GetBinCenter(xbin)
					content = histo.GetBinContent(xbin, ybin)
					if switch :
						if content != 0. and (content > 17. or True) or True :
							file.write('%f %f %f\n' % (xlow * sfx, ylow * sfy, content))
						else :
							file.write('%f %f %s\n' % (xlow * sfx, ylow * sfy, 'nan'))
					else :
						if content != 0. :
							file.write('%f %f %f\n' % (xlow * sfx, ylow * sfy, content))
							file.write('%f %f %f\n' % (xlow * sfx, yup  * sfy, content))
							file.write('%f %f %f\n' % (xup  * sfx, yup  * sfy, content))
							file.write('%f %f %f\n' % (xup  * sfx, ylow * sfy, content))


	def get_histoSlices(self, histo, path) :
		nybins = histo.GetNbinsY()
		profiles = {}
		for i in range(1, nybins+1) :
			cluster_size = histo.GetYaxis().GetBinCenter(i)
			profiles['%.0f' % cluster_size] = histo.ProjectionX('PulseHeight_ClusterSize_%.0f' % cluster_size, i, i, 'o')
			if cluster_size > 1 :
				profiles['1-%.0f' % cluster_size] = histo.ProjectionX('PulseHeight_ClusterSize_1-%.0f' % cluster_size, histo.GetYaxis().FindBin(1), i, 'o')
		return profiles


	def add_statistics(self, histo) :
		histos = {}
		histos['data'] = histo
		res = {}
		res['mean'    ] = histo.GetMean()
		res['mean_err'] = histo.GetMeanError()
		print 'Mean: %f' % res['mean']
		helper.save_object(res, '%s%s_mean.pkl' % (self.output_path, self.name))
		histos['stat'] = ROOT.TH1F('%s_stat' % self.histo_type, 'stat', histo.GetNbinsX(), 0., 1.)
		histos['stat'].SetBinContent(1, self.run_no    )
		histos['stat'].SetBinError  (1, 0              )
		histos['stat'].SetBinContent(2, res['mean'    ])
		histos['stat'].SetBinError  (2, res['mean_err'])
		histos['stat'].SetBinContent(3, histo.GetRMS     ())
		histos['stat'].SetBinError  (3, histo.GetRMSError())
		histos['stat'].SetBinContent(4, histo.Integral())
		histos['stat'].SetBinContent(7, self.nstrips)
		if self.run_config_file != '' and self.run_config.has_section('%d' % self.run_no) :
			histos['stat'].SetBinContent(5, eval(self.run_config.get('%d' % self.run_no, 'calibration'    )))
			histos['stat'].SetBinError  (5, eval(self.run_config.get('%d' % self.run_no, 'calibration_err')))
			histos['stat'].SetBinContent(6, eval(self.run_config.get('%d' % self.run_no, 'fluence'    )))
			histos['stat'].SetBinError  (6, eval(self.run_config.get('%d' % self.run_no, 'fluence_err')))
		return histos


	def get_histo(self) :
		histo_file = helper.open_rootFile(self.file_path, 'READ')
		if hasattr(self, 'primitive') :
			primitive = self.primitive
		else :
			primitive = '%s%s%s' % (self.histo_prefix, self.histo_name, self.histo_suffix)
		histo = histo_file.Get('%s%s' % (self.canvas_prefix, self.histo_name)).GetPrimitive(primitive).Clone()

		# remove functions
		if not eval(self.fit) and self.histo_type == 'PulseHeight' :
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
		print 'usage: plotter.py -r <RUN_NO> -i <DATA_PATH> - p <POSITION> -c <CONFIG_FILE> -o <OUTPUT_PATH>, --runconfig <RUN_CONFIG>'
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

	if ('--runconfig' in args) :
		runconfig = args[args.index('--runconfig')+1]
	else :
		runconfig = ''

	plots = ['FidCut', 'PulseHeight', 'Noise']
	plots.append('PulseHeight_BiggestSignalSNRDia')
	plots.append('PulseHeight_BiggestAdjacentSNRDia')
	for plane in range(1, 2) :
		for coord in ['X',] :# 'Y']
			histo_name = 'PulseHeight_BiggestSignalSNRD%d%s'  % (plane, coord)
			plots.append(histo_name)
			histo_name = 'PulseHeight_BiggestAdjacentSNRD%d%s' % (plane, coord)
			plots.append(histo_name)
	nstrips = {}
	for cluster_size in range(1, 11) :
		plot_name = 'PulseHeight_%dStrips' % cluster_size
		plots.append(plot_name)
		nstrips[plot_name] = cluster_size
	plots.append('PulseHeight_ClusterSize')
	plots.append('ClusterSize')
	for plot in plots :
#		if plot != 'FidCut' : continue
#		if plot != 'PulseHeight' : continue
#		if plot != 'Noise' : continue
		pl = plotter(config_file, path, output_path, run_no, position, plot, runconfig)
		if plot in nstrips :
			pl.nstrips = nstrips[plot]
		pl.plot()
