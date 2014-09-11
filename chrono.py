# Import python modules
import os, sys, glob
from datetime import datetime as dt
from operator import itemgetter as ig
from matplotlib import pyplot as plt



class chrono:
	_colors = {'red': 'r', 'green': 'g', 'blue': 'b', 'yellow': 'y', 'cyan': 'c', 'magenta': 'm', 'black': 'k', 'white': 'w'}
	_linestyles = {' ': ' ', '-': 'solid', '--': 'dashed', '-.': 'dash_dot', ':': 'dotted'}
	_markers  = {' ': ' ', '.': '.', '_' : '_', 'o': 'o', '*': '*', '+': '+', 'x': 'x', 'square': 's', 'triangle': '^', 'diamond': 'd'}
	_channels =  [1, 2, 3, 4, 5, 6, 7, 8]	
	_months   =  {'Jan.': 1, 'Feb.': 2, 'Mar.': 3, 'Apr.': 4, 'May.': 5, 'Jun.': 6, 'Jul.': 7, 'Aug.': 8, 'Sep.': 9, 'Oct.': 10, 'Nov.': 11, 'Dec.': 12}		
	_anode_cathode_flag = {'anode only': 0, 'cathode only': 1, 'anode cathode both': 2}


	def __init__(self, anode_path_name, cathode_path_name, elec_area, area_unit, plot_style):
		self.anode_path_name = anode_path_name
		self.cathode_path_name = cathode_path_name

		self.process_anode = False
		self.process_cathode = False

		self.elec_area = elec_area
		self.area_unit = area_unit

		self.anode_plot_color = plot_style['anode_plot_color']
		self.anode_line_style = plot_style['anode_line_style']
		self.anode_plot_marker = plot_style['anode_marker']
		self.cathode_plot_color = plot_style['cathode_plot_color']
		self.cathode_line_style = plot_style['cathode_line_style']
		self.cathode_plot_marker = plot_style['cathode_marker']

		self.err_msg = None
		self.channels = []


	# Validating the input directory and files
	def validation(self):		
		if not self.anode_path_name and not self.cathode_path_name:
			self.err_msg = 'Nothing to process. Enter anode and/or folder name\n'
			sys.stderr.write(self.err_msg)
			return False


		if self.anode_path_name:
			if os.path.isdir(self.anode_path_name) == True:
				self.process_anode = True
				pwd = os.getcwd()
				os.chdir(self.anode_path_name)

				try:
					os.mkdir('plots')
				except OSError:
					pass
	
				os.chdir(pwd)
		
			else:
				self.err_msg = 'Only directory path is allowed. Try again!\n'	
				sys.stderr.write(self.err_msg)
				return False


		if self.cathode_path_name:
			if os.path.isdir(self.cathode_path_name) == True:
				self.process_cathode = True
				pwd = os.getcwd()
				os.chdir(self.cathode_path_name)

				try:
					os.mkdir('plots')
				except OSError:
					pass
	
				os.chdir(pwd)
		
			else:
				self.err_msg = 'Only directory path is allowed. Try again!\n'	
				sys.stderr.write(self.err_msg)
				return False

		return True


			
	def process_data(self, file_data):
		self.line_count, self.time = 0, ''

			
		for cnt in range(len(file_data)):
			self.line_count += 1

			if self.line_count == 1:
				try:
					self._months[file_data[cnt][0:4]]
				except KeyError:
					sys.stderr.write('Invalid data on first line of the file')					
				else:
					timestamp = file_data[cnt].split()
					year = timestamp[2]
					month = self._months[timestamp[0]]
					day = timestamp[1].split(',')[0]
					hour =  timestamp[3].split(':')[0]
					minute =  timestamp[3].split(':')[1]
					second =  timestamp[3].split(':')[2]
				
					self.datetime = dt(int(year), int(month), int(day), int(hour), int(minute), int(second))
			
			elif self.file_count == 1 and file_data[cnt][0:6] == 'Time/s':
				for i in range(1, len(file_data[cnt].split(','))):
					self.channels.append(file_data[cnt].split(',')[i][2])


			try:			
				float(file_data[cnt][0:4])
			except ValueError:
				pass
			else:
				self.channel_data_1, self.channel_data_2 = [], []
				self.data_count = self.data_count + 1
 
				line_data = file_data[cnt].split(',')		

				self.time = line_data[0]
			
				for j in range(1, len(line_data)):
					self.channel_data_1.append(float(line_data[j]) * 1.0e6)
					self.channel_data_2.append(float(line_data[j]) * 1.0e6 / float(self.elec_area))

				self.dataset.append((self.datetime, self.time, self.channel_data_1, self.channel_data_2))
		


	# Read all the text files in the directory
	def read_files(self, path_name):
		self.dataset, self.file_count, self.data_count = [], 0, 0

		sys.stdout.write('Entering directory ' + path_name + '...\n')
			
		file_list = glob.glob(os.path.join(path_name, '*.txt'))

		for file_name in file_list:
			try:
				file = open(file_name, 'r')
			except IOError:
				self.err_msg = 'Unable to open ' + file_name + '\n'
				sys.stderr.write(self.err_msg)
			else:
				self.datetime, file_data = '', []

				self.file_count = self.file_count + 1
				
				sys.stdout.write('Processing file ' + file_name + '\n')

				file_data = file.readlines()

				file.close()

				self.process_data(file_data)
				

		sys.stdout.write('A total of ' + str(self.data_count) + ' data points read from ' + str(self.file_count) + ' files\n')
		return self.dataset				


	# Process the files under the directory	
	def process_files(self):
		self.anode_dataset, self.cathode_dataset = [], []
		self.anode_x, self.anode_y1, self.anode_y2 = [], [], []
		self.cathode_x, self.cathode_y1, self.cathode_y2 = [], [], []


		if self.process_anode == True:
			self.anode_dataset = self.read_files(self.anode_path_name)
			self.anode_dataset = sorted(self.anode_dataset, key=ig(0))

			if min(self.anode_dataset[0][2]) < 0 and max(self.anode_dataset[0][2]) > 0:
				self.anode_cathode_flag = self._anode_cathode_flag['anode cathode both']
				for cnt in range(len(self.anode_dataset)):				
					self.cathode_y1.append([])
					self.anode_y1.append([])
					self.cathode_y2.append([])
					self.anode_y2.append([])
			elif min(self.anode_dataset[0][2]) < 0 and max(self.anode_dataset[0][2]) < 0:
				self.anode_cathode_flag = self._anode_cathode_flag['cathode only']
				for cnt in range(len(self.anode_dataset)):				
					self.cathode_y1.append([])
					self.cathode_y2.append([])
			else:
				self.anode_cathode_flag = self._anode_cathode_flag['anode only']
				for cnt in range(len(self.anode_dataset)):
					self.anode_y1.append([])
					self.anode_y2.append([])
				

			for i in range(len(self.anode_dataset)):
				if self.anode_cathode_flag == 0:
					if i == 0:
						self.anode_x.append(float(self.anode_dataset[i][1]) / 3600)
					elif i == 1:
						self.time_diff = float(self.anode_dataset[i][1]) - float(self.anode_dataset[i - 1][1])
						self.anode_x.append(float(self.anode_x[i - 1]) + ( self.time_diff / 3600))
					else:
						self.anode_x.append(float(self.anode_x[i - 1]) + ( self.time_diff / 3600))
				elif self.anode_cathode_flag == 1:
					if i == 0:
						self.cathode_x.append(float(self.anode_dataset[i][1]) / 3600)
					elif i == 1:
						self.time_diff = float(self.anode_dataset[i][1]) - float(self.anode_dataset[i - 1][1])
						self.cathode_x.append(float(self.cathode_x[i - 1]) + ( self.time_diff / 3600))
					else:
						self.cathode_x.append(float(self.cathode_x[i - 1]) + ( self.time_diff / 3600))
				else:
					if i == 0:
						self.anode_x.append(float(self.anode_dataset[i][1]) / 3600)
						self.cathode_x.append(float(self.anode_dataset[i][1]) / 3600)
					elif i == 1:
						self.time_diff = float(self.anode_dataset[i][1]) - float(self.anode_dataset[i - 1][1])
						self.anode_x.append(float(self.anode_x[i - 1]) + ( self.time_diff / 3600))
						self.cathode_x.append(float(self.cathode_x[i - 1]) + ( self.time_diff / 3600))
					else:
						self.anode_x.append(float(self.anode_x[i - 1]) + ( self.time_diff / 3600))
						self.cathode_x.append(float(self.cathode_x[i - 1]) + ( self.time_diff / 3600))

		
				for current in self.anode_dataset[i][2]:
					if current < 0:
						self.cathode_y1[i].append(current)
					else:
						self.anode_y1[i].append(current)


				for current_den in self.anode_dataset[i][3]:
					if current_den < 0:
						self.cathode_y2[i].append(current_den)
					else:	
						self.anode_y2[i].append(current_den)
								

