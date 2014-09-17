import os, sys
import helper
from plotter import plotter
import tables


class results(object) :

	def __init__(self, config_file, path, output_path) :
		self.config_file = config_file
		if not path.endswith('/') : path += '/'
		self.path = path
		if not output_path.endswith('/') : output_path += '/'
		self.output_path = output_path
		helper.mkdir(self.output_path)


	def get_results(self, runs) :
		'''get plots and results for a list of runs'''

		plots = ['FidCut', 'PulseHeight', 'Noise']
		results = {}
		for run in runs :
			results[run] = {}
			for plot in plots :
				pl = plotter(self.config_file, self.path, self.output_path, run, plot)
				results[run][plot] = pl.plot()
		tables.make_NoisePulseHeightTable(self.output_path, results)


if __name__ == '__main__' :
	args = sys.argv
	path = './'
	output_path = 'results/'

	if ('--help' in args) or ('-h' in args) :
		print 'usage: ..'
		sys.exit(1)

	if ('-i' in args) :
		path = args[args.index('-i')+1]

	if ('-c' in args) and (args.index('-c')+1 < len(args)) and (not args[args.index('-c')+1].startswith('-')) :
		config_file = args[args.index('-c')+1]
	else :
		config_file = '%s/config.cfg' % os.path.dirname(os.path.realpath(__file__))

	if ('-o' in args) :
		output_path = args[args.index('-o')+1]

	res = results(config_file, path, output_path)
	res.get_results([17100, 17101])