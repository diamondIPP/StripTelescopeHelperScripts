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
		file.write('\\begin{tabular}{\n')
		file.write('\tS[table-alignment = left, table-format = 5.0]\n')
		file.write('\tS[table-number-alignment = center, table-format = -4.0, retain-explicit-plus]\n')
		file.write('\tS\n')
		file.write('\tS[table-number-alignment = center, table-format = 4.1]\n')
		file.write('}\n')
		file.write('\t\\toprule\n')
		file.write('\t{Run} & {Voltage (\\si{\\volt})} & {Noise (ADC Counts)} & {Pulse Height Mean (ADC Counts)} \\\\\n')
		file.write('\t\\midrule\n')
		for run in results :
			file.write('\t%5d & %5s & %5.1f & %6.1f \\\\\n' % (
				run,
				results[run]['Voltage'],
				results[run]['Noise'],
				results[run]['PulseHeight']))
		file.write('\t\\bottomrule\n')
		file.write('\\end{tabular}')
