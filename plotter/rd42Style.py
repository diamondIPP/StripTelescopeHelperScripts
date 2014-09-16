#! /usr/bin/python
import ROOT
from array import array


def rd42Style() :
	rd42Style = ROOT.TStyle('rd42Style','RD42 Style')

	# canvas
	rd42Style.SetCanvasBorderMode(0)
	rd42Style.SetCanvasColor(ROOT.kWhite)
	rd42Style.SetCanvasDefH(600)
	rd42Style.SetCanvasDefW(600)
	rd42Style.SetCanvasDefX(0)
	rd42Style.SetCanvasDefY(0)

	# pad
#	rd42Style.SetPadBorderMode(0)
#	# rd42Style.SetPadBorderSize(Width_t size = 1)
#	rd42Style.SetPadColor(ROOT.kWhite)
#	rd42Style.SetPadGridX(False)
#	rd42Style.SetPadGridY(False)
#	rd42Style.SetGridColor(0)
#	rd42Style.SetGridStyle(3)
#	rd42Style.SetGridWidth(1)

	# frame
	rd42Style.SetFrameBorderMode(0)
	rd42Style.SetFrameBorderSize(1)
	rd42Style.SetFrameFillColor(0)
	rd42Style.SetFrameFillStyle(0)
	rd42Style.SetFrameLineColor(1)
	rd42Style.SetFrameLineStyle(1)
	rd42Style.SetFrameLineWidth(1)

	# histo
##	rd42Style.SetHistFillColor(63)
#	# rd42Style.SetHistFillStyle(0)
#	rd42Style.SetHistLineColor(1)
#	rd42Style.SetHistLineStyle(0)
#	rd42Style.SetHistLineWidth(1)
#	# rd42Style.SetLegoInnerR(Float_t rad = 0.5)
#	# rd42Style.SetNumberContours(Int_t number = 20)
#
#	rd42Style.SetEndErrorSize(2)
##	rd42Style.SetErrorMarker(20)
#	#rd42Style.SetErrorX(0.)
#	
#	rd42Style.SetMarkerStyle(20)
#	rd42Style.SetMarkerSize(1.2)
#
#	# fit/function
##	rd42Style.SetOptFit(1)
	rd42Style.SetOptFit(0)
#	rd42Style.SetFitFormat('5.4g')
	rd42Style.SetFuncColor(3)
#	rd42Style.SetFuncStyle(1)
#	rd42Style.SetFuncWidth(1)
#
#	# date
#	rd42Style.SetOptDate(0)
#	# rd42Style.SetDateX(Float_t x = 0.01)
#	# rd42Style.SetDateY(Float_t y = 0.01)

	# statistics box
#	rd42Style.SetOptFile(0)
	rd42Style.SetOptStat(0)  # To display the mean and RMS:   SetOptStat('mr')
	rd42Style.SetStatColor(ROOT.kWhite)
	rd42Style.SetStatFont(42)
	rd42Style.SetStatFontSize(0.025)
	rd42Style.SetStatTextColor(1)
#	rd42Style.SetStatFormat('6.4g')
	rd42Style.SetStatBorderSize(0)
#	rd42Style.SetStatH(0.1)
#	rd42Style.SetStatW(0.15)
	rd42Style.SetStatStyle(1001)
	rd42Style.SetStatX(0.9)
	rd42Style.SetStatY(0.9)

	# margins
	rd42Style.SetPadTopMargin   (0.04)
	rd42Style.SetPadBottomMargin(0.14)
	rd42Style.SetPadLeftMargin  (0.14)
	rd42Style.SetPadRightMargin (0.04)

	# global title
	rd42Style.SetOptTitle(0)
	rd42Style.SetTitleFont(42)
	rd42Style.SetTitleColor(1)
#	rd42Style.SetTitleTextColor(1)
	rd42Style.SetTitleFillColor(10)
#	rd42Style.SetTitleFontSize(0.05)
#	# rd42Style.SetTitleH(0)  # Set the height of the title box
#	# rd42Style.SetTitleW(0)  # Set the width of the title box
#	# rd42Style.SetTitleX(0)  # Set the position of the title box
#	# rd42Style.SetTitleY(0.985)  # Set the position of the title box
#	# rd42Style.SetTitleStyle(Style_t style = 1001)
#	# rd42Style.SetTitleBorderSize(2)
#
#	# axis titles
#	rd42Style.SetTitleColor(1, 'XYZ')
	rd42Style.SetTitleFont(42, 'XYZ')
	rd42Style.SetTitleSize(0.046, 'XYZ')
#	rd42Style.SetTitleXSize(0.02)  # Another way to set the size?
#	rd42Style.SetTitleYSize(0.02)
#	rd42Style.SetTitleXOffset(1.25)
#	rd42Style.SetTitleYOffset(1.25)
	rd42Style.SetTitleOffset(1.5, 'XYZ')  # Another way to set the Offset
#
#	# axis labels
#	rd42Style.SetLabelColor(1, 'XYZ')
	rd42Style.SetLabelFont(42, 'XYZ')
	rd42Style.SetLabelOffset(0.012, 'XYZ')
	rd42Style.SetLabelSize(0.04, 'XYZ')
#
#	# axis
#	rd42Style.SetAxisColor(1, 'XYZ')
#	rd42Style.SetStripDecimals(ROOT.kTRUE)
#	rd42Style.SetTickLength(0.03, 'XYZ')
#	rd42Style.SetNdivisions(510, 'XYZ')
	rd42Style.SetPadTickX(1)   # To get tick marks on the opposite side of the frame
	rd42Style.SetPadTickY(1)
#
#	# Change for log plots:
#	rd42Style.SetOptLogx(0)
#	rd42Style.SetOptLogy(0)
#	rd42Style.SetOptLogz(0)
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
