#! /usr/bin/python
import ROOT
from array import array
import ConfigParser
import os


def rd42Style() :
	rd42Style = parse_styleSettings('rd42Style.cfg', 'rd42Style','RD42 Style')

	# PostScript output
	rd42Style.SetPaperSize(15., 15.)
#
#	# colors
	rd42Style.SetPalette(1)
	stops = [0.00, 0.34, 0.61, 0.84, 1.00]
	red   = [0.00, 0.00, 0.87, 1.00, 0.51]
	green = [0.00, 0.81, 1.00, 0.20, 0.00]
	blue  = [0.51, 1.00, 0.12, 0.00, 0.00]
	s = array('d', stops)
	r = array('d', red)
	g = array('d', green)
	b = array('d', blue)
	ncontours = 999
	npoints = len(s)
	ROOT.TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
	rd42Style.SetNumberContours(ncontours)

	# text
#	rd42Style.SetTextAlign(12)

#
#	# postscript options:
#	#rd42Style.SetPaperSize(20.,20.)
##	rd42Style.SetLineScalePS(Float_t scale = 3)
##	rd42Style.SetLineStyleString(Int_t i, const char* text)
##	rd42Style.SetHeaderPS(const char* header)
##	rd42Style.SetTitlePS(const char* pstitle)
#
##	rd42Style.SetBarOffset(Float_t baroff = 0.5)
##	rd42Style.SetBarWidth(Float_t barwidth = 0.5)
##	rd42Style.SetPaintTextFormat(const char* format = 'g')
##	rd42Style.SetPalette(Int_t ncolors = 0, Int_t* colors = 0)
##	rd42Style.SetTimeOffset(Double_t toffset)
##	rd42Style.SetHistMinimumZero(kTRUE)

	rd42Style.cd()


def parse_styleSettings(config_file, style_name = 'style', style_title = 'style') :
	if not os.path.isfile(config_file) :
		print '[WARNING] %s does not exist! Returning default root style..' % config_file
		return ROOT.gStyle
	style = ROOT.TStyle(style_name, style_title)
	config = ConfigParser.ConfigParser()
	config.optionxform = str # case sensitive options
	config.read(config_file)
	for section in config.sections() :
		for key, value_str in config.items(section) :
			value = eval(value_str)
			if type(value) is not tuple :
				getattr(style, 'Set%s' % key)(value)
			else :
				getattr(style, 'Set%s' % key)(*value)
	return style
