#! /usr/bin/python

import os, sys
import ROOT
import numpy as np
import helper


class eventDisplay :
	'''draws strip signals of individual events'''


	def __init__(self, ped_path, path = 'output') :
#		self.raw_path     = raw_path
		self.ped_path     = ped_path
#		self.raw_file     = ROOT.TFile.Open(self.raw_path, 'READ')
		self.ped_file     = ROOT.TFile.Open(self.ped_path, 'READ')
#		self.raw_tree     = self.raw_file.Get('rawTree')
		self.ped_tree     = self.ped_file.Get('pedestalTree')
#		if self.raw_tree.GetEntries() != self.ped_tree.GetEntries() :
#			print '[ERROR] check trees!'
#			sys.exit(1)
#		self.ped_tree.GetListOfFriends().Clear()
#		friend = self.ped_tree.GetListOfFriends().FindObject('rawTree')
#		self.ped_tree.GetListOfFriends().Remove(friend)
		self.nevents = int(self.ped_tree.GetEntries())
		self.path = path
		if not self.path.endswith('/') : self.path += '/'
		helper.mkdir(self.path)


	def make_eventDisplays(self) :
		pkl_path = '%sevent_displays.pkl' % self.path
		if os.path.exists(pkl_path) :
			print '[status] loading %s..' % pkl_path
			histo = helper.load_object(pkl_path)
		else :
			histo = self.scan_events()
			helper.save_object(histo, pkl_path)
		self.draw_events(histo)


	def scan_events(self) :
		histo_name = 'DiaSignalvsChannelvsEvent'
		nevents = 100
		histo = ROOT.TH2F(histo_name, histo_name, 128, 0.5, 128.5, nevents, 0., nevents)
		event_bin = 0
		for i, event in enumerate(self.ped_tree) :
			if event.eventNumber%50000 == 0 and event.eventNumber != 0 :
				print '[status] processed %d events' % event.eventNumber
			if event_bin >= nevents : break

			# load event data
			data = {}
			for leaf in ['eventNumber', 'DiaADC', 'diaPedestalMeanCMN', 'diaPedestalSigmaCMN', 'commonModeNoise'] :
				data[leaf] = self.get_eventData(event, leaf)
			data['signal'] = data['DiaADC'] - data['diaPedestalMeanCMN'] - data['commonModeNoise']

			# check if saturated
			if max(data['DiaADC']) > 4094 :
				continue

			# check if signal
			if max(data['signal']) < 200 : continue

			# only small signals
			if max(data['signal']) > 400. : continue

			# fiducial cut
			if np.argmax(data['signal']) < 20 or np.argmax(data['signal']) > 55 : continue

			# noisy channel
			if data['diaPedestalSigmaCMN'][63] > 15 : continue

			# fill histogram
			print '[status] filling event %d in histogram..' % event.eventNumber
			for channel, signal in enumerate(data['signal']) :
				histo.SetBinContent(channel+1, event_bin+1, data['signal'][channel])
				histo.SetBinError  (channel+1, event_bin+1, data['diaPedestalSigmaCMN'][channel])
			histo.GetYaxis().SetBinLabel(event_bin+1, '%d' % data['eventNumber'])
			event_bin += 1

		# save canvas
		canvas = ROOT.TCanvas('Event', 'Event')
		histo.Draw('pe')
		histo.SaveAs('%sDiaSignalvsChannelEvents.root' % self.path)

		return histo


	def get_eventData(self, event, leaf_name) :
		leaf = getattr(event, leaf_name)
		if isinstance(leaf, float) or isinstance(leaf, long) :
			data = float(leaf)
		else :
			data = np.zeros(len(leaf))
			for i in range(len(leaf)) :
				data[i] = float(leaf[i])
		return data


	def draw_events(self, histo) :
		for event_bin in range(1, histo.GetNbinsY()) :
			event_str = histo.GetYaxis().GetBinLabel(event_bin)
			if event_str == '' : continue
			event_number = int(event_str)
			projection_name = 'DiaSignalvsChannelEvent%d' % event_number
			projection = histo.ProjectionX(projection_name, event_bin, event_bin, 'o')
			canvas = ROOT.TCanvas(projection_name, projection_name)
			canvas.cd()
			projection.Draw('pe')
			canvas.SaveAs('%s%s.root' % (self.path, projection_name))


if __name__ == '__main__' :
	args = sys.argv

	if '-p' in args :
		ped_path = str(args[args.index('-p')+1])
		if '--pos' in args :
			pos = str(args[args.index('--pos')+1])
			if not pos.endswith('/') :
				pos += '/'
		else : pos = ''
		if '-o' in args :
			output_path = str(args[args.index('-o')+1])
		else :
			output_path = '%s/%spedestalAnalysis/root/' % (os.path.dirname(ped_path), pos)
	else :
		print 'usage: eventDisplay.py -b -p <PEDESTALTREE> -o <OUTPUTPATH> --pos <POSITION>'
		sys.exit(1)

	display = eventDisplay(ped_path, output_path)
	display.make_eventDisplays()
