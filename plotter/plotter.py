#! /usr/bin/python
import ROOT
import sys
import os
import ConfigParser
from rd42Style import rd42Style
import helper
import roundNumbers as rn
import numpy as np


class plotter(object) :

	def __init__(self, config_file, path, output_path, run_no, position, histo_type, run_config_file = '', event_number = 0) :
		self.config_file = config_file
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
		self.event_number = event_number
		rd42Style()

		for key, value in self.config.items(histo_type) :
			value = value.replace('EVENTNUMBER', '%d' % self.event_number)
			setattr(self, key, value)
		if not hasattr(self, 'name') :
			self.name = self.histo_name
		if not hasattr(self, 'variable') :
			self.variable = histo_type
		if not hasattr(self, 'nstrips') :
			self.nstrips = 0
		else :
			self.nstrips = int(self.nstrips)
		if hasattr(self, 'output_dir') :
			self.output_path += self.output_dir
			if not self.output_path.endswith('/') : self.output_path += '/'
		helper.mkdir(self.output_path)
		if hasattr(self, 'rebin') :
			self.rebin = int(self.rebin)
		self.root_file = self.root_file.replace('RUNNUMBER', '.%d' % self.run_no)
		self.file_path = self.path + self.root_file
		self.rand = ROOT.TRandom3(0)

		self.run_config_file = run_config_file
		if self.run_config_file != '' :
			self.run_config = ConfigParser.ConfigParser()
			self.run_config.optionxform = str # case sensitive options
			self.run_config.read(run_config_file)


	def plot(self) :
		print '[status] plotting %s..' % self.name
		rd42Style()
		if self.histo_type == 'PulseHeight' :
			ROOT.gStyle.SetOptStat('m')
		if self.histo_type == 'Noise' :
			ROOT.gStyle.SetOptFit(01111)
