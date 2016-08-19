#! /usr/bin/python

import sys
import ROOT


def draw_map(path) :
	file = ROOT.TFile.Open(path, 'read')
	tree = file.Get('pedestalTree')
	histo_name = 'BiggestHit_Dia'
	histo = ROOT.TH1F(histo_name, histo_name, 128, 0.5, 128.5)
	ped_histo_name = 'PedestalVsStip_Dia'
	ped_histo = ROOT.TH2F(ped_histo_name, ped_histo_name, 128, 0.5, 128.5, 2000, 0., 2000.)

	for event in tree :
		if event.eventNumber%50000 == 0 and event.eventNumber != 0 :
			print '[status] processed %d events' % event.eventNumber
		index = 0
		DiaADCs   = event.DiaADC
		Pedestals = event.diaPedestalMeanCMN
		Noises    = event.diaPedestalSigmaCMN
		CMN       = event.commonModeNoise
		for i in range(len(DiaADCs)) :
			if DiaADCs[i]-Pedestals[i]-CMN > DiaADCs[index]-Pedestals[index]-CMN :
				index = i
			raw      = DiaADCs[i]
			pedestal = Pedestals[i]
			sigma    = Noises[i]
			if raw-CMN <= pedestal + 5*sigma :
				ped_histo.Fill(i+1, raw-CMN)
		histo.Fill(index+1)
	canvas = ROOT.TCanvas(histo_name, histo_name)
	canvas.cd()
	histo.Draw()
	canvas.SaveAs('%s.root' % histo_name)
	canvas = ROOT.TCanvas(ped_histo_name, ped_histo_name)
	canvas.cd()
	ped_histo.Draw()
	canvas.SaveAs('%s.root' % ped_histo_name)


if __name__ == '__main__' :
	args = sys.argv

	if '-p' in args :
		ped_path = str(args[args.index('-p')+1])
	else :
		print 'usage: pedestalPlots.py -b -p <PEDESTALTREE>'
		sys.exit(1)
	draw_map(ped_path)