#		if self.process_cathode = True
#			self.cathode_dataset = self.read_files(self.cathode_path_name) 
#			self.cathode_dataset = sorted(self.cathode_dataset, key=ig(1))	

		if self.anode_cathode_flag == 0 or self.anode_cathode_flag == 1:
			self.num_channels = len(self.channels)
		else:
			self.num_channels = len(self.anode_y1[0])				

		for channel_number in range(self.num_channels):
			self.I_T_plot(self.anode_path_name, channel_number)
			self.J_T_plot(self.anode_path_name, channel_number) 

	

	def I_T_plot(self, path_name, channel_number):
		if self.anode_cathode_flag == 0: 
			self.y = []

			for current in self.anode_y1:
				self.y.append(current[channel_number])	
		
			xmax = 1.1 * max(self.anode_x)
			xmin = 1.1 * min(self.anode_x)
			ymax = 1.1 * max(self.y)
			ymin = 0

			plt.clf()
			plt.xlabel('Time (hours)')
			plt.ylabel(r'Current ($\mu$A)')
			plt.axis([xmin, xmax, ymin, ymax])	
			plt.plot(self.anode_x, self.y, color = self.anode_plot_color, linestyle = self._linestyles[self.anode_line_style.lower()], marker = self._markers[self.anode_plot_marker.lower()])
			plt.savefig(os.path.join(path_name, 'plots', 'plot_ch' + str(channel_number + 1) + '_IT.png'))
		elif self.anode_cathode_flag == 1:
			self.y = []
			
			for current in self.cathode_y1:
				self.y.append(current[channel_number])	
		
			xmax = 1.1 * max(self.cathode_x)
			xmin = 1.1 * min(self.cathode_x)
			ymax = 0
			ymin = 1.1 * min(self.y)

			plt.clf()
			plt.xlabel('Time (hours)')
			plt.ylabel(r'Current ($\mu$A)')
			plt.axis([xmin, xmax, ymin, ymax])	
			plt.plot(self.cathode_x, self.y, color = self.cathode_plot_color, linestyle = self._linestyles[self.cathode_line_style.lower()], marker = self._markers[self.cathode_plot_marker.lower()])
			plt.savefig(os.path.join(path_name, 'plots', 'plot_ch' + str(channel_number + 1) + '_IT.png'))
		else:
			self.y1, self.y2 = [], []
			
			for current in self.anode_y1:
				self.y1.append(current[channel_number])

			for current in self.cathode_y1:
				self.y2.append(current[channel_number])	
		
			xmax = 1.1 * max(self.anode_x)
			xmin = 1.1 * min(self.anode_x)
			ymax = 1.1 * max(self.y1)
			ymin = 1.1 * min(self.y2)

			fig = plt.figure()
			ax = fig.add_subplot(111)
	
			fig.add_axes([xmin, xmax, ymin, ymax])

			ax.set_xlabel('Time (hours)')
			ax.set_ylabel(r'Current ($\mu$A)')

			ax.plot(self.anode_x, self.y1, color = self.anode_plot_color, linestyle = self._linestyles[self.anode_line_style.lower()], marker = self._markers[self.anode_plot_marker.lower()])
			ax.plot(self.cathode_x, self.y2, color = self.cathode_plot_color, linestyle = self._linestyles[self.cathode_line_style.lower()], marker = self._markers[self.cathode_plot_marker.lower()])

			leg = ax.legend(('Anode', 'Cathode'), 'upper right')
		
			for t in leg.get_texts():
    				t.set_fontsize('small') 

			plt.savefig(os.path.join(self.anode_path_name, 'plots', 'plot_ch' + str(channel_number + 1) + '_IT.png'))


	def J_T_plot(self, path_name, channel_number):
		if self.anode_cathode_flag == 0: 
			self.y = []

			for current_den in self.anode_y2:
				self.y.append(current_den[channel_number])	
		
			xmax = 1.1 * max(self.anode_x)
			xmin = 1.1 * min(self.anode_x)
			ymax = 1.1 * max(self.y)
			ymin = 0

			plt.clf()
			plt.xlabel('Time (hours)')

			if self.area_unit == 'm^2':
				plt.ylabel(r'Current Density ($\mu$A/$m^2$)')
			else:
				plt.ylabel(r'Current Density ($\mu$A/$cm^2$)')

			plt.axis([xmin, xmax, ymin, ymax])	
			plt.plot(self.anode_x, self.y, color = self.anode_plot_color, linestyle = self._linestyles[self.anode_line_style.lower()], marker = self._markers[self.anode_plot_marker.lower()])
			plt.savefig(os.path.join(path_name, 'plots', 'plot_ch' + str(channel_number + 1) + '_JT.png'))
		elif self.anode_cathode_flag == 1:
			self.y = []
			
			for current_den in self.cathode_y2:
				self.y.append(current_den[channel_number])	
		
			xmax = 1.1 * max(self.cathode_x)
			xmin = 1.1 * min(self.cathode_x)
			ymax = 0
			ymin = 1.1 * min(self.y)

			plt.clf()
			plt.xlabel('Time (hours)')
			if self.area_unit == 'm^2':
				plt.ylabel(r'Current Density ($\mu$A/$m^2$)')
			else:
				plt.ylabel(r'Current Density ($\mu$A/$cm^2$)')

			plt.axis([xmin, xmax, ymin, ymax])	
			plt.plot(self.cathode_x, self.y, color = self.cathode_plot_color, linestyle = self._linestyles[self.cathode_line_style.lower()], marker = self._markers[self.cathode_plot_marker.lower()])
			plt.savefig(os.path.join(path_name, 'plots', 'plot_ch' + str(channel_number + 1) + '_JT.png'))
		else:
			self.y1, self.y2 = [], []
			
			for current_den in self.anode_y2:
				self.y1.append(current_den[channel_number])

			for current_den in self.cathode_y2:
				self.y2.append(current_den[channel_number])	
		
			xmax = 1.1 * max(self.anode_x)
			xmin = 1.1 * min(self.anode_x)
			ymax = 1.1 * max(self.y1)
			ymin = 1.1 * min(self.y2)

			fig = plt.figure()
			ax = fig.add_subplot(111)
	
			fig.add_axes([xmin, xmax, ymin, ymax])

			ax.set_xlabel('Time (hours)')
			if self.area_unit == 'm^2':
				ax.set_ylabel(r'Current Density ($\mu$A/$m^2$)')
			else:
				ax.set_ylabel(r'Current Density ($\mu$A/$cm^2$)')


			ax.plot(self.anode_x, self.y1, color = self.anode_plot_color, linestyle = self._linestyles[self.anode_line_style.lower()], marker = self._markers[self.anode_plot_marker.lower()])
			ax.plot(self.cathode_x, self.y2, color = self.cathode_plot_color, linestyle = self._linestyles[self.cathode_line_style.lower()], marker = self._markers[self.cathode_plot_marker.lower()])

			leg = ax.legend(('Anode', 'Cathode'), 'upper right')
		
			for t in leg.get_texts():
    				t.set_fontsize('small') 

			plt.savefig(os.path.join(self.anode_path_name, 'plots', 'plot_ch' + str(channel_number + 1) + '_JT.png'))
	

def main(anode_dir_path, cathode_dir_path, elec_area, area_unit, **plot_style):
	chrono_data = chrono(anode_dir_path, cathode_dir_path, elec_area, area_unit, plot_style)
	chrono_data.validation()
	chrono_data.process_files()
	
	return True	