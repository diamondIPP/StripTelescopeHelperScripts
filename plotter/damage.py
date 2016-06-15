#! /usr/bin/python
import ROOT
import sys
import os
import numpy as np
import ConfigParser
import math
#from rd42Style import rd42Style
import helper
#import roundNumbers as rn


class result :
	def __init__(self, run) :
		self.run = run
		self.polarity = 0.
		self.voltage = 0.
		self.calibration = 0.
		self.calibration_err = 0.
		self.pulse_height = 0.
		self.pulse_height_err = 0.
		self.noise = 0.
		self.noise_err = 0.
		self.fluence = 0.
		self.fluence_err = 0.


	@property
	def ccd(self) :
		ccd = self.pulse_height * 100. / self.calibration / 36.
		return ccd


	@property
	def ccd_err(self) :
		ccd_err = self.ccd * math.sqrt(self.pulse_height_err**2/self.pulse_height**2 + self.calibration_err**2/self.calibration**2)
		return ccd_err


class irr_results :
	def __init__(self, path, input_path, run_config) :
		if not path.endswith('/') : path += '/'
		self.path = path
		helper.mkdir(self.path)
		if not input_path.endswith('/') : input_path += '/'
		self.input_path = input_path
		self.runs = self.read_runs(run_config)


	def read_runs(self, path) :
		'''reads selections from config file'''

		print '[status] reading selections from %s..' % path
		if not os.path.isfile(path) :
			print '[ERROR] %s does not exist!' % path
			sys.exit(1)
		run_file = ConfigParser.ConfigParser()
		run_file.optionxform = str # case sensitive options
		run_file.read(path)

		runs = {}
		for run_number in run_file.sections() :
			run = result(run = run_number)
			for res in run_file.options(run_number) :
				if not hasattr(run, res) :
					print '[ERROR] run instance has no attribute %s! Check your selections config file!' % res
					sys.exit(1)
				setattr(run, res, eval(run_file.get(run_number, res)))
			runs[run_number] = run
			ph_file = '%s%s/DiaTranspAnaPulseHeightOf2HighestIn10Strips_mean.pkl' % (self.input_path, run_number)
#			pulse_height = helper.load_object('Mar23/%s/DiaTranspAnaPulseHeightOf2HighestIn10Strips_mean.pkl' % run_number)
			pulse_height = helper.load_object(ph_file)
			run.pulse_height     = pulse_height['mean']
#			run.pulse_height_err = pulse_height['mean_err']
			run.pulse_height_err = run.noise

		return runs


	def write_table(self) :
		with open('%sdamage.dat' % self.path, 'w') as file :
			file.write('  run, polarity, voltage, calibration, calibration_err, pulse_height, pulse_height_err, fluence, fluence_err,        ccd,  ccd_err\n')
#			for run in ['16001', '16005', '16303', '16307', '17101', '17104', '17208', '17211'] :
			for run in sorted(self.runs.keys()) :
				if   self.runs[run].voltage > 0. : polarity = 'positive'
				elif self.runs[run].voltage < 0. : polarity = 'negative'
				file.write('%s, %s, %+7d, %11.2f, %15.2f, %12f, %16f, %7.3f, %11.3f, %f, %f\n' % (
					run,
					polarity,
					self.runs[run].voltage,
					self.runs[run].calibration,
					self.runs[run].calibration_err,
					self.runs[run].pulse_height,
					self.runs[run].pulse_height_err,
					self.runs[run].fluence,
					self.runs[run].fluence_err,
					self.get_ccd(run)[0],
					self.get_ccd(run)[1]))


	def get_ccd(self, run) :
		ccd     = self.runs[run].ccd
		ccd_err = self.runs[run].ccd_err
		return (ccd, ccd_err)


if __name__ == '__main__' :
	args = sys.argv
	run_no = -1
	path = 'output/'
	position = ''

	help_message = 'usage: damage.py -i <RESULT_PATH> -c <CONFIG_FILE> -o <OUTPUT_PATH>'

	if ('--help' in args) or ('-h' in args) :
		print help_message
		sys.exit(1)

	if ('-i' in args) :
		input_path = args[args.index('-i')+1]
	else :
		print help_message
		sys.exit(1)

	if ('-o' in args) :
		path = args[args.index('-o')+1]

	if ('-c' in args) :
		config = args[args.index('-c')+1]
	else :
		print help_message
		sys.exit(1)

	irrad = irr_results(path, input_path, config)
	irrad.write_table()
