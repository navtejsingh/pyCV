import os, sys
from matplotlib import pyplot as plt

'''
		Cyclic Voltammetry Graph Utility
		------------------------------
	Plots potential-current and potential-current density graphs for CV input files.
	If overlay flag is 'on', it overlays graphs from all the input files.
'''

class cv:
	_colors = {'red': 'r', 'green': 'g', 'blue': 'b', 'yellow': 'y', 'cyan': 'c', 'magenta': 'm', 'black': 'k', 'white': 'w'}
	_linestyles = {' ': ' ', '-': 'solid', '--': 'dashed', '-.': 'dash_dot', ':': 'dotted'}
	_markers  = {' ': ' ', '.': '.', '_' : '_', 'o': 'o', '*': '*', '+': '+', 'x': 'x', 'square': 's', 'triangle': '^', 'diamond': 'd'}


	def __init__(self, path_name, elec_area, area_unit, overlay, plot_style):
		self.path_name = path_name.split(',')
		self.elec_area = elec_area
		self.area_unit = area_unit
		self.overlay = overlay
		self.plot_color = plot_style['plot_color']
		self.line_style = plot_style['line_style']
		self.plot_marker = plot_style['marker']
		self.err_msg = None


	# Validate the path and names of the input files
	def validation(self):
		if not self.path_name:
			self.err_msg = 'Nothing to process. Enter a file name\n'
			sys.stderr.write(self.err_msg)
			return False
		else:
			self.path = []
			for path in self.path_name:
				if os.path.isfile(path) == True:
					file_path,file_name = os.path.split(path)
					self.path.append([file_path, file_name])

					pwd = os.getcwd()
					os.chdir(file_path)
					
					try:
						os.mkdir('plots')
					except OSError:
						pass

					os.chdir(pwd)
				else:
					self.err_msg =  'Invalid file path. Check the path and try again!\n'
					sys.stderr.write(self.err_msg)
					return False

		return True


	# Read one file at a time and store potential, current, current density and charge
	def read_file(self,file_name):
		self.x, self.y1, self.y2, self.z = [], [], [], []

		try:
			file = open(file_name,'r')
		except IOError:
			self.err_msg = 'Unable to open ' + file_name + '\n'
			sys.stderr.write(self.err_msg)
			return False
		else:
			data = file.readlines()
			file.close()
	
		for line in data:
			try:			
				float(line[0:4])
			except ValueError:
				pass
			else:
				self.x.append(float(line.split(',')[0]))
				self.y1.append(float(line.split(',')[1])*1.0e6)
				self.y2.append(float(line.split(',')[1])*(1.0e6/float(self.elec_area)))
				self.z.append(float(line.split(',')[2]))	
		
		return True


	# Process one file at a time - reading the file and storing all the variables to be plotted
	def process_files(self):
		self.x_dataset, self.y1_dataset, self.y2_dataset = [], [], []
	
		for file_name in self.path:
			sys.stdout.write('Processing file ' + file_name[1] + '\n')
			self.read_file(os.path.join(file_name[0],file_name[1]))

			self.x_dataset.append(self.x)
			self.y1_dataset.append(self.y1)
			self.y2_dataset.append(self.y2)


	# Plot out IV and JV graphs and if overlay flag is on, overlay all the graphs
	def plot_graphs(self):
		for count in range(len(self.path)):
			self.I_V_plot(count)
			self.J_V_plot(count)

		if self.overlay == 1 and len(self.path) > 1: 
			self.overlay_graphs()


	# Plot IV graphs
	def I_V_plot(self, cnt):
		xmax = 1.1 * max(self.x_dataset[cnt])
		xmin = 1.1 * min(self.x_dataset[cnt])
		ymax = 1.1 * max(self.y1_dataset[cnt])
		ymin = 1.1 * min(self.y1_dataset[cnt])

		plt.clf()
		plt.axis([xmin,xmax,ymin,ymax])

		plt.xlabel('Potential (V)')

		if self.area_unit == 'm^2':
			plt.ylabel(r'Current ($\mu$A)')
		else:
			plt.ylabel(r'Current ($\mu$A)')

		plt.plot(self.x_dataset[cnt], self.y1_dataset[cnt], color = self._colors[self.plot_color.lower()], linestyle = self._linestyles[self.line_style.lower()], marker = self._markers[self.plot_marker.lower()])

		full_name, short_name = self.path[cnt][1], os.path.splitext(self.path[cnt][1])
		plt.savefig(os.path.join(self.path[cnt][0], 'plots', short_name + '_IV.png'))

			
	# Plot JV graphs
	def J_V_plot(self, cnt):
		xmax = 1.1 * max(self.x_dataset[cnt])
		xmin = 1.1 * min(self.x_dataset[cnt])
		ymax = 1.1 * max(self.y2_dataset[cnt])
		ymin = 1.1 * min(self.y2_dataset[cnt])

		plt.clf()
		plt.axis([xmin,xmax,ymin,ymax])

		plt.xlabel('Potential (V)')

		if self.area_unit == 'm^2':
			plt.ylabel(r'Current Density ($\mu$A/$m^2$)')
		else:
			plt.ylabel(r'Current Density ($\mu$A/$cm^2$)')

		plt.plot(self.x_dataset[cnt], self.y2_dataset[cnt], color = self._colors[self.plot_color.lower()], linestyle = self._linestyles[self.line_style.lower()], marker = self._markers[self.plot_marker.lower()])

		full_name, short_name = self.path[cnt][1], os.path.splitext(self.path[cnt][1])
		plt.savefig(os.path.join(self.path[cnt][0], 'plots', short_name + '_JV.png'))


	# Determine maximum value in a list	
	def list_max(self, lst):
		tmp = []

		for item in lst:
			tmp.append(max(item))			
			
		return max(tmp)


	# Determine minimum value in a list
	def list_min(self, lst):
		tmp = []

		for item in lst:
			tmp.append(min(item))			
			
		return min(tmp)


	# Overlay IV and JV graphs
	def overlay_graphs(self):
		### Potential versus Current graph - overlay
		xmax = 1.1 * self.list_max(self.x_dataset)
		xmin = 1.1 * self.list_min(self.x_dataset)
		ymax = 1.1 * self.list_max(self.y1_dataset)
		ymin = 1.1 * self.list_min(self.y1_dataset)

		plt.clf()
		plt.grid()

		fig = plt.figure()
		ax = fig.add_subplot(111)

		fig.add_axes([xmin,xmax,ymin,ymax])

		ax.set_xlabel('Potential (V)')
		ax.set_ylabel(r'Current ($\mu$A)')

		
		for cnt in range(len(self.y1_dataset)):
			ax.plot(self.x_dataset[cnt], self.y1_dataset[cnt], linestyle = self._linestyles[self.line_style.lower()], marker = self._markers[self.plot_marker.lower()])		
		
		full_name, short_name = self.path[cnt][1], os.path.splitext(self.path[cnt][1])
		plt.savefig(os.path.join(self.path[0][0],'plots',short_name + '_overlay_IV.png'))


		### Potential versus Current Density graph - overlay
		xmax = 1.1 * self.list_max(self.x_dataset)
		xmin = 1.1 * self.list_min(self.x_dataset)
		ymax = 1.1 * self.list_max(self.y2_dataset)
		ymin = 1.1 * self.list_min(self.y2_dataset)

		plt.clf()
		plt.grid()

		fig = plt.figure()
		ax = fig.add_subplot(111)

		fig.add_axes([xmin,xmax,ymin,ymax])

		ax.set_xlabel('Potential (V)')

		if self.area_unit == 'm^2':
			ax.set_ylabel(r'Current Density ($\mu$A/$m^2$)')
		else:
			ax.set_ylabel(r'Current Density ($\mu$A/$cm^2$)')

		for cnt in range(len(self.y2_dataset)):
			ax.plot(self.x_dataset[cnt], self.y2_dataset[cnt], linestyle = self._linestyles[self.line_style.lower()], marker = self._markers[self.plot_marker.lower()])		


		full_name, short_name = self.path[cnt][1], os.path.splitext(self.path[cnt][1])
		plt.savefig(os.path.join(self.path[0][0],'plots',short_name + '_overlay_JV.png'))


# Main function - called by GUI as well as command line interface
def main(file_path, elec_area, area_unit, overlay, **plot_style):
	cv_data = cv(file_path, elec_area, area_unit, overlay, plot_style)
	
	if cv_data.validation() == True:
		cv_data.process_files()	
		cv_data.plot_graphs()
		sys.stdout.write("Graphs generated in 'plots' folder in the data files directory\n")
	
		return True
	else:
		return False
	