#		ROOT.gStyle.SetDrawOption('colz')
#		ROOT.gStyle.SetCanvasDefW(1200)
		canvas = ROOT.TCanvas('%s_%s' % (self.name, self.rand.Integer(10000)), 'canvas')
		histo = self.get_histo()
		if 'PulseHeight_Cluster1-' in self.histo_type :
			for i in range(1, self.nstrips) :
				if self.position != '' :
					path_tmp = self.path.rstrip('%d/%s/' % (self.run_no, self.position))
				else :
					path_tmp = self.path.rstrip('%d/' % self.run_no)
				pl = plotter(self.config_file, path_tmp, self.output_path.rstrip('%d' % self.run_no), self.run_no, self.position, 'PulseHeight_Cluster%d_%s' % (i, self.histo_type.split('_')[-1]), self.run_config_file)
				histo_tmp = pl.get_histo()
				histo.Add(histo_tmp)
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
		if 'Alignment_Plane2_YPred_DeltaX' in self.histo_type :
			if 'Post' in self.histo_type :
				self.save_TH2histo2table(histo, path = '%s%s.dat' % (self.output_path, self.name), rebinx = 3, rebiny = 5, xmin = 3000., ymin = -15., nxbins = 30, nybins = 96, sfx = 0.001, sfy = 1.)
			else :
				self.save_TH2histo2table(histo, path = '%s%s.dat' % (self.output_path, self.name), rebinx = 4, rebiny = 2, xmin = 3000., ymin = -260., nxbins = 32, nybins = 146, sfx = 0.001, sfy = 1.)
			return
		if 'Alignment_Plane2_XPred_DeltaY' in self.histo_type :
			if 'Post' in self.histo_type :
				self.save_TH2histo2table(histo, path = '%s%s.dat' % (self.output_path, self.name), rebinx = 4, rebiny = 13, xmin = 3000., ymin = -6.2, nxbins = 30, nybins = 37, sfx = 0.001, sfy = 1.)
			else :
				self.save_TH2histo2table(histo, path = '%s%s.dat' % (self.output_path, self.name), rebinx = 4, rebiny = 2, xmin = 3000., ymin = -540., nxbins = 32, nybins = 148, sfx = 0.001, sfy = 1.)
			return
		if self.histo_type == 'StripMeanPedestal_Dia' :
			profile = histo.ProfileX('profile', 1, -1, 'os')
			nbins = profile.GetNbinsX()
			sigma_histo = ROOT.TH1F('ped_sigma', 'ped_sigma', nbins, profile.GetBinLowEdge(1), profile.GetXaxis().GetBinUpEdge(nbins))
			for ibin in range(1, nbins+1) :
				projection = histo.ProjectionY('tmp%d' % ibin, ibin, ibin, 'o')
				sigma_histo.SetBinContent(ibin, projection.GetRMS())
				sigma_histo.SetBinError  (ibin, projection.GetRMSError())
			print profile.GetEntries()
			print profile.GetBinLowEdge(1)
			print profile.GetBinContent(1)
			print profile.GetBinError(1)
			histos = self.add_statistics(profile)
			print histos['data'].GetEntries()
			print histos['data'].GetBinLowEdge(1)
			print histos['data'].GetBinContent(1)
			print histos['data'].GetBinError(1)
			histos['sigma'] = sigma_histo
			processes = ['data', 'sigma', 'stat']
			print profile
			self.save_histo2table(histos = histos, processes = processes, path = '%s%s.dat' % (self.output_path, self.name), var = self.variable, bin_width = False)
			# sigma spectra
			histos = self.add_statistics(sigma_histo)
			processes = ['data', 'stat']
			self.save_histo2table(histos = histos, processes = processes, path = '%s%s.dat' % (self.output_path, 'StripPedestalSigma_Dia'), var = 'StripPedestalSigma', bin_width = False)
			return
		if self.histo_type == 'PulseHeight_ClusterSize' or self.histo_type == 'Eta_Dia_Area' :
			processes = ['data', 'stat']
			slice_name = self.histo_type
			if self.histo_type == 'Eta_Dia_Area' :
				slice_name = 'Eta_Area'
			slices = self.get_histoSlices(histo, path = self.output_path, slice_name = slice_name)
			for projection in slices :
				if '-' in projection :
					self.nstrips = int(projection.lstrip('1-'))
				else :
					self.nstrips = int(projection)
				print self.nstrips
				histos = self.add_statistics(slices[projection], slices[projection].GetName())
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
			fit = histo.GetListOfFunctions().FindObject('histofitx')
			histos = self.add_statistics(histo, fit = fit)
			processes.append('stat')
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
					if process == 'stat' and bin == 6 :
						file.write('\t%e' % (histos[process].GetBinContent(bin)*1e15))
					else :
						file.write('\t%f' % histos[process].GetBinContent(bin))
				for process in processes :
					if process == 'stat' and bin == 6 :
						file.write('\t%e' % (histos[process].GetBinError(bin)*1e15))
					else :
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
		print 'x bin width:', histo.GetXaxis().GetBinWidth(1)
		print 'y bin width:', histo.GetYaxis().GetBinWidth(1)
		print histo.Integral()
		print 'max:', histo.GetBinContent(histo.GetMaximumBin())
		histo.Rebin2D(rebinx, rebiny)
		nbinsx = histo.GetNbinsX()
		nbinsy = histo.GetNbinsY()
		print 'n x bins:', nbinsx
		print 'n y bins:', nbinsy
		print 'x bin min', histo.GetXaxis().FindBin(xmin)
		print 'y bin min', histo.GetYaxis().FindBin(ymin)
		print 'x bin width:', histo.GetXaxis().GetBinWidth(1)
		print 'y bin width:', histo.GetYaxis().GetBinWidth(1)
		xminbin = histo.GetXaxis().FindBin(xmin)
		xmaxbin = xminbin + nxbins
		yminbin = histo.GetYaxis().FindBin(ymin)
		ymaxbin = yminbin + nybins
		print 'xbins: %d .. %d' % (xminbin, xmaxbin)
		print 'ybins: %d .. %d' % (yminbin, ymaxbin)
		print 'x: %f .. %f' % (histo.GetXaxis().GetBinLowEdge(xminbin), histo.GetXaxis().GetBinUpEdge(xmaxbin))
		print 'y: %f .. %f' % (histo.GetYaxis().GetBinLowEdge(yminbin), histo.GetYaxis().GetBinUpEdge(ymaxbin))
		print '%d x %d = %d' % (xmaxbin-xminbin, ymaxbin-yminbin, (xmaxbin-xminbin)*(ymaxbin-yminbin))
		print 'max:', histo.GetBinContent(histo.GetMaximumBin())
		if xmaxbin > nbinsx or ymaxbin > nbinsy :
			print '[ERROR] Check bin settings!'
			sys.exit(1)

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


	def save_graph2table(self, graph, path) :
		nentries = graph.GetN()
		print nentries
		x_tmp = np.zeros(1, dtype=float)
		y_tmp = np.zeros(1, dtype=float)
		x = []
		y = []
		for i in range(nentries) :
			graph.GetPoint(i, x_tmp, y_tmp)
			x.append(x_tmp[0])
			y.append(y_tmp[0])

		with open(path, 'w') as file :
			file.write('x, y\n')
			for i in range(nentries) :
				file.write('%f, %f\n' % (x[i], y[i]))


	def get_histoSlices(self, histo, path, slice_name = 'PulseHeight_ClusterSize', slice_name_suffix = 'Dia') :
		nybins = histo.GetNbinsY()
		profiles = {}
		for i in range(1, nybins+1) :
			cluster_size = histo.GetYaxis().GetBinCenter(i)
			profiles['%.0f' % cluster_size] = histo.ProjectionX('%s_%.0f_%s' % (slice_name, cluster_size, slice_name_suffix), i, i, 'o')
			if cluster_size > 1 :
				profiles['1-%.0f' % cluster_size] = histo.ProjectionX('%s_1-%.0f_%s' % (slice_name, cluster_size, slice_name_suffix), histo.GetYaxis().FindBin(1), i, 'o')
		return profiles


	def add_statistics(self, histo, pkl_name = None, fit = None) :
		print 'histo %f .. %f with %d bins' % (histo.GetBinLowEdge(1), histo.GetXaxis().GetBinUpEdge(histo.GetNbinsX()), histo.GetNbinsX())
		if pkl_name == None : pkl_name = self.name
		histos = {}
		histos['data'] = histo
		res = {}
		res['mean'    ] = histo.GetMean()
		res['mean_err'] = histo.GetMeanError()
		print 'Mean: %f' % res['mean']
		histos['stat'] = ROOT.TH1F('%s_stat' % pkl_name, 'stat', histo.GetNbinsX(), 0., 1.)
		histos['stat'].SetBinContent(1, self.run_no    )
		histos['stat'].SetBinError  (1, 0              )
		histos['stat'].SetBinContent(2, res['mean'    ])
		histos['stat'].SetBinError  (2, res['mean_err'])
		histos['stat'].SetBinContent(3, histo.GetRMS     ())
		histos['stat'].SetBinError  (3, histo.GetRMSError())
		histos['stat'].SetBinContent(4, histo.Integral())
		histos['stat'].SetBinContent(7, self.nstrips)
		if self.run_config_file != '' and self.run_config.has_section('%d' % self.run_no) and self.det_type == 'Dia' :
			histos['stat'].SetBinContent(5, eval(self.run_config.get('%d' % self.run_no, 'calibration'    )))
			histos['stat'].SetBinError  (5, eval(self.run_config.get('%d' % self.run_no, 'calibration_err')))
			histos['stat'].SetBinContent(6, eval(self.run_config.get('%d' % self.run_no, 'fluence'    ))/1e15)
			histos['stat'].SetBinError  (6, eval(self.run_config.get('%d' % self.run_no, 'fluence_err'))/1e15)
		if fit != None :
			for i in [0, 1, 2] :
				histos['stat'].SetBinContent(i+10, fit.GetParameter(i))
				histos['stat'].SetBinError  (i+10, fit.GetParError(i))
			res['sigma'    ] = fit.GetParameter(2)
			res['sigma_err'] = fit.GetParError(2)
			mean  = (fit.GetParameter(1), fit.GetParError(1))
			sigma = (fit.GetParameter(2), fit.GetParError(2))
			print 'Mean : %s +- %s' % rn.get_roundedNumber(*mean )
			print 'Sigma: %s +- %s' % rn.get_roundedNumber(*sigma)
		helper.save_object(res, '%s%s_stat.pkl' % (self.output_path, pkl_name))
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
		if hasattr(self, 'rebin') :
			histo.Rebin(self.rebin)
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


def usage() :
	print 'usage: plotter.py -r <RUN_NO> -i <DATA_PATH> - p <POSITION> -c <CONFIG_FILE> -o <OUTPUT_PATH>, --runconfig <RUN_CONFIG>'
	sys.exit(1)


if __name__ == '__main__' :
	args = sys.argv
	run_no = -1
	path = './'
	position = ''

	if ('--help' in args) or ('-h' in args) :
		usage()

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

	if ('--plots' in args) :
		plots = []
		plots_ind = args.index('--plots')
		it = 1
		while plots_ind + it < len(args) and not args[plots_ind+it].startswith('-') :
			plots.append(args[plots_ind+it])
			it += 1
	else :
		usage()

	for plot in plots :
		if plot == 'Event_Dia' :
			for event in [168221, 169021, 169149, 169631, 173675, 173970, 175220, 175586, 176049, 176054, 176274, 176539, 177067, 195755, 225010, 419220, 455990, 465430] :
				pl = plotter(config_file, path, output_path, run_no, position, plot, runconfig, event)
				pl.plot()
			continue
		pl = plotter(config_file, path, output_path, run_no, position, plot, runconfig)
		pl.plot()
