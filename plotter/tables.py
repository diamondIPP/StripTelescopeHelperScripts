#! /usr/bin/python
import helper
import time


def make_NoisePulseHeightTable(path, results) :
	if not path.endswith('/') : path += '/'
	helper.mkdir(path)
	table_name = 'NoisePulseHeightTable.tex'
	print '[status] writing %s' % table_name
	with open(path + table_name, 'w') as file :
		timestamp = time.asctime()
		file.write('%!TEX root = ../../Dissertation.tex\n')
		file.write('\n\n')
		file.write('\\begin{tabular}{l|r|rr}\n')
		file.write('\\hline\\hline\n')
		file.write('Run   & Voltage (V) & Noise (ADC Counts) & Pulse Height Mean (ADC Counts) \\\\\n')
		file.write('\\hline\n')
		for run in results :
			file.write('%5d & %4d & %5.1f & %6.1f \\\\\n' % (
				run,
				-1,
				results[run]['Noise'],
				results[run]['PulseHeight']))
		file.write('\\hline\\hline\n')
		file.write('\\end{tabular}')
