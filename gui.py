#!/usr/bin/env python

import sys
from Tkinter import *
from tkFileDialog import askopenfilenames, askdirectory
import Pmw
import cv
import chrono


class frame:
	_colors = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta', 'black']
	_linestyles = [' ', '-', '--', '-.', ':']
	_markers  = [' ', 'o', '.', '_', '*', '+', 'x', 'square', 'triangle', 'diamond']
	_units  = ['cm^2', 'm^2']


	def __init__(self, master):
		self.parent = master

		self.file_names = None
		self.anode_name = None
		self.cathode_name = None

		self.var_p1 = IntVar()
		self.var_p2 = IntVar()
		self.elec_area = None

		Pmw.initialise()
		self.create_frame(self.parent)

	
	def create_frame(self, master):
		nb = Pmw.NoteBook(master)
		nb.pack(padx = 10, pady = 10, fill = BOTH, expand = 1)


		################## First Tab - CV graph using one file #####################
		p1 = nb.add('CV Plots')
		g1_p1 = Pmw.Group(p1, tag_text='Data & Parameters')
		g1_p1.pack(fill = 'both', expand = 1, padx = 6, pady = 6)

		self.file_entry_p1 = Pmw.EntryField(g1_p1.interior(), labelpos = 'w', label_text = 'Data Path: ', entry_width = 40, validate = None, command = None)
		self.file_entry_p1.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 5)

		open_file_p1 = Button(g1_p1.interior(), text = 'Select Files', command = self.open_files)
		open_file_p1.grid(row = 0, column = 2, padx = 5, pady = 5)

		self.overlay_graphs_p1 = Checkbutton(g1_p1.interior(), text = 'Overlay graphs', variable = self.var_p1)
		self.overlay_graphs_p1.grid(row = 1, column = 0, padx = 5, pady = 5)		


		self.elec_area_entry_p1 = Pmw.EntryField(g1_p1.interior(), labelpos = 'w', label_text = 'Electrode Area: ',  entry_width = 4, validate = {'validator': 'real'}, command = None)
		self.elec_area_entry_p1.grid(row = 2, column = 0, padx = 5, pady = 5)

		self.area_unit_entry_p1 = Pmw.OptionMenu(g1_p1.interior(), labelpos='w', label_text='', items = self._units, menubutton_width=4,)
		self.area_unit_entry_p1.setvalue(self._units[0])
		self.area_unit_entry_p1.grid(row = 2, column = 1, padx = 2, pady = 2)

		g2_p1 = Pmw.Group(p1, tag_text='Plot Style')
		g2_p1.pack(fill = 'both', expand = 1, padx = 6, pady = 6)

		self.plot_color_p1 = Pmw.OptionMenu(g2_p1.interior(), labelpos='w', label_text='Plot color: ', items = self._colors, menubutton_width = 6,)
		self.plot_color_p1.setvalue(self._colors[2])
		self.plot_color_p1.grid(row = 0, column = 0, padx = 10, pady = 5)

		self.plot_line_p1 = Pmw.OptionMenu(g2_p1.interior(), labelpos='w', label_text='Line Style: ', items = self._linestyles, menubutton_width = 2,)
		self.plot_line_p1.setvalue(self._linestyles[1])
		self.plot_line_p1.grid(row = 0, column = 1, padx = 10, pady = 5)

		self.plot_marker_p1 = Pmw.OptionMenu(g2_p1.interior(), labelpos='w', label_text='Marker: ', items = self._markers, menubutton_width = 6,)
		self.plot_marker_p1.setvalue(self._markers[1])
		self.plot_marker_p1.grid(row = 0, column = 2, padx = 10, pady = 5)
 
		close_p1 = Button(p1, text='Cancel', command=root.quit)
		close_p1.pack(side = 'right', expand = 0, padx = 6, pady = 6)

		generate_graphs_p1 = Button(p1, text='Generate graphs', command = self.generate_graph_p1)
		generate_graphs_p1.pack(side = 'right', expand = 0, padx = 6, pady = 6)



		################## Second tab - Chrono plots #####################
		p2 = nb.add('Chrono Plots')
		g1_p2 = Pmw.Group(p2, tag_text='Data & Parameters')
		g1_p2.pack(fill = 'both', expand = 1, padx = 6, pady = 6)

		self.directory_entry_p2_1 = Pmw.EntryField(g1_p2.interior(), labelpos = 'w', label_text = 'Anode Data: ', entry_width = 40, validate = None, command = None)
		self.directory_entry_p2_1.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 5)

		open_directory_p2_1 = Button(g1_p2.interior(), text = 'Select Folder', command = self.open_anode)
		open_directory_p2_1.grid(row = 0, column = 2, padx = 5, pady = 5) 

		self.directory_entry_p2_2 = Pmw.EntryField(g1_p2.interior(), labelpos = 'w', label_text = 'Cathode Data: ', entry_width = 40, entry_state = 'disabled', validate = None, command = None)
		self.directory_entry_p2_2.grid(row = 1, column = 0, columnspan = 2, padx = 10, pady = 5)

		open_directory_p2_2 = Button(g1_p2.interior(), text = 'Select Folder', state = DISABLED, command = self.open_cathode)
		open_directory_p2_2.grid(row = 1, column = 2, padx = 5, pady = 5) 


		self.overlay_graphs_p2 = Checkbutton(g1_p2.interior(), text = 'Overlay graphs', variable = self.var_p2, state = DISABLED)
		self.overlay_graphs_p2.grid(row = 2, column = 0, padx = 5, pady = 5)		
		self.overlay_graphs_p2.select()

		self.elec_area_entry_p2 = Pmw.EntryField(g1_p2.interior(), labelpos = 'w', label_text = 'Electrode Area: ',  entry_width = 4, validate = {'validator': 'real'}, command = None)
		self.elec_area_entry_p2.grid(row = 3, column = 0, padx = 5, pady = 5)

		self.area_unit_entry_p2 = Pmw.OptionMenu(g1_p2.interior(), labelpos='w', label_text='', items = self._units, menubutton_width=4,)
		self.area_unit_entry_p2.setvalue(self._units[0])
		self.area_unit_entry_p2.grid(row = 3, column = 1, padx = 2, pady = 2)


		g2_p2 = Pmw.Group(p2, tag_text='Plot Style')
		g2_p2.pack(fill = 'both', expand = 1, padx = 6, pady = 6)

		anode_label = Label(g2_p2.interior(), text = 'Anode --> ')
		anode_label.grid(row = 0, column = 0, padx = 5, pady = 5)

		self.plot_color_p2_1 = Pmw.OptionMenu(g2_p2.interior(), labelpos = 'w', label_text = 'Plot color: ', items = self._colors, menubutton_width = 6,)
		self.plot_color_p2_1.setvalue(self._colors[1])
		self.plot_color_p2_1.grid(row = 0, column = 1, padx = 10, pady = 5)


		self.plot_line_p2_1 = Pmw.OptionMenu(g2_p2.interior(), labelpos='w', label_text='Line Style: ', items = self._linestyles, menubutton_width = 2,)
		self.plot_line_p2_1.setvalue(self._linestyles[1])
		self.plot_line_p2_1.grid(row = 0, column = 2, padx = 10, pady = 5)


		self.plot_marker_p2_1 = Pmw.OptionMenu(g2_p2.interior(), labelpos='w', label_text='Marker: ', items = self._markers, menubutton_width = 6,)
		self.plot_marker_p2_1.setvalue(self._markers[2])
		self.plot_marker_p2_1.grid(row = 0, column = 3, padx = 10, pady = 5)


		cathode_label = Label(g2_p2.interior(), text = 'Cathode --> ')
		cathode_label.grid(row = 1, column = 0, padx = 5, pady = 5)

		self.plot_color_p2_2 = Pmw.OptionMenu(g2_p2.interior(), labelpos = 'w', label_text = 'Plot color: ', items = self._colors, menubutton_width = 6,)
		self.plot_color_p2_2.setvalue(self._colors[2])
		self.plot_color_p2_2.grid(row = 1, column = 1, padx = 10, pady = 5)


		self.plot_line_p2_2 = Pmw.OptionMenu(g2_p2.interior(), labelpos='w', label_text='Line Style: ', items = self._linestyles, menubutton_width = 2,)
		self.plot_line_p2_2.setvalue(self._linestyles[1])
		self.plot_line_p2_2.grid(row = 1, column = 2, padx = 10, pady = 5)

		self.plot_marker_p2_2 = Pmw.OptionMenu(g2_p2.interior(), labelpos='w', label_text='Marker: ', items = self._markers, menubutton_width = 6,)
		self.plot_marker_p2_2.setvalue(self._markers[2])
		self.plot_marker_p2_2.grid(row = 1, column = 3, padx = 10, pady = 5)


		close_p2 = Button(p2, text = 'Cancel', command=root.quit)
		close_p2.pack(side = 'right', expand = 0, padx = 6, pady = 6)

		generate_graphs_p2 = Button(p2, text='Generate graphs', command = self.generate_graphs_p2)
		generate_graphs_p2.pack(side = 'right', expand = 0, padx = 6, pady = 6)
	
		nb.tab('CV Plots').focus_set()


	def open_files(self):
		self.file_names = askopenfilenames()
		self.file_entry_p1.clear()
		self.file_entry_p1.insert(0, self.file_names)


	def open_anode(self):
		self.anode_name = askdirectory()
		self.directory_entry_p2_1.clear()
		self.directory_entry_p2_1.insert(0, self.anode_name)		


	def open_cathode(self):
		self.cathode_name = askdirectory()
		self.directory_entry_p2_2.clear()
		self.directory_entry_p2_2.insert(0, self.cathode_name)		


	def generate_graph_p1(self):
		self.elec_area = self.elec_area_entry_p1.getvalue()

		if self.file_names and self.elec_area:
			names = self.file_names[0]			
			for i in range(1,len(self.file_names)):
				names += ',' + self.file_names[i]

			if cv.main(names, float(self.elec_area), self.area_unit_entry_p1.getvalue(), self.var_p1.get(), plot_color = self.plot_color_p1.getvalue(), line_style = self.plot_line_p1.getvalue(), marker = self.plot_marker_p1.getvalue()) == True:
				dialog = Pmw.MessageDialog(self.parent, title = 'Success Message', defaultbutton = 0, message_text = 'Graphs successfully generated!')
				dialog.activate()
			else:
				dialog = Pmw.MessageDialog(self.parent, title = 'Error Message', defaultbutton = 0, message_text = 'Failed to generate the graphs. Check error.txt file for details.')
				dialog.activate()				
		else:
			dialog = Pmw.MessageDialog(self.parent, title = 'Error Message', defaultbutton = 0, message_text = 'Please select data files and enter electrode area to generate graphs!')
			dialog.activate()



	def generate_graphs_p2(self):
		self.elec_area = self.elec_area_entry_p2.getvalue()

		if self.anode_name and self.elec_area:
			if chrono.main(self.anode_name, '', float(self.elec_area), self.area_unit_entry_p2.getvalue(), anode_plot_color = self.plot_color_p2_1.getvalue(), anode_line_style = self.plot_line_p2_1.getvalue(), anode_marker = self.plot_marker_p2_1.getvalue(), cathode_plot_color = self.plot_color_p2_2.getvalue(), cathode_line_style = self.plot_line_p2_2.getvalue(), cathode_marker = self.plot_marker_p2_2.getvalue()) == True:
				dialog = Pmw.MessageDialog(self.parent, title = 'Success Message', defaultbutton = 0, message_text = 'Graphs successfully generated!')
				dialog.activate()
		else:
			dialog = Pmw.MessageDialog(self.parent, title = 'Error Message', defaultbutton = 0, message_text = 'Please select data files and enter electrode area to generate graphs!')
			dialog.activate()



if __name__ == '__main__':

	root = Tk()
	root.title('Cyclic Voltammetry Graph Utility')
	root.maxsize(width=700,height=400)
	root.minsize(width=700,height=400)
	root.resizable(width=NO,height=NO)

	w = root.winfo_screenwidth()
	h = root.winfo_screenheight()
	root.update_idletasks()	
	rootsize = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
	x = w/2 - rootsize[0]/2
	y = h/2 - rootsize[1]/2
	root.geometry("%dx%d+%d+%d" % (rootsize + (x, y)))

	plot = frame(root)	

	try:
		log_file = open('log.txt', 'w')
		err_file = open('error.txt', 'w')
	except IOError:
		sys.stderr.write('Unable to open files in write mode')
	else:
		sys.stdout = log_file
		sys.stderr = err_file
	
	root.mainloop()
