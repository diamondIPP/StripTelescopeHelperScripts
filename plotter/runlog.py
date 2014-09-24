#! /usr/bin/python

class runlog(object) :

	def __init__(self, log_file) :
		self.log_file = log_file
		self.runs = {}
		self.read_logFile()


	def read_logFile(self) :
		print '[status] reading %s' % self.log_file
		with open(self.log_file, 'r') as file :
			for line in file.readlines() :
				if line[0] == '#' : continue
				splitline = line.split()
				[run, diamonds, voltage] = splitline[:3]
				run = int(run)
#				voltage = float(voltage)
				self.runs[run] = {}
				self.runs[run]['diamonds'] = diamonds
				self.runs[run]['voltage' ] = voltage


	def get_voltage(self, run) :
		if not run in self.runs :
			print '[WARNING] run %s not found!' % run
			return -1.
		else :
			return self.runs[run]['voltage']
