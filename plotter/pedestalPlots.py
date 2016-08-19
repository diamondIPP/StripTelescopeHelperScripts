#! /usr/bin/python

import sys
import ROOT


def draw_map(path, output_path) :
	if not output_path.endswith('/') : output_path += '/'
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
	canvas.SaveAs('%s%s.root' % (output_path, histo_name))
	canvas = ROOT.TCanvas(ped_histo_name, ped_histo_name)
	canvas.cd()
	ped_histo.Draw()
	canvas.SaveAs('%s%s.root' % (output_path, ped_histo_name))


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
		print 'usage: pedestalPlots.py -b -p <PEDESTALTREE> -o <OUTPUTPATH> --pos <POSITION>'
		sys.exit(1)
	draw_map(ped_path, output_path)
