from tkinter import *
from math import sin, cos, pi
from random import randrange
import os
import time, threading
import subprocess
import pickle
import numpy as np
import random
from math import cos, sin, sqrt, pi
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
from tkinter import *
import matplotlib
import serial

import usb.core
import usb.util

from collections import deque

import can


matplotlib.use("TkAgg")
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib import cm, colors
import matplotlib.animation as animation
import sys
import os
import socket
from tkinter import messagebox,ttk
import threading
import matplotlib.image as image
import multiprocessing
#from scipy.spatial import KDTree as KDTree


class Canon:
    """Initialisation of elemnt in my GUI
    params:
        fen1:Tkinter window
        flag_start= flag to start event display
        threshold: threshold of DAQ
        comm:class of communication with socket server
        usb2can : class of communication with electronic device usb2can
        entr1: spinbox in Tkinter for var_threshold_DAC
        var_threshold : value of the var_threshold_DAC
        entr14: spinbox in Tkinter for var_threshold_HG
        entr14: spinbox in Tkinter for var_threshold_LG
        var_threshold_HG: value of threshold_HG
        var_threshold_HG: value of threshold_LG

        """

    def __init__(self, fen1, flag_start, comm, usb2can, entr1, var_threshold, entr14, var_threshold_HG, entr15,
                 var_threshold_LG):
        self.x_center = 0 #Camera x_center
        self.y_center = 0 #Camera y_center
        self.size_edge_to_edge = 23.2 # size edge to edge of the pixels
        self.death_size = 1 #death size between pixels
        self.time_allowed_to_display_events = 4000 # step of time during taking data
        self.flag_start=flag_start
        self.fen1=fen1
        self.flag_1=0 # this flag is an auxilliary flag to know if i m enter in subprocess, if i enter in connect with socket server and so on
        self.flag_stop=0 #flag to stop event display
        #self.test_messages_old = 0
        self.entr1=entr1   # Spinbox of threshold variable
        self.threshold_DAC=int(self.entr1.get())
        self.var_threshold_DAC=var_threshold
        self.entr14, self.var_threshold_HG, self.entr15, self.var_threshold_LG=entr14,var_threshold_HG,entr15,var_threshold_LG
        self.threshold_HG,self.threshold_LG=int(self.entr14.get()),int(self.entr15.get())

        self.new_file_to_write = "D:/resultat_acquisition_babymind/_new_file_to_write.daq" # result file where i will writing my event data for later access

        self.file_to_analyze_rate= "D:/resultat_acquisition_babymind/_file_to_analyze_rate.daq" # file where i will put results for analysing rate

        #this are the config files and C sharp script to taking data
        self.config_file_init_0= "D:/resultat_acquisition_babymind/config_scriptApplib_files/init_config_b0.xml"
        self.config_file_init_1 = "D:/resultat_acquisition_babymind/config_scriptApplib_files/init_config_b1.xml"
        self.config_file_aux_0 = "D:/resultat_acquisition_babymind/config_scriptApplib_files/aux_config_b0.xml"
        self.config_file_aux_1 = "D:/resultat_acquisition_babymind/config_scriptApplib_files/aux_config_b1.xml"
        #self.script_cs="D:/resultat_acquisition_babymind/config_scriptApplib_files/daq-tdm-Applib-slotArray-v1.cs"
        self.script_cs = "D:/resultat_acquisition_babymind/config_scriptApplib_files/scriptmainargs.cs"

        #configuration regard for the mapping.
        self.order_list_of_pixels_in_reading_temperature = [98, 99, 112, 113, 87, 88, 100, 101, 76, 89, 90, 102, 124, 125,
                                                       135, 136, 114, 115, 126, 127, 103, 116, 117, 128, 137, 138, 142,
                                                       143, 131, 132, 139, 140, 123, 133, 134, 141, 118, 119, 129, 130,
                                                       108, 109, 120, 121, 97, 110, 111, 122, 39, 50, 49, 61, 51, 63,
                                                       62, 73, 75, 74, 86, 85, 60, 71, 70, 82, 72, 84, 83, 94, 96, 95,
                                                       107, 106, 12, 23, 22, 34, 24, 36, 35, 46, 48, 47, 59, 58, 1, 6,
                                                       5, 13, 7, 15, 14, 25, 27, 26, 38, 37, 78, 66, 54, 42, 77, 65, 53,
                                                       41, 64, 52, 40, 28, 30, 18, 10, 4, 29, 17, 9, 3, 16, 8, 2, 0, 57,
                                                       45, 33, 21, 56, 44, 32, 20, 43, 31, 19, 11, 105, 93, 81, 69, 104,
                                                       92, 80, 68, 91, 79, 67, 55]


        self.flag_store_temperature = 0 # flag to store temperature
        self.temperature_file = "D:/resultat_acquisition_babymind/folder_to_test_readout_temperature/push_pull_T.txt" #temperature file where i will store temperature

        #initialisation variables
        self.list_mean_cosmicray_rate_HG=[]
        self.list_std_cosmicray_rate_HG=[]
        self.list_mean_cosmicray_rate_LG=[]
        self.list_std_cosmicray_rate_LG=[]
        self.list_mean_cosmicray_rate_tot=[]
        self.list_std_cosmicray_rate_tot=[]

        self.list_mean_trigger_rate_ampli=[]
        self.list_std_trigger_rate_ampli=[]
        self.list_mean_trigger_rate_tot=[]
        self.list_std_trigger_rate_tot=[]

        #this is the variables to evaluate npe with spectrum
        self.pedestal_LG=[15]*144
        self.Gain_LG=[4.5]*144

        self.pedestal_HG = [144]*144
        self.Gain_HG = [47]*144

        self.pedestal_tot = [0]*144
        self.Gain_tot = [3]*144

        # the global histogram will be performing here
        self.bin_array_HG = [np.arange(0, 150, round(x + y)) for x, y in zip(self.pedestal_HG, self.Gain_HG)]
        self.bin_array_LG = [np.arange(0, 150, round(x + y)) for x, y in zip(self.pedestal_LG, self.Gain_LG)]
        self.bin_array_tot = [np.arange(0, 150, round(x + y)) for x, y in zip(self.pedestal_tot, self.Gain_tot)]
        #self.my_global_histogram_HG = []
        #self.my_global_histogram_LG = []
        self.old_dict_pixelid_values_HG_for_histo_global = dict(
            (i, Hist1D_global(self.bin_array_HG[i], 0, 5000, i)) for i in np.arange(144))
        self.old_dict_pixelid_values_LG_for_histo_global = dict(
            (i, Hist1D_global(self.bin_array_LG[i], 0, 5000, i)) for i in np.arange(144))
        self.old_dict_pixelid_values_tot_for_histo_global = dict(
            (i, Hist1D_global(self.bin_array_tot[i], 0, 5000, i)) for i in np.arange(144))

        self.comm=comm

        self.usb2can=usb2can

        # self.power_supply=power_supply

        self.var_pause_restart = 1 # initial value for the pause restart (b5) button

        self.flag_active_draw_button_for_histo_parent = 0  #This flag is to know if i can have data to draw it in histogramm

        self.var_global_local_histo=1

        self.flag_test_if_i_operate_global_local_histo = 0  # flag to test if i m enter in the function global or local plot histo

        self.flag_draw_trigger_rate=False

        self.flag_finish_function_get_boards_values_from_file = False  # this is to false initialisation indication for function get_boards_values_from_fil

        self.flag_record_data_in_queu_for_analyse = 0

        self.fen1.grid()

        #Define widgets,Canvas,...

        self.txt2 = Label(self.fen1, text='Gain(HG/LG) :')
        self.txt2.grid(row=3, column=1, sticky='NSEW')

        self.value_hg_or_lg = StringVar()
        self.value_hg_or_lg.set("LG")
        self.bouton1 = Radiobutton(self.fen1, text="HG", variable=self.value_hg_or_lg, value="HG")
        self.bouton1.grid(row=3, column=2, sticky='NSEW')
        self.bouton2 = Radiobutton(self.fen1, text="LG", variable=self.value_hg_or_lg, value="LG")
        self.bouton2.grid(row=3, column=3, sticky='NSEW')
        self.bouton3 = Radiobutton(self.fen1, text="TOT", variable=self.value_hg_or_lg, value="TOT")
        self.bouton3.grid(row=3, column=4, sticky='NSEW')


        self.b3 = Button(self.fen1, text='Start', command=self.start_it)
        self.b3.grid(row=2, column=5, sticky='NSEW')

        self.b4 = Button(self.fen1, text='Stop', cofile_for_acquisition_datammand=self.stop_it)
        self.b4.grid(row=3, column=5, sticky='NSEW')

        self.txt4 = Label(self.fen1, text="Choose trigger conf:")
        self.txt4.grid(row=4, column=1, sticky='NSEW')

        self.var_pixel_trigger_configuration = StringVar(self.fen1)
        self.var_pixel_trigger_configuration.set("1")
        self.entr4 = Spinbox(self.fen1, from_=1, to=3 , textvariable=self.var_pixel_trigger_configuration)
        self.entr4.grid(row=4, column=2)

        self.b5 = Button(self.fen1, text='Pause', command=self._pause)
        self.b5.grid(row=4, column=5, sticky='NSEW')

        self.txt5 = Label(self.fen1, text='Average DAC in trigger \n choosen :')
        self.txt5.grid(row=5, column=1, sticky='NSEW')

        self.var_pixels_trigger_values = StringVar(self.fen1)
        self.var_pixels_trigger_values.set(0)
        self.entr5 = Entry(self.fen1, textvariable=self.var_pixels_trigger_values)
        self.entr5.grid(row=5, column=2,sticky=E)

        self.choices_data_display = ["DAC", "PE", "Eie" , "Temp"]
        self.variable_choices = StringVar(self.fen1)
        self.variable_choices.set("DAC")
        self.box_choice = ttk.Combobox(self.fen1, textvariable=self.variable_choices,values=self.choices_data_display)
        self.box_choice.grid(row=5, column=4, sticky='NSEW')


        self.b6 = Button(self.fen1, text='Quitter', command=self._quit)
        self.b6.grid(row=5, column=5, sticky='NSEW')

        self.txt6 = Label(self.fen1, text='choose pixel \n for histogramm:')
        self.txt6.grid(row=6, column=2, sticky='NSEW')

        self.var_pixel_in_histo = StringVar(self.fen1)
        self.var_pixel_in_histo.set("0")
        self.entr6 = Spinbox(self.fen1, from_=0, to=144, textvariable=self.var_pixel_in_histo)
        self.entr6.grid(row=6, column=3)

        self.b7 = Button(self.fen1, text='Draw', command=self._trace_histo_pixel)
        self.b7.grid(row=6, column=4)

        self.txt9 = Label(self.fen1, text='choose time \n for data \n acquisition(sec):')
        self.txt9.grid(row=7, column=1, sticky='NSEW')
        file_for_acquisition_data
        self.var_time_in_data_acquisition = StringVar(self.fen1)
        self.var_time_in_data_acquisition.set("280")
        self.entr9 = Spinbox(self.fen1, from_=0, to=18000, textvariable=self.var_time_in_data_acquisition)
        self.entr9.grid(row=7, column=2)

        self.txt10 = Label(self.fen1, text='choose time \n for event \n display(msec):')
        self.txt10.grid(row=7, column=3, sticky='NSEW')

        self.var_time_in_event_display = StringVar(self.fen1)
        self.var_time_in_event_display.set("1000")
        self.entr10 = Spinbox(self.fen1, from_=0, to=300000, textvariable=self.var_time_in_event_display)
        self.entr10.grid(row=7, column=4)

        self.txt12 = Label(self.fen1, text='IN section below,Choose parameters to draw trigger rate \n and cosmic rays flux', borderwidth=2, relief="solid", bg='white')
        self.txt12.grid(row=8, column=1, rowspan=1, columnspan=5, sticky='NSEW')

        self.txt13 = Label(self.fen1, text='choose\n Threshold\n FROM:')
        self.txt13.grid(row=9, column=1, sticky='NSEW')

        self.var_threshold_in_trigger_rate_draw_0 = StringVar(self.fen1)
        self.var_threshold_in_trigger_rate_draw_0.set("0")
        self.entr11 = Spinbox(self.fen1, from_=0, to=1023, textvariable=self.var_threshold_in_trigger_rate_draw_0)
        self.entr11.grid(row=9, column=2)

        self.txt14 = Label(self.fen1, text='TO:')
        self.txt14.grid(row=9, column=3, sticky='NSEW')

        self.var_threshold_in_trigger_rate_draw_1 = StringVar(self.fen1)
        self.var_threshold_in_trigger_rate_draw_1.set("200")
        self.entr12 = Spinbox(self.fen1, from_=0, to=1023, textvariable=self.var_threshold_in_trigger_rate_draw_1)
        self.entr12.grid(row=9, column=4)

        self.b12 = Button(self.fen1, text='Draw trigger effisciency \n and cosmic ray flux', command=self._draw_trigger_rate_and_cosmic_flux)
        self.b12.grid(row=9, column=5)

        self.choices_threshold_variation = ["LG", "HG"]
        self.variable_threshold = StringVar(self.fen1)
        self.variable_threshold.set("LG")
        self.threshold_choices = ttk.Combobox(self.fen1, textvariable=self.variable_threshold, values=self.choices_threshold_variation)
        self.threshold_choices.grid(row=10, column=2, sticky='NSEW')

        self.txt15 = Label(self.fen1, text='STEP OF:')
        self.txt15.grid(row=10, column=3, sticky='NSEW')

        self.var_step_threshold_in_trigger_rate_draw= StringVar(self.fen1)
        self.var_step_threshold_in_trigger_rate_draw.set("20")
        self.entr13 = Spinbox(self.fen1, from_=1, to=300, textvariable=self.var_step_threshold_in_trigger_rate_draw)
        self.entr13.grid(row=10, column=4)

        self.var_text_in_GUI = StringVar()
        self._update_box_messages('Welcome to this Event Viewer!!')
        self.txt11= Label(self.fen1, textvariable=self.var_text_in_GUI,borderwidth=2, relief="solid", bg='white', height=10, width=90, wraplength=500)
        self.txt11.grid(row=12, column=1, rowspan=2,columnspan=5, sticky='NSEW')

        self.reatribute_id_pixels = self.make_mini_cam_mathieu_with_node(23.2) # one method to Create and Make the mapping of minicamera

        self.find_neighboors_pixels_by_my_method() # method to find the neighboors of pixels

        if self.flag_start==0:
            self.data_electronics_LG=np.array([random.randint(0, self.threshold_DAC) for r in range(144)])
            self.data_electronics_HG = np.array([random.randint(0, self.threshold_DAC) for r in range(144)])
            self.list_of_pixels_on_events=[]

        self.number_figure = 0 # when you save events, figure number begin by this

        self.fig_fen1 = plt.figure(facecolor="green")
        self.axes_fen1 = self.fig_fen1.add_subplot(111)
        self.canvas_fen1 = FigureCanvasTkAgg(self.fig_fen1, master=self.fen1)
        self.canvas_fen1.get_tk_widget().grid(row=1, column=6, rowspan=8, padx=10, pady=5, sticky='NSEW')
        self.toolbar_frame_fen1 = Frame(self.fen1, highlightcolor="red", highlightthickness=1, highlightbackground="blue")
        self.toolbar_frame_fen1.grid(row=1, column=6)
        self.toolbar_fen1 = NavigationToolbar2Tk(self.canvas_fen1, self.toolbar_frame_fen1)
        self.canvas_fen1._tkcanvas.grid(row=1, column=6, rowspan=8, padx=10, pady=5, sticky='NSEW')
        self.canvas_fen1.show()
        if self.box_choice.get() == "Temp":
            self.norm1 = matplotlib.colors.Normalize(0, 35)
        else:
            if self.value_hg_or_lg.get() == "HG":
                self.norm1 = matplotlib.colors.Normalize(np.min(self.data_electronics_HG), np.max(self.data_electronics_HG))
            elif self.value_hg_or_lg.get() == "LG":
                self.norm1 = matplotlib.colors.Normalize(np.min(self.data_electronics_LG), np.max(self.data_electronics_LG))
            elif self.value_hg_or_lg.get() == "TOT":
                self.norm1 = matplotlib.colors.Normalize(np.min(self.data_electronics_tot), np.max(self.data_electronics_tot))
        self.cmap1 = matplotlib.cm.ScalarMappable(norm=self.norm1, cmap=matplotlib.cm.jet)
        self.cmap1.set_array([])
        self.cb_fen1 = self.fig_fen1.colorbar(self.cmap1)  # , ticks=facecolor)

        self.dict_polygones={}
        list_centers_xs = []
        list_centers_ys = []
        for pixels_id, polygons_data in self.reatribute_id_pixels.items():
            list_xs_ys = [(polygons_data[0][0][i], polygons_data[0][1][i]) for i in range(6)]

            list_centers_xs.append(polygons_data[1][0])
            list_centers_ys.append(polygons_data[1][1])

            # if you want to draw the camera pixels id in the camera
            self.draw_camera_pixel_ids(polygons_data[1][0], polygons_data[1][1], pixels_id, self.axes_fen1)


            if self.box_choice.get() == "Temp":
                self.polygon = Polygon(list_xs_ys, closed=True,
                                  edgecolor="blue")
            else:
                if self.value_hg_or_lg.get() == "LG":
                    self.polygon = Polygon(list_xs_ys, closed=True,
                                      edgecolor="blue")
                if self.value_hg_or_lg.get() == "HG":
                    self.polygon = Polygon(list_xs_ys, closed=True,
                                      edgecolor="blue")
                if self.value_hg_or_lg.get() == "TOT":
                    self.polygon = Polygon(list_xs_ys, closed=True,
                                      edgecolor="blue")
            self.axes_fen1.add_patch(self.polygon)
            self.dict_polygones[pixels_id]=self.polygon

        self.plots_hex_in_canvas_pdp()

        # this is to adapt size of the widgets,canvas,script_file_for_acquisition_data... with the size of window
        self.fen1.rowconfigure(0, weight=1)
        self.fen1.rowconfigure(1, weight=1)
        self.fen1.rowconfigure(2, weight=1)
        self.fen1.rowconfigure(3, weight=1)
        self.fen1.rowconfigure(4, weight=1)
        self.fen1.rowconfigure(5, weight=1)
        self.fen1.rowconfigure(6, weight=1)
        self.fen1.rowconfigure(7, weight=1)
        self.fen1.rowconfigure(8, weight=1)
        self.fen1.rowconfigure(9, weight=1)
        self.fen1.columnconfigure(0, weight=1)
        self.fen1.columnconfigure(1, weight=1)
        self.fen1.columnconfigure(2, weight=1)
        self.fen1.columnconfigure(3, weight=1)
        self.fen1.columnconfigure(4, weight=1)
        self.fen1.columnconfigure(5, weight=1)
        self.fen1.columnconfigure(6, weight=1)

        self.fen2=None  # this condition is imperative to test if child windfow fen2 is open or not
        self.fen3 = None  # this condition is imperative to test if child windfow fen3 is open or not

        self.b4.config(state="disabled")  # disable the stop button
        self.b5.config(state="disabled")  # disable the pause button
        self.b7.config(state="disabled")  # disable the draw histogram button of the parent window

        self.MCB_BOARD_ID = 0
        self._boardIds = [self.MCB_BOARD_ID, 2]
        # DAQ parameters, will stop on DAQ time reached or File Limit reached
        self._DAQ_TIME = 10000  # in ms
        self._FILE_LIMIT = 20000  # in Ko
        self._SLEEP_TIME = 50  # ms
        self.l_timeEnd = self._DAQ_TIME / self._SLEEP_TIME
        # Readout parameters
        self.l_enableReadoutOnSpillGate = "false"
        self.l_enableGtrigOnlyOnSpill = "false"
        self.l_syncResetEn = "true"  # enable Spill & GTRIG time/tag counters reset
        self.l_enableGtrig = "true"  # DAQ will see the GTRIG beacons, set it to false if you want only amplitude for histograms
        self.beforeConfigure = "false"



        self.flag_can_stop_all = 0



    def _update_box_messages(self,messages):
        '''this function is to update the messages in box messages(Label self txt7)'''

        print(messages)
        """if self.test_messages_old==0:
            self.var_text_in_GUI.set('%s' % messages)
            self.test_messages_old=1
            self.messages_old=messages
        else:
            self.var_text_in_GUI.set(("%s" +"\n %s") %(self.messages_old,messages))
            self.messages_old=(("%s" +"\n %s") %(self.messages_old,messages))
        self.fen1.update_idletasks()"""

    def _trace_histo_pixel(self):
        '''this function is to initialiser the window,canvas,buttons where the histogramm will be plot'''

        self.fen2=Toplevel(self.fen1) #draw the children window of the window fen1

        self.txt8 = Label(self.fen2, text='choose another pixel')
        self.txt8.grid(row=8, column=1, sticky='NSEW')

        self.var_entr7_pixels_to_histo = StringVar(self.fen2, value=int(self.entr6.get()))
        self.entr7 = Entry(self.fen2, textvariable=self.var_entr7_pixels_to_histo)
        self.entr7.grid(row=8, column=2)


        self.b8 = Button(self.fen2, text='Pause', command=self._pause)
        self.b8.grid(row=8, column=5, sticky='NSEW')
        self.b8["text"]=self.b5["text"]

        self.b9 = Button(self.fen2, text='Global', command=self._plot_global_histo)
        self.b9.grid(row=8, column=3, sticky='NSEW')

        self.b10 = Button(self.fen2, text='Close', command=self._close_window_histogramm)
        self.b10.grid(row=8, column=7, sticky='NSEW')

        self.b7.config(state="disabled")  # disable the draw histogram button of the parent window

        self._trace_histo_pixel_draw_and_plot() #draw this histogramm

        # this is to adapt size of the widgets,canvas,... with the size of window
        self.fen2.rowconfigure(0, weight=1)
        self.fen2.rowconfigure(1, weight=1)
        self.fen2.rowconfigure(2, weight=1)
        self.fen2.rowconfigure(3, weight=1)
        self.fen2.rowconfigure(4, weight=1)
        self.fen2.rowconfigure(5, weight=1)
        self.fen2.rowconfigure(6, weight=1)
        self.fen2.rowconfigure(7, weight=1)
        self.fen2.rowconfigure(8, weight=1)
        self.fen2.columnconfigure(0, weight=1)
        self.fen2.columnconfigure(1, weight=1)
        self.fen2.columnconfigure(2, weight=1)
        self.fen2.columnconfigure(3, weight=1)
        self.fen2.columnconfigure(5, weight=1)
        self.fen2.columnconfigure(6, weight=1)
        self.fen2.columnconfigure(7, weight=1)

        self.fen2.protocol("WM_DELETE_WINDOW", self._close_window_histogramm)  # this is reliated to the function _close_window_histogramm

    def _close_window_histogramm(self):
        '''This function is to close the child window where histogramm have been plotting'''
        self.b7.config(state="active")  # Activate the draw button of the parent window

        if self.var_global_local_histo !=1: # test if i close because i have been in function global or local histo00
            # i activate all buttons,entry deactivated
            my_button_list = [self.bouton1, self.bouton2,self.bouton3, self.b5, self.b6, self.b8]
            my_entry_list = [self.entr4, self.entr5, self.entr6]
            for item in my_button_list:
                item.config(state="active")
            for item in my_entry_list:
                item.config(state="normal")
                self.var_global_local_histo =1 #initialize the variable of global or local plot histogramm
            self.b11.destroy()

        self.flag_test_if_i_operate_global_local_histo = 0 # flag to test if i m enter in the function global or local plot histo

        self.fen2.destroy()  # this is necessary on Windows to prevent
        self.fen2 = None

        print(self.fen2)

    def _plot_global_histo(self):
        ''' this function is to know if we want to plot the global or the local histogram of the pixel selected'''

        if self.flag_test_if_i_operate_global_local_histo==0:
            self.flag_test_if_i_operate_global_local_histo=1
            self.last_old_dict_pixelid_values_LG_for_histo_local = self.old_dict_pixelid_values_LG_for_histo_local.copy()
            self.last_old_dict_pixelid_values_HG_for_histo_local = self.old_dict_pixelid_values_HG_for_histo_local.copy()
            self.last_old_dict_pixelid_values_tot_for_histo_local = self.old_dict_pixelid_values_tot_for_histo_local.copy()

        if self.var_global_local_histo % 2 != 0:

            #self.b8.config(state="disabled")

            self.b9["text"] = "Local"
            self.var_global_local_histo += 1

            #if self.b5["text"] == "Pause":  # i check if i am in pause mode or not
            #    self._pause()  # we need to pause the event display to avoid conflict with very heavy file


            if self.flag_test_if_i_operate_global_local_histo == 1:

                # i disabled all buttons,entry activated
                my_button_list = [self.bouton1, self.bouton2,self.bouton3, self.b5, self.b6]
                my_entry_list = [self.entr4, self.entr5, self.entr6]
                for item in my_button_list:
                    item.config(state="disabled")
                for item in my_entry_list:
                    item.config(state="disabled")

                self.b11 = Button(self.fen2, text='Draw\nhisto', command=self._trace_histo_pixel_draw_and_plot)
                self.b11.grid(row=8, column=4, sticky='NSEW')

                self.fen2.columnconfigure(4, weight=1)

                self.flag_test_if_i_operate_global_local_histo = 2

        else:
            self.b9["text"] = "Global"
            self.var_global_local_histo += 1
            #self.b8.config(state="active")  # Activate the pause button of the parent window

        self._trace_histo_pixel_draw_and_plot()

    def _trace_histo_pixel_draw_and_plot(self):
        '''this function is to draw histogram in amplitude and tot of the pixels selected
        since the event display started and in the intervalle of 4s'''

        self.pixel_to_draw_histo = int(self.entr7.get())  # get the value of pixel of which we want to draw the histo
        self._update_box_messages(("Drawing histogramm of pixel %s") % self.pixel_to_draw_histo)

        if self.value_hg_or_lg.get() == "TOT":
            print("ici on trace l'histogramme avec tot")
            self.fig_histo = plt.figure(facecolor="green")
            self.axs_histo_0 = self.fig_histo.add_subplot(311)
            self.axs_histo_1 = self.fig_histo.add_subplot(312)
            self.axs_histo_2 = self.fig_histo.add_subplot(313)
            try:
                if self.flag_test_if_i_operate_global_local_histo != 0:  # flag to test if i m enter in the function global or local plot histo

                    if self.b9["text"] == "Global":

                        if self.b8["text"] == "Continue":

                            self.last_old_dict_pixelid_values_HG_for_histo_local = self.old_dict_pixelid_values_HG_for_histo_local.copy()
                            self.last_old_dict_pixelid_values_LG_for_histo_local = self.old_dict_pixelid_values_LG_for_histo_local.copy()
                            self.last_old_dict_pixelid_values_tot_for_histo_local = self.old_dict_pixelid_values_tot_for_histo_local.copy()

                            bins_hg = \
                                self.old_dict_pixelid_values_HG_for_histo_local[self.pixel_to_draw_histo].bins_local[
                                    self.pixel_to_draw_histo]
                            hist_hg = \
                                self.old_dict_pixelid_values_HG_for_histo_local[self.pixel_to_draw_histo].hist_local[
                                    self.pixel_to_draw_histo]
                            width_hg = bins_hg[1] - bins_hg[0]
                            edges_hg = \
                                self.old_dict_pixelid_values_HG_for_histo_local[self.pixel_to_draw_histo].edges_local[
                                    self.pixel_to_draw_histo]
                            bin_rem = edges_hg[np.where(hist_hg == 0)]
                            bin_c = edges_hg[np.where(hist_hg != 0)]
                            try:
                                x_min_hg = bin_c[0]
                            except:
                                x_min_hg = 0
                            try:
                                x_max_hg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                            except:
                                x_max_hg = 5000
                            self.axs_histo_0.bar(bins_hg, hist_hg, width_hg, align="center", edgecolor='black')

                            bins_lg = \
                                self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].bins_local[
                                    self.pixel_to_draw_histo]
                            hist_lg = \
                                self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].hist_local[
                                    self.pixel_to_draw_histo]
                            width_lg = bins_lg[1] - bins_lg[0]
                            edges_lg = \
                                self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].edges_local[
                                    self.pixel_to_draw_histo]
                            bin_rem = edges_lg[np.where(hist_lg == 0)]
                            bin_c = edges_lg[np.where(hist_lg != 0)]
                            try:
                                x_min_lg = bin_c[0]
                            except:
                                x_min_lg = 0
                            try:
                                x_max_lg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                            except:
                                x_max_lg = 5000
                            self.axs_histo_1.bar(bins_lg, hist_lg, width_lg, align="center", edgecolor='black')

                            bins_tot = \
                                self.old_dict_pixelid_values_tot_for_histo_local[self.pixel_to_draw_histo].bins_local[
                                    self.pixel_to_draw_histo]
                            hist_tot = \
                                self.old_dict_pixelid_values_tot_for_histo_local[self.pixel_to_draw_histo].hist_local[
                                    self.pixel_to_draw_histo]
                            width_tot = bins_tot[1] - bins_tot[0]
                            edges_tot = \
                                self.old_dict_pixelid_values_tot_for_histo_local[
                                    self.pixel_to_draw_histo].edges_local[
                                    self.pixel_to_draw_histo]
                            bin_rem = edges_tot[np.where(hist_tot == 0)]
                            bin_c = edges_tot[np.where(hist_tot != 0)]
                            try:
                                x_min_tot = bin_c[0]
                            except:
                                x_min_tot = 0
                            try:
                                x_max_tot = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                            except:
                                x_max_tot = 5000
                            self.axs_histo_1.bar(bins_tot, hist_tot, width_tot, align="center", edgecolor='black')

                        else:

                            self.last_old_dict_pixelid_values_HG_for_histo_local = self.old_dict_pixelid_values_HG_for_histo_local.copy()
                            self.last_old_dict_pixelid_values_LG_for_histo_local = self.old_dict_pixelid_values_LG_for_histo_local.copy()
                            self.last_old_dict_pixelid_values_tot_for_histo_local = self.old_dict_pixelid_values_tot_for_histo_local.copy()

                            bins_hg = \
                                self.old_dict_pixelid_values_HG_for_histo_local[self.pixel_to_draw_histo].bins_local[
                                    self.pixel_to_draw_histo]
                            hist_hg = \
                                self.old_dict_pixelid_values_HG_for_histo_local[self.pixel_to_draw_histo].hist_local[
                                    self.pixel_to_draw_histo]
                            width_hg = bins_hg[1] - bins_hg[0]
                            edges_hg = \
                                self.old_dict_pixelid_values_HG_for_histo_local[self.pixel_to_draw_histo].edges_local[
                                    self.pixel_to_draw_histo]
                            bin_rem = edges_hg[np.where(hist_hg == 0)]
                            bin_c = edges_hg[np.where(hist_hg != 0)]
                            try:
                                x_min_hg = bin_c[0]
                            except:
                                x_min_hg = 0
                            try:
                                x_max_hg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                            except:
                                x_max_hg = 5000
                            self.axs_histo_0.bar(bins_hg, hist_hg, width_hg, align="center", edgecolor='black')

                            bins_lg = \
                                self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].bins_local[
                                    self.pixel_to_draw_histo]
                            hist_lg = \
                                self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].hist_local[
                                    self.pixel_to_draw_histo]
                            width_lg = bins_lg[1] - bins_lg[0]
                            edges_lg = \
                                self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].edges_local[
                                    self.pixel_to_draw_histo]
                            bin_rem = edges_lg[np.where(hist_lg == 0)]
                            bin_c = edges_lg[np.where(hist_lg != 0)]
                            try:
                                x_min_lg = bin_c[0]
                            except:
                                x_min_lg = 0
                            try:
                                x_max_lg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                            except:
                                x_max_lg = 5000
                            self.axs_histo_1.bar(bins_lg, hist_lg, width_lg, align="center", edgecolor='black')

                            bins_tot = \
                                self.old_dict_pixelid_values_tot_for_histo_local[self.pixel_to_draw_histo].bins_local[
                                    self.pixel_to_draw_histo]
                            hist_tot = \
                                self.old_dict_pixelid_values_tot_for_histo_local[self.pixel_to_draw_histo].hist_local[
                                    self.pixel_to_draw_histo]
                            width_tot = bins_tot[1] - bins_tot[0]
                            edges_tot = \
                                self.old_dict_pixelid_values_tot_for_histo_local[
                                    self.pixel_to_draw_histo].edges_local[
                                    self.pixel_to_draw_histo]
                            bin_rem = edges_tot[np.where(hist_tot == 0)]
                            bin_c = edges_tot[np.where(hist_tot != 0)]
                            try:
                                x_min_tot = bin_c[0]
                            except:
                                x_min_tot = 0
                            try:
                                x_max_tot = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                            except:
                                x_max_tot = 5000
                            self.axs_histo_1.bar(bins_tot, hist_tot, width_tot, align="center", edgecolor='black')


                    else:
                        bins_hg = \
                        self.old_dict_pixelid_values_HG_for_histo_global[self.pixel_to_draw_histo].bins_global[
                            self.pixel_to_draw_histo]
                        hist_hg = \
                        self.old_dict_pixelid_values_HG_for_histo_global[self.pixel_to_draw_histo].hist_global[
                            self.pixel_to_draw_histo]
                        width_hg = bins_hg[1] - bins_hg[0]
                        edges_hg = \
                        self.old_dict_pixelid_values_HG_for_histo_global[self.pixel_to_draw_histo].edges_global[
                            self.pixel_to_draw_histo]
                        bin_rem = edges_hg[np.where(hist_hg == 0)]
                        bin_c = edges_hg[np.where(hist_hg != 0)]
                        try:
                            x_min_hg = bin_c[0]
                        except:
                            x_min_hg = 0
                        try:
                            x_max_hg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                        except:
                            x_max_hg = 5000
                        self.axs_histo_0.bar(bins_hg, hist_hg, width_hg, align="center", edgecolor='black')

                        bins_lg = \
                            self.old_dict_pixelid_values_LG_for_histo_global[self.pixel_to_draw_histo].bins_global[
                                self.pixel_to_draw_histo]
                        hist_lg = \
                            self.old_dict_pixelid_values_LG_for_histo_global[self.pixel_to_draw_histo].hist_global[
                                self.pixel_to_draw_histo]
                        width_lg = bins_lg[1] - bins_lg[0]
                        edges_lg = \
                            self.old_dict_pixelid_values_LG_for_histo_global[self.pixel_to_draw_histo].edges_global[
                                self.pixel_to_draw_histo]
                        bin_rem = edges_lg[np.where(hist_lg == 0)]
                        bin_c = edges_lg[np.where(hist_lg != 0)]
                        try:
                            x_min_lg = bin_c[0]
                        except:
                            x_min_lg = 0
                        try:
                            x_max_lg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                        except:
                            x_max_lg = 5000
                        self.axs_histo_1.bar(bins_lg, hist_lg, width_lg, align="center", edgecolor='black')

                        bins_tot = \
                            self.old_dict_pixelid_values_tot_for_histo_global[self.pixel_to_draw_histo].bins_global[
                                self.pixel_to_draw_histo]
                        hist_tot = \
                            self.old_dict_pixelid_values_tot_for_histo_global[self.pixel_to_draw_histo].hist_global[
                                self.pixel_to_draw_histo]
                        width_tot = bins_tot[1] - bins_tot[0]
                        edges_tot = \
                            self.old_dict_pixelid_values_tot_for_histo_global[self.pixel_to_draw_histo].edges_global[
                                self.pixel_to_draw_histo]
                        bin_rem = edges_tot[np.where(hist_tot == 0)]
                        bin_c = edges_tot[np.where(hist_tot != 0)]
                        try:
                            x_min_tot = bin_c[0]
                        except:
                            x_min_tot = 0
                        try:
                            x_max_tot = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                        except:
                            x_max_tot = 5000
                        self.axs_histo_1.bar(bins_tot, hist_tot, width_tot, align="center", edgecolor='black')


                else:
                    self.axs_histo_0.hist(self.old_dict_pixelid_values_HG_for_histo_local[self.pixel_to_draw_histo],
                                          bins=np.arange(0, np.max(self.old_dict_pixelid_values_HG_for_histo_local[
                                                                       self.pixel_to_draw_histo]), 3))
                    self.axs_histo_1.hist(self.old_dict_pixelid_values_tot_for_histo_local[self.pixel_to_draw_histo],
                                          bins=np.arange(0, np.max(self.old_dict_pixelid_values_tot_for_histo_local[
                                                                       self.pixel_to_draw_histo]), 3))
                    self.axs_histo_2.hist(self.old_dict_pixelid_values_tot_for_histo_local[self.pixel_to_draw_histo],
                                          bins=np.arange(0, np.max(self.old_dict_pixelid_values_tot_for_histo_local[
                                                                       self.pixel_to_draw_histo]), 1))

            except KeyError:
                image_warning_pixel_triggered_or_not = image.imread(
                    "D:/resultat_acquisition_babymind/warning_pixel_no_triggered_2.png")
                self.axs_histo_0.imshow(image_warning_pixel_triggered_or_not)
                self.axs_histo_1.imshow(image_warning_pixel_triggered_or_not)
                self.axs_histo_2.imshow(image_warning_pixel_triggered_or_not)

                print("There is not this pixels key in the pixels who have triggered")

            self.fig_histo.tight_layout()
            self.axs_histo_0.set_yscale("log")
            self.axs_histo_0.set_title("Histogram in HG")
            self.axs_histo_0.grid()

            self.axs_histo_1.set_yscale("log")
            self.axs_histo_1.set_title("Histogram in LG")
            self.axs_histo_1.grid()

            self.axs_histo_2.set_yscale("log")
            self.axs_histo_2.set_title("Histogram in tot")
            self.axs_histo_2.grid()
        else:
            print("ici on trace l'histo sans tot")

            self.fig_histo = plt.figure(facecolor="green")
            self.axs_histo_0 = self.fig_histo.add_subplot(211)
            self.axs_histo_1 = self.fig_histo.add_subplot(212)
            try:
                if self.flag_test_if_i_operate_global_local_histo != 0:  # flag to test if i m enter in the function global or local plot histo

                    if self.b9["text"] == "Global":

                        if self.b8["text"] == "Continue":

                            bins_hg = \
                                self.last_old_dict_pixelid_values_HG_for_histo_local[
                                    self.pixel_to_draw_histo].bins_local[
                                    self.pixel_to_draw_histo]
                            hist_hg = \
                                self.last_old_dict_pixelid_values_HG_for_histo_local[
                                    self.pixel_to_draw_histo].hist_local[
                                    self.pixel_to_draw_histo]
                            width_hg = bins_hg[1] - bins_hg[0]
                            edges_hg = \
                                self.last_old_dict_pixelid_values_HG_for_histo_local[
                                    self.pixel_to_draw_histo].edges_local[
                                    self.pixel_to_draw_histo]
                            bin_rem = edges_hg[np.where(hist_hg == 0)]
                            bin_c = edges_hg[np.where(hist_hg != 0)]
                            try:
                                x_min_hg = bin_c[0]
                            except:
                                x_min_hg = 0
                            try:
                                x_max_hg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                            except:
                                x_max_hg = 5000
                            self.axs_histo_0.bar(bins_hg, hist_hg, width_hg, align="center", edgecolor='black')

                            bins_lg = \
                                self.last_old_dict_pixelid_values_LG_for_histo_local[
                                    self.pixel_to_draw_histo].bins_local[
                                    self.pixel_to_draw_histo]
                            hist_lg = \
                                self.last_old_dict_pixelid_values_LG_for_histo_local[
                                    self.pixel_to_draw_histo].hist_local[
                                    self.pixel_to_draw_histo]
                            width_lg = bins_lg[1] - bins_lg[0]
                            edges_lg = \
                                self.last_old_dict_pixelid_values_LG_for_histo_local[
                                    self.pixel_to_draw_histo].edges_local[
                                    self.pixel_to_draw_histo]
                            bin_rem = edges_lg[np.where(hist_lg == 0)]
                            bin_c = edges_lg[np.where(hist_lg != 0)]
                            try:
                                x_min_lg = bin_c[0]
                            except:
                                x_min_lg = 0
                            try:
                                x_max_lg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                            except:
                                x_max_lg = 5000
                            self.axs_histo_1.bar(bins_lg, hist_lg, width_lg, align="center", edgecolor='black')

                        else:
                            self.last_old_dict_pixelid_values_HG_for_histo_local = self.old_dict_pixelid_values_HG_for_histo_local.copy()
                            self.last_old_dict_pixelid_values_LG_for_histo_local = self.old_dict_pixelid_values_LG_for_histo_local.copy()

                            bins_hg = \
                                self.old_dict_pixelid_values_HG_for_histo_local[
                                    self.pixel_to_draw_histo].bins_local[
                                    self.pixel_to_draw_histo]
                            hist_hg = \
                                self.old_dict_pixelid_values_HG_for_histo_local[
                                    self.pixel_to_draw_histo].hist_local[
                                    self.pixel_to_draw_histo]
                            width_hg = bins_hg[1] - bins_hg[0]
                            edges_hg = \
                                self.old_dict_pixelid_values_HG_for_histo_local[
                                    self.pixel_to_draw_histo].edges_local[
                                    self.pixel_to_draw_histo]
                            bin_rem = edges_hg[np.where(hist_hg == 0)]
                            bin_c = edges_hg[np.where(hist_hg != 0)]
                            try:
                                x_min_hg = bin_c[0]
                            except:
                                x_min_hg = 0
                            try:
                                x_max_hg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                            except:
                                x_max_hg = 5000
                            self.axs_histo_0.bar(bins_hg, hist_hg, width_hg, align="center", edgecolor='black')

                            bins_lg = \
                                self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].bins_local[
                                    self.pixel_to_draw_histo]
                            hist_lg = \
                                self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].hist_local[
                                    self.pixel_to_draw_histo]
                            width_lg = bins_lg[1] - bins_lg[0]
                            edges_lg = \
                                self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].edges_local[
                                    self.pixel_to_draw_histo]
                            bin_rem = edges_lg[np.where(hist_lg == 0)]
                            bin_c = edges_lg[np.where(hist_lg != 0)]
                            try:
                                x_min_lg = bin_c[0]
                            except:
                                x_min_lg = 0
                            try:
                                x_max_lg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                            except:
                                x_max_lg = 5000
                            self.axs_histo_1.bar(bins_lg, hist_lg, width_lg, align="center", edgecolor='black')


                    else:

                        bins_hg = \
                            self.old_dict_pixelid_values_HG_for_histo_global[self.pixel_to_draw_histo].bins_global[
                                self.pixel_to_draw_histo]
                        hist_hg = \
                            self.old_dict_pixelid_values_HG_for_histo_global[self.pixel_to_draw_histo].hist_global[
                                self.pixel_to_draw_histo]
                        width_hg = bins_hg[1] - bins_hg[0]
                        edges_hg = \
                            self.old_dict_pixelid_values_HG_for_histo_global[self.pixel_to_draw_histo].edges_global[
                                self.pixel_to_draw_histo]
                        bin_rem = edges_hg[np.where(hist_hg == 0)]
                        bin_c = edges_hg[np.where(hist_hg != 0)]
                        try:
                            x_min_hg = bin_c[0]
                        except:
                            x_min_hg = 0
                        try:
                            x_max_hg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                        except:
                            x_max_hg = 5000
                        self.axs_histo_0.bar(bins_hg, hist_hg, width_hg, align="center", edgecolor='black')

                        bins_lg = \
                            self.old_dict_pixelid_values_LG_for_histo_global[self.pixel_to_draw_histo].bins_global[
                                self.pixel_to_draw_histo]
                        hist_lg = \
                            self.old_dict_pixelid_values_LG_for_histo_global[self.pixel_to_draw_histo].hist_global[
                                self.pixel_to_draw_histo]
                        width_lg = bins_lg[1] - bins_lg[0]
                        edges_lg = \
                            self.old_dict_pixelid_values_LG_for_histo_global[self.pixel_to_draw_histo].edges_global[
                                self.pixel_to_draw_histo]
                        bin_rem = edges_lg[np.where(hist_lg == 0)]
                        bin_c = edges_lg[np.where(hist_lg != 0)]
                        try:
                            x_min_lg = bin_c[0]
                        except:
                            x_min_lg = 0
                        try:
                            x_max_lg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                        except:
                            x_max_lg = 5000
                        self.axs_histo_1.bar(bins_lg, hist_lg, width_lg, align="center", edgecolor='black')

                else:

                    bins_hg = \
                        self.old_dict_pixelid_values_HG_for_histo_local[
                            self.pixel_to_draw_histo].bins_local[
                            self.pixel_to_draw_histo]
                    hist_hg = \
                        self.old_dict_pixelid_values_HG_for_histo_local[
                            self.pixel_to_draw_histo].hist_local[
                            self.pixel_to_draw_histo]
                    width_hg = bins_hg[1] - bins_hg[0]
                    edges_hg = \
                        self.old_dict_pixelid_values_HG_for_histo_local[
                            self.pixel_to_draw_histo].edges_local[
                            self.pixel_to_draw_histo]
                    bin_rem = edges_hg[np.where(hist_hg == 0)]
                    bin_c = edges_hg[np.where(hist_hg != 0)]
                    try:
                        x_min_hg = bin_c[0]
                    except:
                        x_min_hg = 0
                    try:
                        x_max_hg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                    except:
                        x_max_hg = 5000

                    self.axs_histo_0.bar(bins_hg, hist_hg, width_hg, align="center", edgecolor='black')

                    bins_lg = \
                        self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].bins_local[
                            self.pixel_to_draw_histo]
                    hist_lg = \
                        self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].hist_local[
                            self.pixel_to_draw_histo]
                    width_lg = bins_lg[1] - bins_lg[0]
                    edges_lg = \
                        self.old_dict_pixelid_values_LG_for_histo_local[self.pixel_to_draw_histo].edges_local[
                            self.pixel_to_draw_histo]
                    bin_rem = edges_lg[np.where(hist_lg == 0)]
                    bin_c = edges_lg[np.where(hist_lg != 0)]
                    try:
                        x_min_lg = bin_c[0]
                    except:
                        x_min_lg = 0
                    try:
                        x_max_lg = [bin_rem[i] for i in bin_rem if i > bin_c[-1]][0]
                    except:
                        x_max_lg = 5000
                    self.axs_histo_1.bar(bins_lg, hist_lg, width_lg, align="center", edgecolor='black')


            except KeyError:
                image_warning_pixel_triggered_or_not = image.imread(
                    "D:/resultat_acquisition_babymind/warning_pixel_no_triggered_2.png")
                self.axs_histo_0.imshow(image_warning_pixel_triggered_or_not)
                self.axs_histo_1.imshow(image_warning_pixel_triggered_or_not)

                print("There is not this pixels key in the pixels who have triggered")

            self.fig_histo.tight_layout()
            self.axs_histo_0.set_yscale("log")
            self.axs_histo_0.set_title("Histogram in HG")
            self.axs_histo_0.grid()
            self.axs_histo_0.set_xlim(x_min_hg, x_max_hg)

            self.axs_histo_1.set_yscale("log")
            self.axs_histo_1.set_title("Histogram in LG")
            self.axs_histo_1.grid()
            self.axs_histo_0.set_xlim(x_min_lg, x_max_lg)

        self.canvas_histo = FigureCanvasTkAgg(self.fig_histo, master=self.fen2)

        self.canvas_histo.show()

        self.canvas_histo.get_tk_widget().grid(row=1, column=1, rowspan=5, columnspan=6, padx=10, pady=5,
                                               sticky='NSEW')

        self.toolbar_frame_histo = Frame(self.fen2, highlightcolor="red", highlightthickness=1,
                                         highlightbackground="blue")
        self.toolbar_frame_histo.grid(row=0, column=1)
        self.toolbar_histo = NavigationToolbar2Tk(self.canvas_histo, self.toolbar_frame_histo)

        self.canvas_histo._tkcanvas.grid(row=1, column=1, rowspan=5, columnspan=6, padx=10, pady=5, sticky='NSEW')

        def on_key_event(event):
            print('you pressed %s' % event.key)
            key_press_handler(event, self.canvas_histo, self.toolbar_histo)

            self.canvas_histo.mpl_connect('key_press_event', on_key_event)

        self.fen2.attributes("-topmost", True)  # this is to maintain fen2 in front of all windows

    def _pause(self):
        ''' this function is relatif to the command of the pause button (b5). when pause is applying
        the Event display pause and when restart is applying, the event display contnue when
        it has been paused'''
        self.b4.config(state="disabled")  # disable the stop button
        if  self.var_pause_restart%2 != 0:
            self.flag_start=1
            self.b5["text"]="Continue"
            self.var_pause_restart+=1
            self._update_box_messages("Events display has been paused. Click on Continue to continue")

            if (self.fen2 is not None) and self.fen2.winfo_exists():
                self.b8["text"] = self.b5["text"]
        else:
            self.flag_start = 0
            self.b5["text"] = "Pause"
            self.var_pause_restart += 1
            self._update_box_messages("Events display will continu")
            self.b4.config(
                state="active")  # Active the stop button

            if (self.fen2 is not None) and self.fen2.winfo_exists():
                self.b8["text"] = self.b5["text"]

            self.start_it()



    def _quit(self):
        '''This function serve to quit application and close the GUI. It
        is relatif to the command of the quit button(b6)'''
        answer = messagebox.askyesnocancel("Quit", "Are You Sure?", icon='warning')

        if answer:
            # Close the socket server
            try:
                self.comm.deconnect()
                time.sleep(1)

                if self.usb2can.flag_connect_usb2can==1 or self.usb2can.flag_HV_ON==1:
                    self.usb2can.set_HV_OFF_PDP()
                    self.usb2can.shutdown_interface_usb2can_Ixxat()
                #self.comm.deconnect()


                # #self.power_supply.Communicate("Opall 0\n")
                # power_supply.Communicate('INST OUT1\n')
                # power_supply.Communicate('OUTP OFF\n')
                # power_supply.Communicate('INST OUT2\n')
                # power_supply.Communicate('OUTP OFF\n')
                # power_supply.Communicate('INST OUT3\n')
                # power_supply.Communicate('OUTP OFF\n')
                time.sleep(1)
            except:
                # print("Error in stopped socket server")
                self._update_box_messages("Error in stopped socket server")
                sys.exit(1)

            time.sleep(2)



            if self.flag_1 != 0: #test if we are enter in the subprocess create file.this means that stop function has never been activated
                self.stop_it()  # stop properly all (socket server, file writting and reading, ...)
            else:
                self.fen1.quit()  # stops mainloop
                self.fen1.destroy()  # this is necessary on Windows to prevent
                # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def stop_it(self):
        '''This function serve to stop event display. You can restart but in this case all
        the start acquisition restart proceeding. It is relatif to the command of the quit button(b4)'''

        self.b4.config(state="disabled")  # disable the stop button
        self.b5.config(state="disabled")  # disable the pause button

        self.flag_start = 0
        self.flag_stop=1

        self.flag_active_draw_button_for_histo_parent = 0  # This flag is to know if i can have data to draw it in histogramm

        """if self.flag_1==1:
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process)])
            #print("Subproccess killed with success")
            self._update_box_messages("Subproccess killed with success")
        else:
            #print("subprocess never begin.Continue with procedure of stop events display")
            self._update_box_messages("subprocess never begin.Continue with procedure of stop events display")"""

        self.flag_1 = 0

        if self.flag_draw_trigger_rate == False:
            #close new file 1
            self.new_file1.close()
            #print("new file were writting data close with success")
            self._update_box_messages("new file were writting data close with success")

        #close file who contain temperatures data recorded
        if self.flag_store_temperature!=0:
            self.temperature_file.close()

        # send command to stop acquisition
        try:
            # socket.send(bytes('BoardLib.StopAcquisition()\r', "utf-8"))
            self.comm.Communicate('BoardLib.StopAcquisition()\r')
        except:
            #print("Error in Stoping acquisition data")
            self._update_box_messages("Error in Stoping acquisition data")
            sys.exit(1)
        #print("Acquisition of data via socket server has been stopped")
        self._update_box_messages("Acquisition of data via socket server has been stopped")
        time.sleep(2)

        if self.usb2can.flag_connect_usb2can == 1 or self.usb2can.flag_HV_ON == 1:
            self.usb2can.set_HV_OFF_PDP()
            self.usb2can.shutdown_interface_usb2can_Ixxat()
        #self.comm.deconnect()

        """"
        #send command to socket server to deactivate time over threshold in taking data
        if self.value_get_data_with_tot.get():
            try:
                send command on socket server to activate tot
            except:
                self._update_box_messages("Error in activate time over threshold command")
        self._update_box_messages("time over threshold has been deactivate")
        time.sleep(2)
        """

        self.flag_finish_function_get_boards_values_from_file = False  # this is to false indication in finish function get_boards_values_from_fil


        #print("Event display has been stopped by user")
        self._update_box_messages("Event display has been stopped by user")

        self.b3.config(state="active")  # Active the start button to eventually restart event display

        #self.b1.config(state="active")  # Active the checkbutton tot
        self.entr1.config(state="normal")  # Active the entry spinbox threshold hardware

        # #self.power_supply.Communicate("Opall 0\n")
        # power_supply.Communicate('INST OUT1\n')
        # power_supply.Communicate('OUTP OFF\n')
        # power_supply.Communicate('INST OUT2\n')
        # power_supply.Communicate('OUTP OFF\n')
        # power_supply.Communicate('INST OUT3\n')
        # power_supply.Communicate('OUTP OFF\n')
        time.sleep(1)

    def start_it(self):
        '''This function serve to start event display. It is relatif to the command of the quit button(b4)'''

        if self.box_choice.get()=="DAC":
            self.txt5["text"] = "Average DAC in trigger \n choosen :"
        elif self.box_choice.get()=="PE":
            self.txt5["text"] = "Average PE in trigger \n choosen :"
        elif self.box_choice.get()=="Eie":
            self.txt5["text"] = "Average Eie in trigger \n choosen :"
        elif self.box_choice.get()=="Temp":
            print("Get temperatures \n of pixels")
            self.txt5["text"] = "temperatures \n of pixels"

            self.b3.config(state="disabled")  # disable the start button to avoid multiple start event display
            self.b4.config(state="disabled")  # disable the pause button
            self.b5.config(state="disabled")  # disable the stop button
            print(self.usb2can.flag_connect_usb2can)
            if self.usb2can.flag_connect_usb2can == 1 and self.usb2can.flag_HV_ON==1:
                if self.flag_record_data_in_queu_for_analyse == 0:
                    self.usb2can.get_temperature_PDP()
                    #time.sleep(.5)
                #elif self.flag_record_data_in_queu_for_analyse == 1:
                    #time.sleep(0.5)
                self.plots_hex_in_canvas_pdp()
            else:
                if self.b5["text"] == "Pause":
                    self._pause()
                ans = "a"
                print("Usb2can is not connected and HV of PDP is Off \n This means Data is not collected \n Do you still Want to display temperature \n (Yes or No) ")

                while (ans not in ["Yes","No"]):
                    ans = input()
                    if ans=="Yes":
                        self.usb2can.connect_interface_usb2can_Ixxat()
                        time.sleep(1)
                        self.usb2can.set_HV_ON_PDP()
                        time.sleep(1)
                        self.usb2can.get_temperature_PDP()
                        #time.sleep(0.5)
                        self.plots_hex_in_canvas_pdp()
                    if ans=="No":
                        self.variable_choices.set("DAC")
                        continue
                    else:
                        print("Enter the correct answer \n (Yes or No) ")
        if self.box_choice.get()!="Temp":

            if self.flag_start == 0 and self.flag_stop==0:
                #
                self.flag_start = 1

                if self.flag_1==0:

                    self.start_test_global = time.time()

                    self.flag_can_stop_all = 0

                    self.threshold_DAC = int(self.entr1.get())
                    self.threshold_HG = int(self.entr14.get())
                    self.threshold_LG = int(self.entr15.get())

                    self.b3.config(state="disabled") # disable the start button to avoid multiple start event display
                    self.b4.config(state="active")  # enable the pause button
                    self.b5.config(state="active")  # enable the stop button

                    #self.b1.config(state="disabled")  # disabling the checkbutton tot
                    self.entr1.config(state="disabled")  # disabling the entry spinbox threshold hardware

                    # #os.system('D:\\resultat_acquisition_babymind\\devcon.exe restart *ROOT_HUB20*')
                    # #time.sleep(5)
                    # #self.power_supply.__init__()
                    # # self.power_supply.Communicate("Opall 1\n")
                    # power_supply.Communicate('INST OUT1\n')
                    # power_supply.Communicate('OUTP ON\n')
                    # power_supply.Communicate('INST OUT2\n')
                    # power_supply.Communicate('OUTP ON\n')
                    # power_supply.Communicate('INST OUT3\n')
                    # power_supply.Communicate('OUTP ON\n')
                    #'''
                    if comm.connect_socket_server_on_or_off==0: #test if socket server has never been connected
                        try:
                            time.sleep(1)
                            self.comm.Connect()
                        except:
                            #print("Bad connection with socket server")
                            self._update_box_messages("Bad connection with socket server")
                            sys.exit(1)
                        #print("Connection with socket server Enable")
                        self._update_box_messages("Connection with socket server Enable")
                        time.sleep(2)

                    if self.usb2can.flag_connect_usb2can==0:
                        self.usb2can.connect_interface_usb2can_Ixxat()
                        time.sleep(0.5)

                    if self.usb2can.flag_HV_ON==0:
                        self.usb2can.set_HV_ON_PDP()




                    try:
                        # send command to socket server to make and download default configuration file


                        self.comm.Communicate('BoardLib.OpenConfigFile("{}")\r'.format(self.config_file_init_0))

                        for i in [0, 1, 2]:
                            self.comm.Communicate(
                                'BoardLib.SetVariable("ASICS.ASIC{}.GlobalControl.DAC10b",{})\r'.format(i,self.threshold_DAC))
                            self.comm.Communicate(
                                'BoardLib.SetVariable("ASICS.ASIC{}.GlobalControl.DAC10b_t",{})\r'.format(i,
                                                                                                        self.threshold_DAC))
                            comm.Communicate(
                                'BoardLib.SetVariable("FPGA.ASIC{}.GlobalControl.L1ThresholdHG",{})\r'.format(i,self.threshold_HG))
                            comm.Communicate(
                                'BoardLib.SetVariable("FPGA.ASIC{}.GlobalControl.L1ThresholdLG",{})\r'.format(i,self.threshold_LG))
                        """"#send command to socket server to activate or deactivate time over threshold
                        if self.value_get_data_with_tot.get():
                            send command on socket server to activate tot
                        """
                        self.comm.Communicate('BoardLib.BoardConfigure(SendVerifyApply)\r')

                        self.comm.Communicate('BoardLib.SaveConfigFile("{}")\r'.format(self.config_file_aux_0))



                        self.comm.Communicate('BoardLib.OpenConfigFile("{}")\r'.format(self.config_file_init_1))
                        for i in [0, 1, 2]:
                            self.comm.Communicate(
                                'BoardLib.SetVariable("ASICS.ASIC{}.GlobalControl.DAC10b",{})\r'.format(i,
                                                                                                        self.threshold_DAC))
                            self.comm.Communicate(
                                'BoardLib.SetVariable("ASICS.ASIC{}.GlobalControl.DAC10b_t",{})\r'.format(i,
                                                                                                          self.threshold_DAC))
                            comm.Communicate(
                                'BoardLib.SetVariable("FPGA.ASIC{}.GlobalControl.L1ThresholdHG",{})\r'.format(i,
                                                                                                              self.threshold_HG))
                            comm.Communicate(
                                'BoardLib.SetVariable("FPGA.ASIC{}.GlobalControl.L1ThresholdLG",{})\r'.format(i,
                                                                                                              self.threshold_LG))
                        """"#send command to socket server to activate or deactivate time over threshold
                        if self.value_get_data_with_tot.get():
                            send command on socket server to activate tot
                        """
                        self.comm.Communicate('BoardLib.BoardConfigure(SendVerifyApply)\r')

                        self.comm.Communicate('BoardLib.SaveConfigFile("{}")\r'.format(self.config_file_aux_1))

                    except:
                        #print("Error in Assigning value to the DAC10b")
                        self._update_box_messages("Error in settings config file")
                        sys.exit(1)
                    #print("Configure parameters success")
                    self._update_box_messages("Configure parameters success")
                    time.sleep(2)

                    self._update_box_messages(" all setting Config files success")

                    self.get_entry_entr9 = int(self.entr9.get())

                    """"#If i m not drawing trigger rate, i erase all files of previous display
                    if self.flag_draw_trigger_rate == False:"""
                    folder_result_acquisition_babymind = "D:/resultat_acquisition_babymind/folder_result_acquisition_babymind"  #folder where i store my files that interface produce
                    for file_object in os.listdir(folder_result_acquisition_babymind):
                        os.remove(os.path.join(folder_result_acquisition_babymind, file_object))

                    self.flag_1 = 1

                    if self.flag_draw_trigger_rate == False:
                        # start sub process get data from ctrock 7
                        self.th3 = threading.Thread(target=self.analyse_file_contain_rate_aux).start()  # this is to start at same time two functions
                        #self.th3 =multiprocessing.Process(target=self.analyse_file_contain_rate_aux()).start()
                        time.sleep(10)

                        locked = True
                        file_object = None
                        while locked == True:
                            try:
                                # Opening file in append mode and read the first 8 characters.
                                self.new_file1 = open(self.new_file_to_write, "r+b", 8)
                                if self.new_file1:
                                    locked = False
                            except:
                                locked = True
                                time.sleep(10)
                            finally:
                                if file_object:
                                    self._update_box_messages("We open new file and begin to write in it")

                        self.b4.config(state="active")  # Active the stop button

                    else:
                        self.analyse_file_contain_rate_aux()


                if self.flag_draw_trigger_rate == False:
                    self.start_test=time.time()
                    #self.export_data_electronis_values()

            elif self.flag_stop ==1:
                self.flag_start = 0
                self.flag_stop=0
                self.flag_1 = 0
                #print("I initialise different flags to stop event display")
                self._update_box_messages("I initialise different flags to stop event display" )


    def analyse_file_contain_rate_aux(self):

        if self.flag_record_data_in_queu_for_analyse == 0:
            self.flag_record_data_in_queu_for_analyse += 1

        if os.path.exists(self.new_file_to_write):
            os.remove(self.new_file_to_write)
            print("%s has been deleted" % self.new_file_to_write)

        if os.path.exists(self.file_to_analyze_rate):
            os.remove(self.file_to_analyze_rate)
            print("%s has been deleted" % self.file_to_analyze_rate)

        if os.path.exists(self.temperature_file):
            os.remove(self.temperature_file)
            print("%s has been deleted" %self.temperature_file)

        '''
        if self.usb2can.flag_connect_usb2can==1:
            self.usb2can.shutdown_interface_usb2can_Ixxat()
            time.sleep(1)
            power_supply.Communicate('INST OUT1\n')
            power_supply.Communicate('OUTP OFF\n')
            power_supply.Communicate('INST OUT2\n')
            power_supply.Communicate('OUTP OFF\n')
            power_supply.Communicate('INST OUT3\n')
            power_supply.Communicate('OUTP OFF\n')

            time.sleep(1)

            power_supply.Communicate('INST OUT1\n')
            power_supply.Communicate('OUTP ON\n')
            power_supply.Communicate('INST OUT2\n')
            power_supply.Communicate('OUTP ON\n')
            power_supply.Communicate('INST OUT3\n')
            power_supply.Communicate('OUTP ON\n')
            time.sleep(5)

        self.usb2can.connect_interface_usb2can_Ixxat()
        time.sleep(1)
        self.usb2can.set_HV_ON_PDP()
        time.sleep(1)
        '''

        died_time=0
        self.rate_LG = 0
        self.rate_HG = 0
        time_spend_on_acquisition_data=0
        died_time_on_acquisition_data=0
        start_time_1=time.time()

        indice_file_taking_data=0

        buffer_size = 8

        #self.daq_tdm_Applib = 0

        while time_spend_on_acquisition_data < self.get_entry_entr9:

            start_time_on_acquisition_data = time.time()

            aux_name_file_recorded_by_babymind = (
                    "D:/resultat_acquisition_babymind/folder_result_acquisition_babymind/test_{}.daq".format(indice_file_taking_data))

            print("Start proceess to read daq file and write data in new file")

            #run c sharp script to take data
            self.daq_tdm_Applib_slotArray_v1(aux_name_file_recorded_by_babymind)

            locked = True
            file_object = None
            while locked == True:
                try:
                    # Opening file in append mode and read the first 8 characters.
                    file_object = open(aux_name_file_recorded_by_babymind, "r+b", buffer_size)
                    if file_object:
                        locked = False
                except:
                    locked = True
                finally:
                    if file_object:
                        file_object.close()
                        print("taking data is finish in file")
            time_spend_on_acquisition_data += time.time() - start_time_on_acquisition_data
            start_time_on_acquisition_data = time.time()

            #read temperature
            if self.usb2can.flag_connect_usb2can == 1 or self.usb2can.flag_HV_ON == 1:
                self.usb2can.get_temperature_PDP()


            if indice_file_taking_data==0:
                self.queue_for_dtata_recorded_by_babymind=deque([aux_name_file_recorded_by_babymind])

                self.th3 = threading.Thread(target=self.get_boards_values_from_file).start()  # this is to start at same time two functions
            else:
                self.queue_for_dtata_recorded_by_babymind.append(aux_name_file_recorded_by_babymind)

            indice_file_taking_data+=1

            died_time_on_acquisition_data += time.time() - start_time_on_acquisition_data


        print("time in step 1 ( time for begining taking data until finish) ===============", time.time() - start_time_1)

        self.flag_record_data_in_queu_for_analyse=0


        if self.usb2can.flag_HV_ON==1:
            self.usb2can.set_HV_OFF_PDP()
            time.sleep(0.5)

        if self.usb2can.flag_connect_usb2can==1:
            self.usb2can.shutdown_interface_usb2can_Ixxat()
            time.sleep(0.5)

        print("died_time=====>",died_time_on_acquisition_data)
        print('time spend on acquisitioon data=====',time_spend_on_acquisition_data)

        # # self.power_supply.Communicate("Opall 0\n")
        # power_supply.Communicate('INST OUT1\n')
        # power_supply.Communicate('OUTP OFF\n')
        # power_supply.Communicate('INST OUT2\n')
        # power_supply.Communicate('OUTP OFF\n')
        # power_supply.Communicate('INST OUT3\n')
        # power_supply.Communicate('OUTP OFF\n')
        time.sleep(1)

        if self.flag_draw_trigger_rate == True:
            self.get_boards_values_from_file()
            self.stop_it()

        self.flag_can_stop_all=1

    def get_boards_values_from_file(self):

        TDM_ID = 0b1110
        Hit_Amplitude_Id = 0b0011
        Hit_Time_Id = 0b0010
        Gtrig_Header_Id = 0b0001
        Gtrig_trailer_1_Id = 0b0100
        Gtrig_trailer_2_Id = 0b0101
        Special_Word_id = 0b1111

        mean_rate = dict((i, []) for i in np.arange(0, 144))
        std_rate = dict((i, []) for i in np.arange(0, 144))

        mean_trigger_rate=[]
        std_trigger_rate =[]

        start_time_2 = time.time()

        #if len(self.queue_for_dtata_recorded_by_babymind)<=3:
        #    time.sleep(5)
        while len(self.queue_for_dtata_recorded_by_babymind) < 1:
            time.sleep(5)
            pass
        with open(self.new_file_to_write, "ab")as new_file:
            #while self.flag_record_data_in_queu_for_analyse==1:
                #if len(self.queue_for_dtata_recorded_by_babymind) == 0:
                #    time.sleep(5)
            print("queue_for_dtata_recorded_by_babymind====",len(self.queue_for_dtata_recorded_by_babymind))
            while len(self.queue_for_dtata_recorded_by_babymind)>0:
                file_to_open = self.queue_for_dtata_recorded_by_babymind.popleft()
                print("we analyse now %s in the queue"%file_to_open)
                print(len(self.queue_for_dtata_recorded_by_babymind))
                if self.flag_record_data_in_queu_for_analyse != 0 and len(self.queue_for_dtata_recorded_by_babymind)==0:
                    while len(self.queue_for_dtata_recorded_by_babymind) < 1:
                        time.sleep(5)
                        pass
                with open(file_to_open, "r+b") as file:
                    line = file.read(4)
                    out_hex = ['{:02X}'.format(b) for b in line]
                    out_hex.reverse()
                    line_out = ''.join(out_hex)
                    line_out_b = bin(int(line_out, 16))[2:].zfill(32)
                    Word_Id = line_out_b[0:4]

                    event_data_amplitude_LG = {}
                    event_data_amplitude_HG = {}
                    event_data_tot = {}

                    '''
                    data_LG = {}
                    data_HG = {}
                    data_time = {}
                    '''

                    data_LG = [[0]*144]
                    data_HG = [[0]*144]
                    data_time =[[0]*144]

                    dict_queue_edge = {}

                    negative_tot = 0
                    positive_tot = 0

                    pin_complete_slots = []

                    _break = 0
                    sumX1_rate = dict((i, 0) for i in np.arange(0, 144))
                    sumX2_rate = dict((i, 0) for i in np.arange(0, 144))

                    dict_for_calc_rate = dict((i, 0) for i in np.arange(0, 144))
                    nbre_ampli_and_tot = dict((i, 0) for i in np.arange(0, 144))

                    write_in_new_file = 0

                    X1_trigger_rate = 0
                    X2_trigger_rate = 0

                    nbre_trigger_rate = 0

                    gtrig_header = {}
                    global_trigger_header_amplitude = dict((i, []) for i in [0, 2])
                    global_trigger_header_time = dict((i, []) for i in [0, 2])

                    gtrig_ampli_or_tot_old = dict((i, 0) for i in [0, 2])

                    countss = 0

                    gtrig_header_used_for_rate = {}

                    calc_rate = dict((i, 0) for i in np.arange(0, 144))

                    if self.entr5.get() == '':  # attribute value 0 to entry 5 if it is equal to 0
                        self.entr5.delete(0, END)
                        self.entr5.insert(0, "0")

                    self.time_allowed_to_display_events = int(self.entr10.get()) * 1e-3
                    start_time = time.time()
                    duration = 0
                    pqr = 0
                    aux_dict_to_test_coincidence={}

                    while line != b'':# and countss < 40000:

                        countss += 1
                        duration += time.time() - start_time
                        start_time = time.time()


                        if int(Word_Id, 2) == TDM_ID and int(line_out_b[4:6], 2) == 0:

                            slot = int(line_out_b[6:11], 2)

                            line = file.read(4)
                            if line != b'':
                                out_hex = ['{:02X}'.format(b) for b in line]
                                out_hex.reverse()
                                line_out = ''.join(out_hex)
                                line_out_b = bin(int(line_out, 16))[2:].zfill(32)
                                Word_Id = line_out_b[0:4]

                            if slot not in pin_complete_slots:
                                pin_complete_slots.append(slot)
                            else:
                                pin_complete_slots = []
                                pin_complete_slots.append(slot)

                            while int(Word_Id, 2) != TDM_ID and line != b'':

                                if int(Word_Id, 2) == TDM_ID and int(line_out_b[4:6], 2) == 1:
                                    break
                                else:

                                    if int(Word_Id, 2) == Special_Word_id and int(line_out_b[11], 2) == 0 and int(
                                            line_out_b[12:32], 2) == 3:
                                        print("Gtrig + Spill REset for slot {}".format(slot))
                                        nmo = 1
                                    else:

                                        if int(Word_Id, 2) == Gtrig_Header_Id:

                                            gtrig_header[slot] = int(line_out_b[4:32], 2)

                                            while int(Word_Id, 2) != Gtrig_trailer_1_Id and line != b'':

                                                if int(Word_Id, 2) == Hit_Amplitude_Id or int(Word_Id,
                                                                                              2) == Hit_Time_Id:

                                                    if slot == 0:
                                                        Channel_id = int(line_out_b[4:11], 2)
                                                    elif slot == 2:
                                                        Channel_id = int(line_out_b[4:11], 2) + 96
                                                    Hit_Id = int(line_out_b[11:14], 2)
                                                    Tag_Id = int(line_out_b[14:16], 2)
                                                    if int(Word_Id, 2) == Hit_Amplitude_Id:
                                                        Amplitude_Id = int(line_out_b[16:20], 2)
                                                    elif int(Word_Id, 2) == Hit_Time_Id:
                                                        Edge_time = int(line_out_b[16], 2)
                                                    Amplitude_or_tot_measurement = int(line_out_b[20:32], 2)

                                                    if len(
                                                            pin_complete_slots) == 2:  # if pin_complete_slots == [0, 2]:
                                                        write_in_new_file = 1
                                                        if (gtrig_header[slot] - gtrig_ampli_or_tot_old[
                                                            slot]) != 0:  # to  verify
                                                            X1_trigger_rate += 1 / ((gtrig_header[slot] -
                                                                                     gtrig_ampli_or_tot_old[
                                                                                         slot]) * 10e-6)
                                                            X2_trigger_rate += (1 / (
                                                                    (gtrig_header[slot] - gtrig_ampli_or_tot_old[
                                                                        slot]) * 10e-6)) ** 2
                                                            nbre_trigger_rate += 1
                                                            gtrig_ampli_or_tot_old[slot] = gtrig_header[slot]

                                                    if (slot, Channel_id, Tag_Id,
                                                        Hit_Id) in dict_queue_edge.keys():
                                                        if int(Word_Id, 2) == Hit_Time_Id:
                                                            if (slot, Channel_id, Tag_Id,
                                                                Hit_Id) in dict_queue_edge.keys():
                                                                if Edge_time == 1:
                                                                    dict_queue_edge[
                                                                        (slot, Channel_id, Tag_Id,
                                                                         Hit_Id)][1] = Amplitude_or_tot_measurement
                                                                    gtrig_header_used_for_rate[
                                                                        (slot, Channel_id, Tag_Id,
                                                                         Hit_Id)] = gtrig_header[slot]
                                                                elif Edge_time == 0 and dict_queue_edge[
                                                                    (slot, Channel_id, Tag_Id,
                                                                     Hit_Id)][1] != 'a':
                                                                    dict_queue_edge[
                                                                        (slot, Channel_id, Tag_Id,
                                                                         Hit_Id)][0] = Amplitude_or_tot_measurement
                                                                else:
                                                                    del dict_queue_edge[
                                                                        (slot, Channel_id, Tag_Id, Hit_Id)]
                                                                    dict_queue_edge[
                                                                        (slot, Channel_id, Tag_Id,
                                                                         Hit_Id)] = 4 * ['a']
                                                                    dict_queue_edge[
                                                                        (slot, Channel_id, Tag_Id,
                                                                         Hit_Id)][0] = Amplitude_or_tot_measurement
                                                        elif int(Word_Id, 2) == Hit_Amplitude_Id:
                                                            if Amplitude_Id == 3:
                                                                dict_queue_edge[(slot,
                                                                                 Channel_id,
                                                                                 Tag_Id,
                                                                                 Hit_Id)][
                                                                    2] = Amplitude_or_tot_measurement
                                                            elif Amplitude_Id == 2 and dict_queue_edge[(slot,
                                                                                                        Channel_id,
                                                                                                        Tag_Id,
                                                                                                        Hit_Id)][
                                                                2] != 'a':
                                                                dict_queue_edge[(slot,
                                                                                 Channel_id,
                                                                                 Tag_Id,
                                                                                 Hit_Id)][
                                                                    3] = Amplitude_or_tot_measurement

                                                            else:
                                                                del dict_queue_edge[(slot,
                                                                                     Channel_id,
                                                                                     Tag_Id,
                                                                                     Hit_Id)]
                                                                '''dict_queue_edge[(slot,
                                                                                           Channel_id,
                                                                                           Tag_Id,
                                                                                           Hit_Id)] = 4 * ['a']
                                                                dict_queue_edge[(slot,
                                                                                           Channel_id,
                                                                                           Tag_Id,
                                                                                           Hit_Id)][2]=Amplitude_or_tot_measurement'''
                                                        try:
                                                            aux_diff_amplitude = dict_queue_edge[(slot,
                                                                                                  Channel_id,
                                                                                                  Tag_Id,
                                                                                                  Hit_Id)][
                                                                                     3] + \
                                                                                 dict_queue_edge[(slot,
                                                                                                  Channel_id,
                                                                                                  Tag_Id,
                                                                                                  Hit_Id)][
                                                                                     2] + \
                                                                                 dict_queue_edge[(slot,
                                                                                                  Channel_id,
                                                                                                  Tag_Id,
                                                                                                  Hit_Id)][
                                                                                     1] + \
                                                                                 dict_queue_edge[(slot,
                                                                                                  Channel_id,
                                                                                                  Tag_Id,
                                                                                                  Hit_Id)][
                                                                                     0]

                                                            tot = dict_queue_edge[
                                                                      (slot, Channel_id, Tag_Id, Hit_Id)][
                                                                      1] - \
                                                                  dict_queue_edge[
                                                                      (slot, Channel_id, Tag_Id, Hit_Id)][
                                                                      0]
                                                            if tot >= 0:

                                                                global_trigger_header_amplitude[slot].append(
                                                                    gtrig_header[slot])
                                                                global_trigger_header_time[slot].append(
                                                                    gtrig_header_used_for_rate[
                                                                        (slot, Channel_id, Tag_Id,
                                                                         Hit_Id)])

                                                                positive_tot += 1

                                                                val_LG=dict_queue_edge[
                                                                        (slot, Channel_id, Tag_Id,
                                                                         Hit_Id)][2]
                                                                val_HG= dict_queue_edge[
                                                                        (slot, Channel_id, Tag_Id,
                                                                         Hit_Id)][3]

                                                                if Channel_id not in aux_dict_to_test_coincidence.keys():
                                                                    aux_dict_to_test_coincidence[Channel_id]=[val_LG]
                                                                else:
                                                                    aux_dict_to_test_coincidence[Channel_id].append(val_LG)


                                                                data_LG[pqr][Channel_id]= val_LG


                                                                data_HG[pqr][Channel_id]= val_HG


                                                                data_time[pqr][Channel_id]=tot

                                                                #fill global histo
                                                                self.old_dict_pixelid_values_LG_for_histo_global[
                                                                    keys].fill(val_LG, Channel_id)
                                                                self.old_dict_pixelid_values_HG_for_histo_global[
                                                                    keys].fill(val_HG, Channel_id)
                                                                self.old_dict_pixelid_values_tot_for_histo_global[
                                                                    keys].fill(tot, Channel_id)

                                                                #fill local histo
                                                                self.old_dict_pixelid_values_LG_for_histo_local[
                                                                    keys].fill(val_LG, Channel_id)
                                                                self.old_dict_pixelid_values_HG_for_histo_local[
                                                                    keys].fill(val_HG, Channel_id)
                                                                self.old_dict_pixelid_values_tot_for_histo_local[
                                                                    keys].fill(tot, Channel_id)

                                                                event_data_amplitude_LG[nmo] = [(Channel_id,
                                                                                                 dict_queue_edge[
                                                                                                     (slot, Channel_id,
                                                                                                      Tag_Id,
                                                                                                      Hit_Id)][2])]
                                                                event_data_amplitude_HG[nmo] = [(Channel_id,
                                                                                                 dict_queue_edge[
                                                                                                     (slot, Channel_id,
                                                                                                      Tag_Id,
                                                                                                      Hit_Id)][3])]
                                                                event_data_tot[nmo] = (Channel_id,
                                                                                       tot)

                                                                if nbre_ampli_and_tot[Channel_id] != 0:
                                                                    rate_aux = 1 / ((gtrig_header_used_for_rate[
                                                                                         (slot, Channel_id, Tag_Id,
                                                                                          Hit_Id)] - dict_for_calc_rate[
                                                                                         Channel_id]) * 10e-6)
                                                                    sumX1_rate[
                                                                        Channel_id] += rate_aux  # + rate_HG  # this rate is in Mhz. we divide by 10 because 10us is time between header and trailer
                                                                    sumX2_rate[Channel_id] += (
                                                                                                  rate_aux) ** 2  # + rate_HG ** 2  # this rate is in Mhz. we divide by 10 because 10us is time between header and trailer

                                                                nbre_ampli_and_tot[Channel_id] += 1

                                                                dict_for_calc_rate[
                                                                    Channel_id] = gtrig_header_used_for_rate[
                                                                    (slot, Channel_id, Tag_Id,
                                                                     Hit_Id)]

                                                                nmo += 1

                                                                del gtrig_header_used_for_rate[
                                                                    (slot, Channel_id, Tag_Id,
                                                                     Hit_Id)]


                                                            else:
                                                                negative_tot += 1

                                                            del dict_queue_edge[(slot,
                                                                                 Channel_id,
                                                                                 Tag_Id,

                                                                                 Hit_Id)]

                                                        except:
                                                            pass
                                                    else:
                                                        dict_queue_edge[(slot,
                                                                         Channel_id, Tag_Id,
                                                                         Hit_Id)] = 4 * ['a']

                                                        if int(Word_Id, 2) == Hit_Time_Id:
                                                            if Edge_time == 0:
                                                                dict_queue_edge[
                                                                    (slot, Channel_id, Tag_Id,
                                                                     Hit_Id)][0] = Amplitude_or_tot_measurement
                                                            elif Edge_time == 1:
                                                                del dict_queue_edge[
                                                                    (slot, Channel_id, Tag_Id,
                                                                     Hit_Id)]
                                                        elif int(Word_Id, 2) == Hit_Amplitude_Id:
                                                            if Amplitude_Id == 2:
                                                                dict_queue_edge[(slot,
                                                                                 Channel_id,
                                                                                 Tag_Id,
                                                                                 Hit_Id)][
                                                                    3] = Amplitude_or_tot_measurement
                                                            elif Amplitude_Id == 3:
                                                                del dict_queue_edge[(slot,
                                                                                     Channel_id,
                                                                                     Tag_Id,
                                                                                     Hit_Id)]

                                                line = file.read(4)
                                                if line != b'':
                                                    out_hex = ['{:02X}'.format(b) for b in line]
                                                    out_hex.reverse()
                                                    line_out = ''.join(out_hex)
                                                    line_out_b = bin(int(line_out, 16))[2:].zfill(32)
                                                    Word_Id = line_out_b[0:4]

                                                if int(Word_Id, 2) == TDM_ID and int(line_out_b[4:6], 2) == 1:
                                                    _break = 1
                                                    break

                                            '''print("duration==", duration)
                                            print(self.time_allowed_to_display_events)
                                            print(self.flag_draw_trigger_rate)
                                            print(write_in_new_file)'''

                                            if write_in_new_file and self.flag_draw_trigger_rate == False:

                                                self.trigger_sofware_in_pixel_configuration(aux_dict_to_test_coincidence)
                                                if self.list_pixels_triggered==[]:
                                                    data_LG[pqr] = [0] * 144
                                                    data_HG[pqr] = [0] * 144
                                                    data_time[pqr] = [0] * 144
                                                pickle.dump(["Event", data_LG[pqr], data_HG[pqr],data_time[pqr]], new_file)
                                                write_in_new_file = 0
                                                data_LG.append([0]*144)
                                                data_HG.append([0]*144)
                                                data_time.append([0]*144)
                                                pqr+=1
                                                aux_dict_to_test_coincidence={}

                                                if self.flag_active_draw_button_for_histo_parent == 0:
                                                    self.b7.config(
                                                        state="active")  # enable the draw histogram button
                                                    self.flag_active_draw_button_for_histo_parent = 1  # This flag is to know if i can have data to draw it in histogramm

                                                if duration > self.time_allowed_to_display_events:
                                                    index_max_sum = [np.sum(l) for l in data_LG].index(
                                                        np.max([np.sum(l) for l in data_LG]))
                                                    self.data_electronics_LG = data_LG[index_max_sum]
                                                    self.data_electronics_HG = data_HG[index_max_sum]
                                                    self.data_electronics_tot = data_time[index_max_sum]
                                                    self.list_of_pixels_on_events = [data_LG.index(item) for item in
                                                                                     data_LG if item != 0]
                                                    if self.list_of_pixels_on_events !=[] :
                                                        if self.value_hg_or_lg.get() == "HG":
                                                            sum_to_have_more_event_ligthed = np.sum(self.data_electronics_HG)
                                                        elif self.value_hg_or_lg.get() == "LG":
                                                            sum_to_have_more_event_ligthed = np.sum(
                                                                self.data_electronics_LG)
                                                        elif self.value_hg_or_lg.get() == "TOT":
                                                            sum_to_have_more_event_ligthed = np.sum(
                                                                self.data_electronics_tot)
                                                        if sum_to_have_more_event_ligthed >= int(self.entr5.get()):
                                                            print("Boom")
                                                            self.plots_hex_in_canvas_pdp()
                                                            self.fen1.update_idletasks()
                                                    else:
                                                        print("kheops")

                                                    self.old_dict_pixelid_values_HG_for_histo_local = dict(
                                                        (i, Hist1D_local(self.bin_array_HG[i], 0, 5000, i)) for i in
                                                        np.arange(144))
                                                    self.old_dict_pixelid_values_LG_for_histo_local = dict(
                                                        (i, Hist1D_local(self.bin_array_LG[i], 0, 5000, i)) for i in
                                                        np.arange(144))
                                                    self.old_dict_pixelid_values_tot_for_histo_local = dict(
                                                        (i, Hist1D_local(self.bin_array_tot[i], 0, 5000, i)) for i in
                                                        np.arange(144))
                                                    self.list_of_pixels_on_events=[]
                                                    pqr = 0
                                                    data_LG = [[0] * 144]
                                                    data_HG = [[0] * 144]
                                                    data_time = [[0] * 144]

                                                    duration = 0
                                                    start_time = time.time()

                                                    if (self.fen2 is not None) and self.fen2.winfo_exists():  # condition to test if child fen2 window is open or not
                                                        #self.th2 = threading.Thread(target=self._trace_histo_pixel_draw_and_plot()).start()  # this is to start at same time two functions
                                                        self._trace_histo_pixel_draw_and_plot()


                                            if _break:
                                                _break = 0
                                                break

                                            line = file.read(4)
                                            if line != b'':
                                                out_hex = ['{:02X}'.format(b) for b in line]
                                                out_hex.reverse()
                                                line_out = ''.join(out_hex)
                                                line_out_b = bin(int(line_out, 16))[2:].zfill(32)
                                                Word_Id = line_out_b[0:4]

                                line = file.read(4)
                                if line != b'':
                                    out_hex = ['{:02X}'.format(b) for b in line]
                                    out_hex.reverse()
                                    line_out = ''.join(out_hex)
                                    line_out_b = bin(int(line_out, 16))[2:].zfill(32)
                                    Word_Id = line_out_b[0:4]

                        line = file.read(4)
                        if line != b'':
                            out_hex = ['{:02X}'.format(b) for b in line]
                            out_hex.reverse()
                            line_out = ''.join(out_hex)
                            line_out_b = bin(int(line_out, 16))[2:].zfill(32)
                            Word_Id = line_out_b[0:4]

                    for keys in sumX1_rate.keys():
                        if nbre_ampli_and_tot[keys] not in [0, 1]:
                            mean_rate[keys].append(sumX1_rate[keys] / (nbre_ampli_and_tot[keys] - 1))
                            std_rate[keys].append(
                                sqrt((sumX2_rate[keys] / (nbre_ampli_and_tot[keys] - 1)) - mean_rate[keys][0] ** 2))

                            # std_rate[keys].append(1)
                        else:
                            mean_rate[keys].append(0)
                            std_rate[keys].append(0)

                    if nbre_trigger_rate != 0:
                        mean_trigger_rate.append(X1_trigger_rate / nbre_trigger_rate)
                        std_trigger_rate.append(sqrt((X2_trigger_rate / nbre_trigger_rate) - (
                                X1_trigger_rate / nbre_trigger_rate) ** 2))
                    else:
                        mean_trigger_rate.append(0)
                        std_trigger_rate.append(0)

            pickle.dump("END", new_file)

        std_rate = dict((keys,np.mean(mean_rate[keys])) for keys in std_rate.keys())
        mean_rate = dict((keys,np.mean(mean_rate[keys])) for keys in mean_rate.keys())

        mean_trigger_rate=np.mean(mean_trigger_rate)
        std_trigger_rate=np.mean(std_trigger_rate)

        list_rate_components = [mean_rate, std_rate, mean_trigger_rate, std_trigger_rate]

        print(
            "[mean_rate ,std_rate,mean_trigger_rate,std_trigger_rate]===",
            [aux[74] for aux in list_rate_components[0:2]], mean_trigger_rate, std_trigger_rate)

        if self.flag_draw_trigger_rate==True:
            self.list_mean_cosmicray_rate_HG.append(list_rate_components[0][0])
            self.list_std_cosmicray_rate_HG.append(list_rate_components[1][0])
            self.list_mean_cosmicray_rate_LG.append(list_rate_components[2][0] )
            self.list_std_cosmicray_rate_LG.append(list_rate_components[3][0] )
            self.list_mean_cosmicray_rate_tot.append(list_rate_components[4][0] )
            self.list_std_cosmicray_rate_tot.append(list_rate_components[5][0] )

            self.list_mean_trigger_rate_ampli.append(list_rate_components[6])
            self.list_std_trigger_rate_ampli.append(list_rate_components[7])
            self.list_mean_trigger_rate_tot.append(list_rate_components[8])
            self.list_std_trigger_rate_tot.append(list_rate_components[9])

        self.flag_finish_function_get_boards_values_from_file=True

        print("time in step 2 (time of analysing all datas of babymind and copy it in result file)===============", time.time() - start_time_2)

        self.stop_it()

    def _draw_trigger_rate_and_cosmic_flux(self):
        '''This function serve to draw trigger rate and cosmic rays flux. It
                is relatif to the command of the draw button(b12)'''
        answer = messagebox.askyesnocancel("Draw", "Are You Sure to do this operation?", icon='warning')

        if answer:
            if (self.fen2 is not None) and self.fen2.winfo_exists():
                self._close_window_histogramm()

            if self.flag_1==1: # i check if i display and/or store file from babymind
                self.stop_it() # i stop evnt display

            if self.flag_draw_trigger_rate == False:
                folder_result_acquisition_babymind = "D:/resultat_acquisition_babymind/folder_result_acquisition_babymind"
                for file_object in os.listdir(folder_result_acquisition_babymind):
                    os.remove(os.path.join(folder_result_acquisition_babymind, file_object))
            self.flag_draw_trigger_rate=True


            self.threshold_x_shape_in_trigger_plot=np.arange(int(self.entr11.get()),int(self.entr12.get()),int(self.entr13.get()))

            if self.threshold_choices.get() == "LG":
                threshold_old = self.threshold_LG
                flag_stop_old = self.flag_stop
                for threshold_aux in self.threshold_x_shape_in_trigger_plot:
                    self.var_threshold_LG.set("%s"%threshold_aux)
                    print(threshold_aux)
                    self.start_it()
                    self.flag_stop = 0
            elif self.threshold_choices.get() == "HG":
                threshold_old = self.threshold_LG
                flag_stop_old = self.flag_stop
                for threshold_aux in self.threshold_x_shape_in_trigger_plot:
                    self.var_threshold_LG.set("%s" % threshold_aux)
                    print(threshold_aux)
                    self.start_it()
                    self.flag_stop = 0

            with open(self.file_to_analyze_rate,"wb") as trigger_file:
                pickle.dump([self.list_mean_cosmicray_rate_HG, self.list_std_cosmicray_rate_HG ,self.list_mean_cosmicray_rate_LG ,self.list_std_cosmicray_rate_LG,self.list_mean_cosmicray_rate_tot,self.list_std_cosmicray_rate_tot,self.list_mean_trigger_rate_ampli,self.list_std_trigger_rate_ampli,self.list_mean_trigger_rate_tot,self.list_std_trigger_rate_tot],trigger_file)

            #disable button drw histogramm, start and draw trigger rate
            self.b3.config(state="disabled")  # disable the start button to avoid multiple start event display
            self.b7.config(state="disabled")  # disable the start button to avoid multiple start event display
            self.b12.config(state="disabled")  # disable the start button to avoid multiple start event display


            '''initialiser the window,canvas,buttons where the trigger rate will be plot'''
            self.fen3 = Toplevel(self.fen1)  # draw the children window of the window fen1

            self.b13 = Button(self.fen3, text='Close', command=self._close_window_trigger_rate_and_cosmic_flux)
            self.b13.grid(row=8, column=7, sticky='NSEW')

            self._trace_trigger_rate_and_cosmic_flux()  # draw this trigger rate

            self.fen3.protocol("WM_DELETE_WINDOW",
                               self._close_window_trigger_rate_and_cosmic_flux)  # this is reliated to the function _close_window_histogramm

            #reinitialise parameters
            self.list_mean_cosmicray_rate_HG = []
            self.list_std_cosmicray_rate_HG = []
            self.list_mean_cosmicray_rate_LG = []
            self.list_std_cosmicray_rate_LG = []
            self.list_mean_cosmicray_rate_tot = []
            self.list_std_cosmicray_rate_tot = []

            self.list_mean_trigger_rate_ampli = []
            self.list_std_trigger_rate_ampli = []
            self.list_mean_trigger_rate_tot = []
            self.list_std_trigger_rate_tot = []
            self.flag_draw_trigger_rate = False
            if self.threshold_choices.get() == "LG":
                self.threshold_LG = threshold_old
                self.flag_stop = flag_stop_old
            elif self.threshold_choices.get() == "HG":
                self.threshold_HG = threshold_old
                self.flag_stop = flag_stop_old


            # this is to adapt size of the widgets,canvas,... with the size of window
            self.fen3.rowconfigure(0, weight=1)
            self.fen3.rowconfigure(1, weight=1)
            self.fen3.rowconfigure(2, weight=1)
            self.fen3.rowconfigure(3, weight=1)
            self.fen3.rowconfigure(4, weight=1)
            self.fen3.rowconfigure(5, weight=1)
            self.fen3.rowconfigure(6, weight=1)
            self.fen3.rowconfigure(7, weight=1)
            self.fen3.rowconfigure(8, weight=1)
            self.fen3.columnconfigure(0, weight=1)
            self.fen3.columnconfigure(1, weight=1)
            self.fen3.columnconfigure(2, weight=1)
            self.fen3.columnconfigure(3, weight=1)
            self.fen3.columnconfigure(5, weight=1)
            self.fen3.columnconfigure(6, weight=1)
            self.fen3.columnconfigure(7, weight=1)


    def _trace_trigger_rate_and_cosmic_flux(self):
        '''this function is to draw histogram in amplitude and tot of the pixels selected
                since the event display started and in the intervalle of 4s'''

        self.fig_trigger = plt.figure(facecolor="green")
        self.axs_trigger_0 = self.fig_trigger.add_subplot(221)
        self.axs_trigger_1 = self.fig_trigger.add_subplot(222)
        self.axs_trigger_2 = self.fig_trigger.add_subplot(223)
        self.axs_trigger_3 = self.fig_trigger.add_subplot(224)

        print("rate parameters for plot")
        print("threshold_x_shape_in_trigger_plot===",self.threshold_x_shape_in_trigger_plot)
        print("list_mean_cosmicray_rate_HG===",self.list_mean_cosmicray_rate_HG)
        print("list_mean_cosmicray_rate_tot===",self.list_mean_cosmicray_rate_tot)
        print("list_mean_trigger_rate_ampli===",self.list_mean_trigger_rate_ampli)
        print("list_mean_trigger_rate_tot===",self.list_mean_trigger_rate_tot)

        self.list_std_trigger_rate_ampli=[0 if inst is 0 else np.log(inst) for inst in self.list_std_trigger_rate_ampli]
        self.list_std_trigger_rate_tot = [0 if inst is 0 else np.log(inst) for inst in self.list_std_trigger_rate_tot]

        self.threshold_x_shape_in_trigger_plot_in_PE_LG=[(threshold_LG - np.mean(self.pedestal_LG))/np.mean(self.Gain_LG) for threshold_LG in self.threshold_x_shape_in_trigger_plot]
        self.threshold_x_shape_in_trigger_plot_in_PE_HG = [
            (threshold_HG - np.mean(self.pedestal_HG)) / np.mean(self.Gain_HG) for threshold_HG in
            self.threshold_x_shape_in_trigger_plot]
        self.threshold_x_shape_in_trigger_plot_in_PE_LG=['%s'%e for e in self.threshold_x_shape_in_trigger_plot_in_PE_LG]
        self.threshold_x_shape_in_trigger_plot_in_PE_HG = ['%s' % e for e in
                                                           self.threshold_x_shape_in_trigger_plot_in_PE_HG]

        self.axs_trigger_0.errorbar(self.threshold_x_shape_in_trigger_plot,self.list_mean_trigger_rate_ampli,self.list_std_trigger_rate_ampli,fmt='-o')

        self.axs_trigger_1.errorbar(self.threshold_x_shape_in_trigger_plot, self.list_mean_trigger_rate_tot,
                                    self.list_std_trigger_rate_tot, fmt='-o')

        self.axs_trigger_2.errorbar(self.threshold_x_shape_in_trigger_plot, self.list_mean_cosmicray_rate_HG,
                                    self.list_std_cosmicray_rate_HG, fmt='-o')

        self.axs_trigger_3.errorbar(self.threshold_x_shape_in_trigger_plot, self.list_mean_cosmicray_rate_tot,
                                    self.list_std_cosmicray_rate_tot, fmt='-o')

        self.fig_trigger.tight_layout()

        self.axs_trigger_0.set_yscale("log")
        self.axs_trigger_0.set_title("Trigger in amplitude")
        self.axs_trigger_0.grid()
        #self.axs_trigger_0.set_xlabel(" IN DAC")
        self.axs_trigger_0_prime=self.axs_trigger_0.twiny()
        self.axs_trigger_0_prime.set_xlim(self.axs_trigger_0.get_xlim())
        self.axs_trigger_0_prime.set_xticks(self.threshold_x_shape_in_trigger_plot)
        self.axs_trigger_0_prime.set_xticklabels(self.threshold_x_shape_in_trigger_plot_in_PE_HG)
        #self.axs_trigger_0_prime.set_xlabel(" IN PE")


        self.axs_trigger_1.set_yscale("log")
        self.axs_trigger_1.set_title("Trigger in tot")
        self.axs_trigger_1.grid()
        #self.axs_trigger_1.set_xlabel(" IN DAC")
        self.axs_trigger_1_prime = self.axs_trigger_1.twiny()
        self.axs_trigger_1_prime.set_xlim(self.axs_trigger_1.get_xlim())
        self.axs_trigger_1_prime.set_xticks(self.threshold_x_shape_in_trigger_plot)
        self.axs_trigger_1_prime.set_xticklabels(self.threshold_x_shape_in_trigger_plot_in_PE_HG)
        #self.axs_trigger_1_prime.set_xlabel(" IN PE")

        self.axs_trigger_2.set_yscale("log")
        self.axs_trigger_2.set_title("CR flux in amplitude")
        self.axs_trigger_2.grid()
        #self.axs_trigger_2.set_xlabel(" IN DAC")
        self.axs_trigger_2_prime = self.axs_trigger_2.twiny()
        self.axs_trigger_2_prime.set_xlim(self.axs_trigger_2.get_xlim())
        self.axs_trigger_2_prime.set_xticks(self.threshold_x_shape_in_trigger_plot)
        self.axs_trigger_2_prime.set_xticklabels(self.threshold_x_shape_in_trigger_plot_in_PE_LG)
        #self.axs_trigger_2_prime.set_xlabel(" IN PE")

        self.axs_trigger_3.set_yscale("log")
        self.axs_trigger_3.set_title("CR flux in tot")
        self.axs_trigger_3.grid()
        #self.axs_trigger_3.set_xlabel(" IN DAC")
        self.axs_trigger_3_prime = self.axs_trigger_3.twiny()
        self.axs_trigger_3_prime.set_xlim(self.axs_trigger_3.get_xlim())
        self.axs_trigger_3_prime.set_xticks(self.threshold_x_shape_in_trigger_plot)
        self.axs_trigger_3_prime.set_xticklabels(self.threshold_x_shape_in_trigger_plot_in_PE_LG)
        #self.axs_trigger_3_prime.set_xlabel(" IN PE")

        self.canvas_trigger = FigureCanvasTkAgg(self.fig_trigger, master=self.fen3)

        self.canvas_trigger.show()

        self.canvas_trigger.get_tk_widget().grid(row=1, column=1, rowspan=5, columnspan=6, padx=10, pady=5,
                                               sticky='NSEW')

        self.toolbar_frame_trigger = Frame(self.fen3, highlightcolor="red", highlightthickness=1,
                                         highlightbackground="blue")
        self.toolbar_frame_trigger.grid(row=0, column=1)
        self.toolbar_trigger = NavigationToolbar2Tk(self.canvas_trigger, self.toolbar_frame_trigger)

        self.canvas_trigger._tkcanvas.grid(row=1, column=1, rowspan=5, columnspan=6, padx=10, pady=5, sticky='NSEW')

        def on_key_event(event):
            print('you pressed %s' % event.key)
            key_press_handler(event, self.canvas_trigger, self.toolbar_trigger)

            self.canvas_trigger.mpl_connect('key_press_event', on_key_event)

        self.fen3.attributes("-topmost", True)  # this is to maintain fen3 in front of all windows

        #while (self.fen3 is not None) and self.fen3.winfo_exists():


    def _close_window_trigger_rate_and_cosmic_flux(self):
        '''This function is to close the child window where histogramm have been plotting'''

        # activate button drw histogramm, start and draw trigger rate
        self.b3.config(state="active")  # disable the start button to avoid multiple start event display
        self.b7.config(state="active")  # disable the start button to avoid multiple start event display
        self.b12.config(state="active")  # disable the start button to avoid multiple start event display

        self.fen3.destroy()  # this is necessary on Windows to prevent
        self.fen3 = None

    # Close the socket server

    def daq_tdm_Applib_slotArray_v1(self,aux_name_file_recorded_by_babymind):

        #------------------------------------------------------------------------------
        # MAIN SCRIPT FUNCTIONS
        # ------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------
        # --- fill there the config file names. just one in the array

        #if self.daq_tdm_Applib==0:
        cfgfilename_0 = self.config_file_aux_0
        cfgfilename_1 = self.config_file_aux_1

        #This will launch the TDM DAQ for MCB on slot 0 & SLAVE on slot 2 trough GTX chain
        # Configure Master Clock FEB & TDM...
        self.comm.Communicate('App.TDMPrepareDaq({}, "{}", {},{}, {}, {},{},{})\r'.format(self.MCB_BOARD_ID
                                                                                     , cfgfilename_0, self.MCB_BOARD_ID
                                                                                     , self.l_enableGtrig
                                                                                     , self.l_enableGtrigOnlyOnSpill
                                                                                     , self.l_enableReadoutOnSpillGate
                                                                                     , self.l_syncResetEn, self.beforeConfigure))

        #"Prepare SYNC on slave slots")
        self.comm.Communicate('App.ChainSetCheckSyncAndGtxs("{}|{}")\r'.format(self._boardIds[0], self._boardIds[1]))


        #"prepare DAQ from last slot to USB slot 0")
        self.comm.Communicate('App.TDMPrepareDaq({}, "{}", {},{}, {}, {},{},{})\r'.format(self._boardIds[0]
                                                                                     , cfgfilename_0, self.MCB_BOARD_ID
                                                                                     , self.l_enableGtrig
                                                                                     , self.l_enableGtrigOnlyOnSpill
                                                                                     , self.l_enableReadoutOnSpillGate
                                                                                     , self.l_syncResetEn, self.beforeConfigure))

        self.comm.Communicate('App.TDMPrepareDaq({}, "{}", {},{}, {}, {},{},{})\r'.format(self._boardIds[1]
                                                                                     , cfgfilename_0, self.MCB_BOARD_ID
                                                                                     , self.l_enableGtrig
                                                                                     , self.l_enableGtrigOnlyOnSpill
                                                                                     , self.l_enableReadoutOnSpillGate
                                                                                     , self.l_syncResetEn, self.beforeConfigure))

        #Starting DAQ on all slot with USB on SLOT0")
        self.comm.Communicate(
            'BoardLib.SetVariable("Board.UsbParam.FileLimit", {})\r'.format(self._FILE_LIMIT))

        l_daqFile = aux_name_file_recorded_by_babymind
        self.comm.Communicate(
            'App.TDMStartDaqs("{}|{}", "{}", {})\r'.format(self._boardIds[0], self._boardIds[1], l_daqFile, self.MCB_BOARD_ID))


    def pointy_top_hex(self,center_x, center_y, size_edge_to_edge, i):
        """Define coordinate of edges' pixels with pointy up """
        rayon = size_edge_to_edge / 2
        angle_deg = 60 * i + 30
        angle_rad = pi / 180 * angle_deg
        Point = (center_x + rayon * cos(angle_rad),
                 center_y + rayon * sin(angle_rad))
        return Point

    def make_mini_cam_mathieu(self, size_edge_to_edge):
        mini_cam_mathieu = {}
        with open("D:/resultat_acquisition_babymind/fichier_config_mini_camera_mathieu.txt","r") as file:
            line = file.readline().split("\n")[0].split("\t")
            while line[0] != "":
                pixel_id = float(line[0])
                pixel_center = (float(line[1]), float(line[2]))

                xs = []
                ys = []
                for i in range(6):
                    Point = self.pointy_top_hex(pixel_center[0], pixel_center[1], size_edge_to_edge, i)
                    xs.append(Point[0])
                    ys.append(Point[1])

                mini_cam_mathieu[pixel_id] = [(xs, ys), pixel_center]

                line = file.readline().split("\n")[0].split("\t")

        return mini_cam_mathieu

    def make_mini_cam_mathieu_with_node(self, size_edge_to_edge):
        '''
        Create and Make the mapping of minicamera
        '''

        mini_cam_mathieu_with_node = {}
        with open("D:/resultat_acquisition_babymind/mapping_mini_cam_with_node/MappingTable_MiniCamera.txt","r") as file:
            line=file.readline()
            line = file.readline().split("\n")[0].split("\t")
            while line[0] != "":
                pixel_id = float(line[6])
                pixel_center = (float(line[7]), float(line[8]))

                xs = []
                ys = []
                for i in range(6):
                    Point = self.pointy_top_hex(pixel_center[0], pixel_center[1], size_edge_to_edge, i)
                    xs.append(Point[0])
                    ys.append(Point[1])

                mini_cam_mathieu_with_node[pixel_id] = [(xs, ys), pixel_center]


                line = file.readline().split("\n")[0].split("\t")

        dict_pixels_ids_1 = {117: 0, 84: 1, 116: 2, 113: 3, 111: 4, 86: 5, 85: 6, 90: 7, 119: 8, 112: 9, 110: 10, 129: 11,
                             72: 12, 87: 13, 88: 14, 91: 15, 118: 16, 115: 17, 109: 18, 128: 19, 125: 20, 123: 21,
                             74: 22, 73: 23, 78: 24, 89: 25, 95: 26, 94: 27, 105: 28, 114: 29, 108: 30, 131: 31,
                             124: 32, 122: 33, 75: 34, 76: 35, 79: 36, 93: 37, 92: 38, 48: 39, 104: 40, 101: 41,
                             99: 42, 130: 43, 127: 44, 121: 45, 77: 46, 83: 47, 82: 48, 50: 49, 49: 50, 54: 51,
                             107: 52, 100: 53, 98: 54, 141: 55, 126: 56, 120: 57, 81: 58, 80: 59, 60: 60, 51: 61, 52: 62,
                             55: 63, 106: 64, 103: 65, 97: 66, 140: 67, 137: 68, 135: 69, 62: 70, 61: 71, 66: 72, 53: 73,
                             59: 74, 58: 75, 10: 76, 102: 77, 96: 78, 143: 79, 136: 80, 134: 81, 63: 82, 64: 83, 67: 84,
                             57: 85, 56: 86, 6: 87, 7: 88, 11: 89, 8: 90, 142: 91, 139: 92, 133: 93, 65: 94, 71: 95,
                             70: 96, 46: 97, 0: 98, 1: 99, 4: 100, 5: 101, 9: 102, 22: 103, 138: 104, 132: 105,
                             69: 106, 68: 107, 42: 108, 43: 109, 47: 110, 44: 111, 2: 112, 3: 113, 18: 114, 19: 115,
                             23: 116, 20: 117, 36: 118, 37: 119, 40: 120, 41: 121, 45: 122, 34: 123, 12: 124, 13: 125,
                             16: 126, 17: 127, 21: 128, 38: 129, 39: 130, 30: 131, 31: 132, 35: 133, 32: 134, 14: 135,
                             15: 136, 24: 137, 25: 138, 28: 139, 29: 140, 33: 141, 26: 142, 27: 143}
        dict_pixels_ids_1=dict((item,key) for (key,item) in dict_pixels_ids_1.items())
        mini_cam_mathieu_with_node=dict((dict_pixels_ids_1[key],item) for (key,item) in mini_cam_mathieu_with_node.items())




        return mini_cam_mathieu_with_node


    def find_neighboors_pixels_by_scipy_method(self):
        """uses a KD-Tree to quickly find nearest neighbors of the pixels in a
            camera. This function can be used to find the neighbor pixels if
            such a list is not already present in the file.

            Parameters
            ----------
            pix_x : array_like
                x position of each pixel
            pix_y : array_like
                y position of each pixels
            rad : float
                radius to consider neighbor it should be slightly larger
                than the pixel diameter.

            Returns
            -------
            array of neighbor indices in a list for each pixel
            """

        rad=23.2 + 1 + 4
        pixels=self.reatribute_id_pixels
        list_centers_xs = []
        list_centers_ys = []
        list_pixels_id=[]
        for pixels_id, polygons_data in pixels.items():
            list_centers_xs.append(polygons_data[1][0])
            list_centers_ys.append(polygons_data[1][1])
            list_pixels_id.append(pixels_id)

        points = np.array([list_centers_xs, list_centers_ys]).T
        indices = np.arange(len(list_centers_xs))
        kdtree = KDTree(points)
        neighbors = [kdtree.query_ball_point(p, r=rad) for p in points]
        for nn, ii in zip(neighbors, indices):
            nn.remove(ii)  # get rid of the pixel itself

        print(neighbors)
        return neighbors

    def find_neighboors_pixels_by_my_method(self):
        """uses a KD-Tree to quickly find nearest neighbors of the pixels in a
            camera. This function can be used to find the neighbor pixels if
            such a list is not already present in the file.

            Parameters
            ----------
            pix_x : array_like
                x position of each pixel
            pix_y : array_like
                y position of each pixels
            rad : float
                radius to consider neighbor it should be slightly larger
                than the pixel diameter.

            Returns
            -------
            array of neighbor indices in a list for each pixel
            """

        rad=23.2 + 1 + 4
        pixels=self.reatribute_id_pixels
        dict_centers_xs_ys={}
        list_pixels_id=[]
        list_centers_xs_ys = []
        neighboors={}
        for pixels_id, polygons_data in pixels.items():
            centers_xs =polygons_data[1][0]
            centers_ys=polygons_data[1][1]
            dict_centers_xs_ys[pixels_id]=(centers_xs,centers_ys)
            list_centers_xs_ys.append((centers_xs,centers_ys))
            list_pixels_id.append(pixels_id)

        keys=dict_centers_xs_ys.keys()
        values=dict_centers_xs_ys.values()
        #print(dict_centers_xs_ys)
        for pixels_id,centers_in_dict in dict_centers_xs_ys.items():
            list_centers_xs_ys.remove(centers_in_dict)
            for centers_in_list in list_centers_xs_ys:
                if (sqrt((centers_in_dict[0] - centers_in_list[0])**2+(centers_in_dict[1] - \
                                                                          centers_in_list[1])**2)-rad) <= 0:
                    if not pixels_id in neighboors.keys():
                        neighboors[pixels_id]=[list(keys)[list(values).index(centers_in_list)]]
                    else:
                        neighboors[pixels_id].append(list(keys)[list(values).index(centers_in_list)])

            list_centers_xs_ys.append(centers_in_dict)

        self.neighboors=neighboors
        '''
        neighboors={0: [1, 6, 46, 47, 44, 56], 1: [2, 6, 7, 4, 44, 0], 2: [3, 4, 34, 44, 45, 1], 3: [4, 5, 12, 18, 34, 2],
            6: [7, 58, 59, 56, 0, 1], 7: [4, 10, 11, 58, 1, 6], 4: [5, 11, 1, 2, 3, 7], 5: [11, 8, 9, 18, 3, 4],
            10: [11, 58, 102, 103, 106, 7], 11: [8, 102, 7, 4, 5, 10], 8: [9, 96, 102, 142, 5, 11], 9: [18, 19, 22, 142, 5, 8],
            12: [13, 18, 34, 35, 32, 3], 13: [14, 18, 19, 16, 32, 12], 14: [15, 16, 32, 33, 13], 15: [16, 17, 14], 18: [19, 3, 5, 9, 12, 13],
            19: [16, 22, 23, 9, 13, 18], 16: [17, 23, 13, 14, 15, 19], 17: [23, 20, 21, 15, 16], 22: [23, 138, 139, 142, 9, 19],
            23: [20, 138, 19, 16, 17, 22], 20: [21, 132, 138, 17, 23], 21: [17, 20], 24: [25, 30, 39], 25: [26, 30, 31, 28, 24],
            26: [27, 28, 25], 27: [28, 29, 26], 30: [31, 39, 41, 45, 24, 25], 31: [28, 34, 35, 45, 25, 30], 28: [29, 35, 25, 26, 27, 31],
            29: [35, 32, 33, 27, 28], 34: [35, 45, 2, 3, 12, 31], 35: [32, 12, 31, 28, 29, 34], 32: [33, 12, 13, 14, 29, 35],
            33: [14, 29, 32], 36: [37, 42, 68], 37: [38, 42, 43, 40, 36], 38: [39, 40, 37], 39: [40, 41, 24, 30, 38],
            42: [43, 70, 71, 68, 36, 37], 43: [40, 46, 47, 70, 37, 42], 40: [41, 47, 37, 38, 39, 43], 41: [47, 44, 45, 30, 39, 40],
            46: [47, 56, 57, 70, 0, 43], 47: [44, 0, 43, 40, 41, 46], 44: [45, 0, 1, 2, 41, 47], 45: [2, 30, 31, 34, 41, 44],
            48: [49, 54, 94, 95, 92, 104], 49: [50, 54, 55, 52, 92, 48], 50: [51, 52, 82, 92, 93, 49], 51: [52, 53, 60, 66, 82, 50],
            54: [55, 106, 107, 104, 48, 49], 55: [52, 58, 59, 106, 49, 54], 52: [53, 59, 49, 50, 51, 55], 53: [59, 56, 57, 66, 51, 52],
            58: [59, 106, 6, 7, 10, 55], 59: [56, 6, 55, 52, 53, 58], 56: [57, 0, 6, 46, 53, 59], 57: [66, 67, 70, 46, 53, 56],
            60: [61, 66, 82, 83, 80, 51], 61: [62, 66, 67, 64, 80, 60], 62: [63, 64, 80, 81, 61], 63: [64, 65, 62],
            66: [67, 51, 53, 57, 60, 61], 67: [64, 70, 71, 57, 61, 66], 64: [65, 71, 61, 62, 63, 67], 65: [71, 68, 69, 63, 64],
            70: [71, 42, 43, 46, 57, 67], 71: [68, 42, 67, 64, 65, 70], 68: [69, 36, 42, 65, 71], 69: [65, 68], 72: [73, 78, 87],
            73: [74, 78, 79, 76, 72], 74: [75, 76, 73], 75: [76, 77, 74], 78: [79, 87, 89, 93, 72, 73], 79: [76, 82, 83, 93, 73, 78],
            76: [77, 83, 73, 74, 75, 79], 77: [83, 80, 81, 75, 76], 82: [83, 93, 50, 51, 60, 79], 83: [80, 60, 79, 76, 77, 82],
            80: [81, 60, 61, 62, 77, 83], 81: [62, 77, 80], 84: [85, 90, 116], 85: [86, 90, 91, 88, 84], 86: [87, 88, 85],
            87: [88, 89, 72, 78, 86], 90: [91, 118, 119, 116, 84, 85], 91: [88, 94, 95, 118, 85, 90], 88: [89, 95, 85, 86, 87, 91],
            89: [95, 92, 93, 78, 87, 88], 94: [95, 104, 105, 118, 48, 91], 95: [92, 48, 91, 88, 89, 94], 92: [93, 48, 49, 50, 89, 95],
            93: [50, 78, 79, 82, 89, 92], 96: [97, 102, 142, 143, 140, 8], 97: [98, 102, 103, 100, 140, 96], 98: [99, 100, 130, 140, 141, 97],
            99: [100, 101, 108, 114, 130, 98], 102: [103, 10, 11, 8, 96, 97], 103: [100, 106, 107, 10, 97, 102], 100: [101, 107, 97, 98, 99, 103],
            101: [107, 104, 105, 114, 99, 100], 106: [107, 10, 54, 55, 58, 103], 107: [104, 54, 103, 100, 101, 106],
            104: [105, 48, 54, 94, 101, 107], 105: [114, 115, 118, 94, 101, 104], 108: [109, 114, 130, 131, 128, 99],
            109: [110, 114, 115, 112, 128, 108], 110: [111, 112, 128, 129, 109], 111: [112, 113, 110], 114: [115, 99, 101, 105, 108, 109],
            115: [112, 118, 119, 105, 109, 114], 112: [113, 119, 109, 110, 111, 115], 113: [119, 116, 117, 111, 112],
            118: [119, 90, 91, 94, 105, 115], 119: [116, 90, 115, 112, 113, 118], 116: [117, 84, 90, 113, 119], 117: [113, 116],
            120: [121, 126, 135], 121: [122, 126, 127, 124, 120], 122: [123, 124, 121], 123: [124, 125, 122],
            126: [127, 135, 137, 141, 120, 121], 127: [124, 130, 131, 141, 121, 126], 124: [125, 131, 121, 122, 123, 127],
            125: [131, 128, 129, 123, 124], 130: [131, 141, 98, 99, 108, 127], 131: [128, 108, 127, 124, 125, 130],
            128: [129, 108, 109, 110, 125, 131], 129: [110, 125, 128], 132: [133, 138, 20], 133: [134, 138, 139, 136, 132],
            134: [135, 136, 133], 135: [136, 137, 120, 126, 134], 138: [139, 22, 23, 20, 132, 133], 139: [136, 142, 143, 22, 133, 138],
            136: [137, 143, 133, 134, 135, 139], 137: [143, 140, 141, 126, 135, 136], 142: [143, 8, 9, 22, 96, 139],
            143: [140, 96, 139, 136, 137, 142], 140: [141, 96, 97, 98, 137, 143], 141: [98, 126, 127, 130, 137, 140]}

        '''
    def draw_camera_pixel_ids(self,xs_center, ys_center, pixels_id, axes):
        """draw the camera pixels id in the camera"""

        axes.text(xs_center, ys_center, pixels_id, fontsize=10, ha='center')


    def draw_pixel_center(self,list_centers_xs, list_centers_ys, axes):
        """draw the camera'pixels centers """

        axes.plot(list_centers_xs, list_centers_ys, 'y+')


    def plot_pixels_grid_bis(self,pixels, data_from_electronics):

        #cmap1 = cm.YlOrBr
        #norm1 = colors.Normalize(np.min(data_from_electronics), np.max(data_from_electronics))

        if self.box_choice.get() == "Temp":
            self.norm1 = matplotlib.colors.Normalize(0,35)
        else:
            self.norm1 = matplotlib.colors.Normalize(np.min(data_from_electronics), np.max(data_from_electronics))
        self.cmap1 = matplotlib.cm.ScalarMappable(norm=self.norm1, cmap=matplotlib.cm.jet)
        self.cmap1.set_array([])

        for pixel_id,polygones in self.dict_polygones.items():
            polygones.set_facecolor(self.cmap1.to_rgba(data_from_electronics[int(pixel_id)]))
            self.axes_fen1.add_patch(polygones)

        self.cb_fen1.update_normal(self.cmap1)
        self.cb_fen1.draw_all()
        self.axes_fen1.axis('equal')
        self.fig_fen1.savefig("D:/resultat_acquisition_babymind/figures/fig_%s"%self.number_figure)
        self.number_figure+=1
        # if you want to draw the center of the pixels
        # draw_pixel_center(list_centers_xs, list_centers_ys)

        #free memory

    def plots_hex_in_canvas_pdp(self):

        if self.box_choice.get() == "Temp":

            self._update_box_messages("We are reading temperature of PDP")
            print(self.usb2can.data_temperature)
            self.plot_pixels_grid_bis(self.reatribute_id_pixels,
                                                            self.usb2can.data_temperature)
            self.fen1.after(3000, self.start_it)
        else:

            if self.value_hg_or_lg.get() == "HG":
                self._update_box_messages("We are in HG")
                self._update_box_messages(self.list_of_pixels_on_events)
                print(self.data_electronics_HG)
                self.plot_pixels_grid_bis(self.reatribute_id_pixels,
                                                                         self.data_electronics_HG)
            elif self.value_hg_or_lg.get() == "LG":
                self._update_box_messages("We are in LG")
                self._update_box_messages(self.list_of_pixels_on_events)
                print(self.data_electronics_LG)
                self.plot_pixels_grid_bis(self.reatribute_id_pixels,
                                                                         self.data_electronics_LG)

            elif self.value_hg_or_lg.get() == "TOT":
                self._update_box_messages("We are in TOT")
                self._update_box_messages(self.list_of_pixels_on_events)
                print(self.data_electronics_tot)
                self.plot_pixels_grid_bis(self.reatribute_id_pixels,
                                                                         self.data_electronics_tot)
        def on_key_event(event):
            print('you pressed %s' % event.key)
            key_press_handler(event, self.canvas_fen1, self.toolbar_fen1)

        self.canvas_fen1.draw()
        self.canvas_fen1.mpl_connect('key_press_event', on_key_event)
        self.canvas_fen1.flush_events()

        # free memory
        self.clear_figure(self.axes_fen1)
        if self.box_choice.get() == "Temp":
            del self.usb2can.data_temperature
        else:
            if self.value_hg_or_lg.get() == "HG":
                del self.data_electronics_HG
            elif self.value_hg_or_lg.get() == "LG":
                del self.data_electronics_LG
            elif self.value_hg_or_lg.get() == "TOT":
                del self.data_electronics_tot

    def clear_figure(self,axes):

        plt.cla()
        axes.clear()
        #self.cb_fen1.remove()
        #plt.close()
        # del self.fig,self.axes

    def trigger_sofware_in_pixel_configuration(self,dict_pixelid_values):
        '''This function is to apply the trigger condition due to the pixel configuration'''

        self.software_trigger_in_pixel_configuration = int(self.entr4.get())


        if self.software_trigger_in_pixel_configuration == 1:
            self.list_pixels_triggered = list(dict_pixelid_values.keys())
        elif self.software_trigger_in_pixel_configuration == 2:
            self.list_pixels_triggered = [pixels_test for pixels_test in list(dict_pixelid_values.keys()) \
                                     if not set(self.neighboors[pixels_test]).isdisjoint \
                    (list(dict_pixelid_values.keys()))]
        elif self.software_trigger_in_pixel_configuration == 3:
            self.list_pixels_triggered = []
            for pixels_test in list(dict_pixelid_values.keys()):
                if not set(self.neighboors[pixels_test]).isdisjoint \
                            (list(dict_pixelid_values.keys())):
                    iter = list(dict_pixelid_values.keys())
                    iter.remove(pixels_test)
                    for pixels in list(set(list(dict_pixelid_values.keys())).intersection(self.neighboors[pixels_test])):
                        if not set(self.neighboors[pixels]).isdisjoint \
                                    (iter):
                            self.list_pixels_triggered.append(pixels_test)
                            break

    def export_data_electronis_values(self):

        if self.entr5.get()=='': #attribute value 0 to entry 5 if it is equal to 0
            self.entr5.delete(0,END)
            self.entr5.insert(0,"0")

        self.time_allowed_to_display_events = int(self.entr10.get()) * 1e-3
        duration=0
        dict_data_electronics_LG={}
        dict_data_electronics_HG = {}
        dict_data_electronics_tot = {}
        start_time = time.time()
        self.old_dict_pixelid_values_HG_for_histo_local = dict(
            (i, Hist1D_local(self.bin_array_HG[i], 0, 5000, i)) for i in np.arange(144))
        self.old_dict_pixelid_values_LG_for_histo_local = dict(
            (i, Hist1D_local(self.bin_array_LG[i], 0, 5000, i)) for i in np.arange(144))
        self.old_dict_pixelid_values_tot_for_histo_local = dict(
            (i, Hist1D_local(self.bin_array_tot[i], 0, 5000, i)) for i in np.arange(144))

        while duration < self.time_allowed_to_display_events:

            where = self.new_file1.tell()
            try:
                line = pickle.load(self.new_file1)
                #print(line)
                if line=="END":
                    while self.flag_can_stop_all==0:
                        time.sleep(2)

                    print("End of the new file")
                    print("Event display is finish")
                    stop_test = time.time()
                    print('my test duration in step 3====', stop_test - self.start_test)
                    print('my test duration in step glopbal (duration since begining until end of display)====', stop_test - self.start_test_global)
                    self.stop_it()
                    break
            except EOFError:
                line=0
                pass

            if line==0:
                time.sleep(1)
                self.new_file1.seek(where)
            else:
                #print("succes read new file")
                #print(line)
                if line[0]=="Amplitude":
                    event_data_amplitude_LG=line[1]
                    event_data_amplitude_HG=line[2]
                    #print(line[0])
                    if event_data_amplitude_LG != {}:

                        list_tuples_LG = [var[0] for var in list(event_data_amplitude_LG.values())]
                        dict_pixelid_values_LG = {}
                        for (x, y) in enumerate(list_tuples_LG):

                            if y[0] not in dict_pixelid_values_LG.keys():
                                dict_pixelid_values_LG[y[0]] = [y[1]]

                            else:
                                dict_pixelid_values_LG[y[0]].append(y[1])

                        # the local and global histogram will be performing here
                        for keys, data in dict_pixelid_values_LG.items():
                            self.old_dict_pixelid_values_LG_for_histo_global[keys].fill(data, keys)
                            self.old_dict_pixelid_values_LG_for_histo_local[keys].fill(data, keys)

                        # data_electronics_LG = np.array([random.randint(0, self.threshold_DAC) for r in range(144)])
                        data_electronics_LG = np.zeros(144)

                        if self.box_choice.get()=="DAC": #test if i want to display events in the DAc mode

                            dict_pixelid_values_LG = {keys: np.max(dict_pixelid_values_LG[keys]) for keys in
                                                      dict_pixelid_values_LG.keys()}
                            # print(dict_pixelid_values_LG)

                            self.trigger_sofware_in_pixel_configuration(dict_pixelid_values_LG) #test trigger pixels configuration


                            #sum_to_have_more_event_ligthed_LG = np.sum(list(dict_pixelid_values_LG.values()))
                            sum_to_have_more_event_ligthed_LG = np.sum([dict_pixelid_values_LG[item] for item in
                                                                           self.list_pixels_triggered])


                            if sum_to_have_more_event_ligthed_LG >= int(self.entr5.get()): #test trigger pixels sum values

                                # data_electronics_LG[list(dict_pixelid_values_LG.keys())] = list(dict_pixelid_values_LG.values())
                                data_electronics_LG[self.list_pixels_triggered] = [dict_pixelid_values_LG[item] for item in
                                                                               self.list_pixels_triggered]

                                dict_data_electronics_LG[sum_to_have_more_event_ligthed_LG] = data_electronics_LG


                        elif self.box_choice.get()=="PE":

                            dict_pixelid_values_LG = {keys: ((np.max(dict_pixelid_values_LG[keys]) \
                                                              - self.pedestal_LG[keys])/self.Gain_LG[keys]) for keys in
                                                      dict_pixelid_values_LG.keys() if \
                                                      np.max(dict_pixelid_values_LG[keys])>=self.pedestal_LG[keys]}
                            # print(dict_pixelid_values_LG)

                            self.trigger_sofware_in_pixel_configuration(
                                dict_pixelid_values_LG)  # test trigger pixels configuration

                            # sum_to_have_more_event_ligthed_LG = np.sum(list(dict_pixelid_values_LG.values()))
                            sum_to_have_more_event_ligthed_LG = np.sum([dict_pixelid_values_LG[item] for item in
                                                                        self.list_pixels_triggered])

                            if sum_to_have_more_event_ligthed_LG >= int(self.entr5.get()):  # test trigger pixels sum values

                                # data_electronics_LG[list(dict_pixelid_values_LG.keys())] = list(dict_pixelid_values_LG.values())
                                data_electronics_LG[self.list_pixels_triggered] = [dict_pixelid_values_LG[item] for \
                                                                                   item in self.list_pixels_triggered]

                                dict_data_electronics_LG[sum_to_have_more_event_ligthed_LG] = data_electronics_LG

                    if event_data_amplitude_HG != {}:
                        #print(list_tuples_HG)
                        list_tuples_HG = [var[0] for var in list(event_data_amplitude_HG.values())]
                        dict_pixelid_values_HG = {}
                        for (x, y) in enumerate(list_tuples_HG):

                            if y[0] not in dict_pixelid_values_HG.keys():
                                dict_pixelid_values_HG[y[0]] = [y[1]]

                            else:
                                dict_pixelid_values_HG[y[0]].append(y[1])

                        # the local and global histogram will be performing here
                        for keys, data in dict_pixelid_values_HG.items():
                            self.old_dict_pixelid_values_HG_for_histo_global[keys].fill(data, keys)
                            self.old_dict_pixelid_values_HG_for_histo_local[keys].fill(data, keys)

                        # data_electronics_HG = np.array([random.randint(0, self.threshold_DAC) for r in range(144)])
                        data_electronics_HG = np.zeros(144)

                        if self.box_choice.get()=="DAC": #test if i want to display events in the DAc mode

                            dict_pixelid_values_HG = {keys: np.max(dict_pixelid_values_HG[keys]) for keys in
                                                      dict_pixelid_values_HG.keys()}
                            # print(dict_pixelid_values_HG)

                            self.trigger_sofware_in_pixel_configuration(dict_pixelid_values_HG) #test trigger pixels configuration


                            #sum_to_have_more_event_ligthed_HG = np.sum(list(dict_pixelid_values_HG.values()))
                            sum_to_have_more_event_ligthed_HG = np.sum([dict_pixelid_values_HG[item] for item in
                                                                           self.list_pixels_triggered])


                            if sum_to_have_more_event_ligthed_HG >= int(self.entr5.get()): #test trigger pixels sum values

                                # data_electronics_HG[list(dict_pixelid_values_HG.keys())] = list(dict_pixelid_values_HG.values())
                                data_electronics_HG[self.list_pixels_triggered] = [dict_pixelid_values_HG[item] for item in
                                                                               self.list_pixels_triggered]

                                dict_data_electronics_HG[sum_to_have_more_event_ligthed_HG] = data_electronics_HG


                        elif self.box_choice.get()=="PE":

                            dict_pixelid_values_HG = {keys: ((np.max(dict_pixelid_values_HG[keys]) \
                                                              - self.pedestal_HG[keys])/self.Gain_HG[keys]) for keys in
                                                      dict_pixelid_values_HG.keys() if \
                                                      np.max(dict_pixelid_values_HG[keys])>=self.pedestal_HG[keys]}
                            # print(dict_pixelid_values_HG)

                            self.trigger_sofware_in_pixel_configuration(
                                dict_pixelid_values_HG)  # test trigger pixels configuration

                            # sum_to_have_more_event_ligthed_HG = np.sum(list(dict_pixelid_values_HG.values()))
                            sum_to_have_more_event_ligthed_HG = np.sum([dict_pixelid_values_HG[item] for item in
                                                                        self.list_pixels_triggered])

                            if sum_to_have_more_event_ligthed_HG >= int(self.entr5.get()):  # test trigger pixels sum values
                                #print("self.entr5", self.entr5.get())
                                # data_electronics_HG[list(dict_pixelid_values_HG.keys())] = list(dict_pixelid_values_HG.values())
                                data_electronics_HG[self.list_pixels_triggered] = [dict_pixelid_values_HG[item] for \
                                                                                   item in self.list_pixels_triggered]

                                dict_data_electronics_HG[sum_to_have_more_event_ligthed_HG] = data_electronics_HG

                elif line[0]=="tot":
                    event_data_tot=line[1]
                    if event_data_tot != {}:

                        list_tuples_tot = [var[0] for var in list(event_data_tot.values())]
                        dict_pixelid_values_tot = {}
                        for (x, y) in enumerate(list_tuples_tot):

                            if y[0] not in dict_pixelid_values_tot.keys():
                                dict_pixelid_values_tot[y[0]] = [y[1]]

                            else:
                                dict_pixelid_values_tot[y[0]].append(y[1])

                        # the local and global histogram will be performing here
                        for keys, data in dict_pixelid_values_tot.items():
                            self.old_dict_pixelid_values_tot_for_histo_global[keys].fill(data, keys)
                            self.old_dict_pixelid_values_tot_for_histo_local[keys].fill(data, keys)

                        # data_electronics_tot = np.array([random.randint(0, self.threshold_DAC) for r in range(144)])
                        data_electronics_tot = np.zeros(144)

                        if self.box_choice.get()=="DAC": #test if i want to display events in the DAc mode

                            dict_pixelid_values_tot = {keys: np.max(dict_pixelid_values_tot[keys]) for keys in
                                                      dict_pixelid_values_tot.keys()}
                            # print(dict_pixelid_values_tot)

                            self.trigger_sofware_in_pixel_configuration(dict_pixelid_values_tot) #test trigger pixels configuration


                            #sum_to_have_more_event_ligthed_tot = np.sum(list(dict_pixelid_values_tot.values()))
                            sum_to_have_more_event_ligthed_tot = np.sum([dict_pixelid_values_tot[item] for item in
                                                                           self.list_pixels_triggered])


                            if sum_to_have_more_event_ligthed_tot >= int(self.entr5.get()): #test trigger pixels sum values

                                # data_electronics_tot[list(dict_pixelid_values_tot.keys())] = list(dict_pixelid_values_tot.values())
                                data_electronics_tot[self.list_pixels_triggered] = [dict_pixelid_values_tot[item] for item in
                                                                               self.list_pixels_triggered]

                                dict_data_electronics_tot[sum_to_have_more_event_ligthed_tot] = data_electronics_tot


                        elif self.box_choice.get()=="PE":

                            dict_pixelid_values_tot = {keys: ((np.max(dict_pixelid_values_tot[keys]) \
                                                              - self.pedestal_tot[keys])/self.Gain_tot[keys]) for keys in
                                                      dict_pixelid_values_tot.keys() if \
                                                      np.max(dict_pixelid_values_tot[keys])>=self.pedestal_tot[keys]}
                            # print(dict_pixelid_values_tot)

                            self.trigger_sofware_in_pixel_configuration(
                                dict_pixelid_values_tot)  # test trigger pixels configuration

                            # sum_to_have_more_event_ligthed_tot = np.sum(list(dict_pixelid_values_tot.values()))
                            sum_to_have_more_event_ligthed_tot = np.sum([dict_pixelid_values_tot[item] for item in
                                                                        self.list_pixels_triggered])

                            if sum_to_have_more_event_ligthed_tot >= int(self.entr5.get()):  # test trigger pixels sum values
                                #print("self.entr5", self.entr5.get())
                                # data_electronics_tot[list(dict_pixelid_values_tot.keys())] = list(dict_pixelid_values_tot.values())
                                data_electronics_tot[self.list_pixels_triggered] = [dict_pixelid_values_tot[item] for \
                                                                                   item in self.list_pixels_triggered]

                                dict_data_electronics_tot[sum_to_have_more_event_ligthed_tot] = data_electronics_tot

            #stop_time = time.time()
            duration = time.time() - start_time
            start_time=time.time()

        #print(dict_data_electronics_LG)
        if dict_data_electronics_LG=={}:
            #self.data_electronics_LG = np.array([random.randint(0, self.threshold_DAC) for r in range(144)])
            self.data_electronics_LG = np.array([random.randint(0, 0) for r in range(144)])
            dict_pixelid_values_LG={}
        else:
            self.data_electronics_LG = dict_data_electronics_LG[np.max(list(dict_data_electronics_LG.keys()))]
            #self.data_electronics_LG = dict_data_electronics_LG[random.choice(list(dict_data_electronics_LG.keys()))]

        if dict_data_electronics_HG=={}:
            #self.data_electronics_HG = np.array([random.randint(0, self.threshold_DAC) for r in range(144)])
            self.data_electronics_HG = np.array([random.randint(0, 0) for r in range(144)])
            dict_pixelid_values_HG={}
        else:
            self.data_electronics_HG = dict_data_electronics_HG[np.max(list(dict_data_electronics_HG.keys()))]
             #self.data_electronics_HG = dict_data_electronics_HG[random.choice(list(dict_data_electronics_HG.keys()))]

        if dict_data_electronics_tot=={}:
            #self.data_electronics_tot = np.array([random.randint(0, self.threshold_DAC) for r in range(144)])
            self.data_electronics_tot = np.array([random.randint(0, 0) for r in range(144)])
            dict_pixelid_values_tot={}
        else:
            self.data_electronics_tot = dict_data_electronics_tot[np.max(list(dict_data_electronics_tot.keys()))]
             #self.data_electronics_tot = dict_data_electronics_tot[random.choice(list(dict_data_electronics_tot.keys()))]

        #print(self.old_dict_pixelid_values_HG_for_histo_local)
        #print(self.old_dict_pixelid_values_LG_for_histo_local)
        # print(self.old_dict_pixelid_values_tot_for_histo_local)
        self.list_of_pixels_on_events_LG=list(dict_pixelid_values_LG.keys())
        self.list_of_pixels_on_events_HG = list(dict_pixelid_values_HG.keys())
        self.list_of_pixels_on_events_tot = list(dict_pixelid_values_tot.keys())
        #plt.close(self.fig)
        self.plots_hex_in_canvas_pdp()
        self.fen1.update_idletasks()

        if self.flag_active_draw_button_for_histo_parent==0:

            self.b7.config(state="active")  # enable the draw histogram button
            self.flag_active_draw_button_for_histo_parent = 1 #This flag is to know if i can have data to draw it in histogramm


        if self.flag_1 == 1:
            print("cycle")
            self.flag_start = 0

            if (self.fen2 is not None) and self.fen2.winfo_exists():  # condition to test if child fen2 window is open or not
                #print(self.fen2.wm_state())   # this is to print the status of child fen 2 only if fen2 is open
                #animation.FuncAnimation(self.canvas, self.export_data_electronis_values(), interval=5000)

                #self.th2 = threading.Thread(target=self._trace_histo_pixel_draw_and_plot()).start() #this is to start at same time two functions
                #self.th1 = threading.Thread(target=self.fen1.after(5000, self.start_it())).start()  #this is to start at same time two functions

                #mp2 = multiprocessing.Process(target=self._trace_histo_pixel_draw_and_plot(),args=(...)).start()  #this is to start at same time two functions
                #mp1 = multiprocessing.Process(target=self.fen1.after(5000, self.start_it()),args=(...)).start()   #this is to start at same time two functions

                self.th2 = threading.Thread(target=self._trace_histo_pixel_draw_and_plot()).start()  # this is to start at same time two functions

            #else :
            self.fen1.after(5000, self.start_it)

class get_data_from_usb2can_ixxat():

    #def __init__(self,power_supply):
    def __init__(self):

        #self.power_supply=power_supply

        self.CRED = '\033[91m'
        self.CGREEN  = '\33[32m'
        self.CVIOLET = '\33[35m'
        self.CEND = '\033[0m'
        self.flag_connect_usb2can=0
        self.flag_HV_ON = 0
        self.time_out=1  #In seconds
        self.critical_temperature=43
        self.critical_HV = 80

        '''
        self.dict_arbitrationId_contains_modules_and_pixelsId = {
            0x602: [[2], [98, 99, 112, 113, 87, 88, 100, 101, 76, 89, 90, 102]],
            0x603: [[7], [124, 125, 135, 136, 114, 115, 126, 127, 103, 116, 117, 128]],
            0x604: [[8], [137, 138, 142, 143, 131, 132, 139, 140, 123, 133, 134, 141]],
            0x605: [[9], [118, 119, 129, 130, 108, 109, 120, 121, 97, 110, 111, 122]],
            0x606: [[3], [39, 50, 49, 61, 51, 63, 62, 73, 75, 74, 86, 85]],
            0x607: [[10], [60, 71, 70, 82, 72, 84, 83, 94, 96, 95, 107, 106]],
            0x608: [[11], [12, 23, 22, 34, 24, 36, 35, 46, 48, 47, 59, 58]],
            0x609: [[12], [1, 6, 5, 13, 7, 15, 14, 25, 27, 26, 38, 37]],
            0x60A: [[1], [78, 66, 54, 42, 77, 65, 53, 41, 64, 52, 40, 28]],
            0x60B: [[4], [30, 18, 10, 4, 29, 17, 9, 3, 16, 8, 2, 0]],
            0x60C: [[5], [57, 45, 33, 21, 56, 44, 32, 20, 43, 31, 19, 11]],
            0x60D: [[6], [105, 93, 81, 69, 104, 92, 80, 68, 91, 79, 67, 55]]}
        '''

        self.dict_arbitrationId_contains_modules_and_pixelsId = {
            0x602: [[2], [0, 1, 2, 3, 6, 7, 4, 5, 10, 11, 8, 9]],
            0x603: [[7], [12, 13, 14, 15, 18, 19, 16, 17, 22, 23, 20, 21]],
            0x604: [[8], [24, 25, 26, 27, 30, 31, 28, 29, 34, 35, 32, 33]],
            0x605: [[9], [36, 37, 38, 39, 42, 43, 40, 41, 46, 47, 44, 45]],
            0x606: [[3], [48, 49, 50, 51, 54, 55, 52, 53, 58, 59, 56, 57]],
            0x607: [[10], [60, 61, 62, 63, 66, 67, 64, 65, 70, 71, 68, 69]],
            0x608: [[11], [72, 73, 74, 75, 78, 79, 76, 77, 82, 83, 80, 81]],
            0x609: [[12], [84, 85, 86, 87, 90, 91, 88, 89, 94, 95, 92, 93]],
            0x60A: [[1], [96, 97, 98, 99, 102, 103, 100, 101, 106, 107, 104, 105]],
            0x60B: [[4], [108, 109, 110, 111, 114, 115, 112, 113, 118, 119, 116, 117]],
            0x60C: [[5], [120, 121, 122, 123, 126, 127, 124, 125, 130, 131, 128, 129]],
            0x60D: [[6], [132, 133, 134, 135, 138, 139, 136, 137, 142, 143, 140, 141]]}



    def connect_interface_usb2can_Ixxat(self):
        if self.flag_connect_usb2can==0:
            self.flag_connect_usb2can += 1
            self.bus = can.interface.Bus(bustype='ixxat', channel=0, bitrate=181000)
            print(self.CGREEN + "Usb2can Ixxat has been connected with success" + self.CEND)
            self.jump_to_application_usb2can()
        else:
            print(self.CGREEN + "Usb2can Ixxat already connected" + self.CEND)
        self.empty_the_fifo()

    def shutdown_interface_usb2can_Ixxat(self):

        if self.flag_HV_ON==1:
            self.set_HV_OFF_PDP()
        else:
            print(self.CVIOLET + "The HV of the PDP has never been ON"+ self.CEND)

        if self.flag_connect_usb2can == 1:
            self.flag_connect_usb2can = 0
            self.bus.shutdown()
            print(self.CVIOLET + '\33[35m' + "Usb2can Ixxat has been shutdown properly" + self.CEND)
        else:
            print(self.CVIOLET + '\33[35m' + "Usb2can Ixxat is already deconnected" + self.CEND)

        self.empty_the_fifo()

    def empty_the_fifo(self):

        try:
            self.rx=str(self.bus.recv(self.time_out))
            while self.rx!="None":
                self.rx = str(self.bus.recv(self.time_out))
        except:
            pass
        print(self.CVIOLET + "The fifo is empty" + self.CEND)
        print(self.rx)

    def jump_to_application_usb2can(self):
        for can_node in self.dict_arbitrationId_contains_modules_and_pixelsId.keys():
            msg=can.Message(arbitration_id=can_node,data=[0x1F,0x05],extended_id=False)
            self.bus.send(msg)
            time.sleep(0.5)
            self.rx=str(self.bus.recv(self.time_out))
            if self.rx=="None":
                print(self.CGREEN+ "Jump to application in module %s"%self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][0][0] + self.CEND)
            else:
                print(self.rx)
                print(self.CRED+ "Jump to application failed in module %s"%self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][0][0] + self.CEND)
                #raise IOError ("Jump to application failed")
        self.empty_the_fifo()

    def set_HV_ON_PDP(self):

        self.flag_HV_ON += 1

        for can_node in self.dict_arbitrationId_contains_modules_and_pixelsId.keys():
            msg = can.Message(arbitration_id=can_node, data=[0x07, 0x8F, 0xFF], extended_id=False)
            self.bus.send(msg)
            time.sleep(0.5)
        self.empty_the_fifo()
        print(self.CGREEN + "The HV of the PDP is ON" + self.CEND)

    def set_HV_OFF_PDP(self):

        self.flag_HV_ON = 0
        for can_node in self.dict_arbitrationId_contains_modules_and_pixelsId.keys():
            msg = can.Message(arbitration_id=can_node, data=[0x07, 0x80, 0x00], extended_id=False)
            self.bus.send(msg)
            time.sleep(0.5)
        self.empty_the_fifo()
        print(self.CVIOLET + "The HV of the PDP is going OFF properly"+ self.CEND)

    def get_HV_PDP(self):

        self.data_HV = [0] * 144
        for can_node in self.dict_arbitrationId_contains_modules_and_pixelsId.keys():
            msg = can.Message(arbitration_id=can_node, data=[0x01, 0x04], extended_id=False)
            self.bus.send(msg)
            for patch in range(4):
                self.rx = str(self.bus.recv(self.time_out)).split()
                dlc = int(self.rx[6])
                if dlc!=1:
                    print(self.rx)
                flag_patch = int(self.rx[7])
                HV_0 = (int(self.rx[8] + self.rx[9], 16)* 1.67375e-3)
                HV_1 = (int(self.rx[10] + self.rx[11], 16)* 1.67375e-3)
                HV_2 = (int(self.rx[12] + self.rx[13], 16) * 1.67375e-3)
                if flag_patch == 1:
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][0]] = HV_0
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][1]] = HV_1
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][2]] = HV_2
                if flag_patch == 21:
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][3]] = HV_0
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][4]] = HV_1
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][5]] = HV_2
                if flag_patch == 41:
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][6]] = HV_0
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][7]] = HV_1
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][8]] = HV_2
                if flag_patch == 61:
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][9]] = HV_0
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][10]] = HV_1
                    self.data_HV[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][11]] = HV_2

        test_HV_critical_or_negative_values = [temp for temp in self.data_HV if temp>=self.critical_HV or temp < 0]
        if test_HV_critical_or_negative_values == []:
            print(self.data_HV)
            print(self.CVIOLET + "Get HV's PDP properly" + self.CEND)
            print("THe maximum HV in PDP is %s" % np.max(self.data_HV))
        else:
            self.shutdown_interface_usb2can_Ixxat()
            print(test_HV_critical_or_negative_values)
            print(self.data_HV)
            nbre = 0
            while nbre <= 8:
                print(self.CRED + "HV has reached critical value or is negative" + self.CEND)
                nbre += 1
            #raise IOError("HV has reached critical value or is negative")



        self.empty_the_fifo()

    def get_temperature_PDP(self):

        self.data_temperature = [0] * 144
        for can_node in self.dict_arbitrationId_contains_modules_and_pixelsId.keys():
            msg = can.Message(arbitration_id=can_node, data=[0x01, 0x00], extended_id=False)
            self.bus.send(msg)
            #time.sleep(1)
            for patch in range(4):
                self.rx = self.bus.recv(self.time_out)
                self.rx=str(self.rx).split()
                dlc = int(self.rx[6])
                if dlc!=7:
                    print(self.rx)
                    print(self.usb2can.flag_connect_usb2can , self.usb2can.flag_HV_ON)
                    # power_supply.Communicate('INST OUT1\n')
                    # power_supply.Communicate('OUTP OFF\n')
                    # power_supply.Communicate('INST OUT2\n')
                    # power_supply.Communicate('OUTP OFF\n')
                    # power_supply.Communicate('INST OUT3\n')
                    # power_supply.Communicate('OUTP OFF\n')
                    # power_supply.Communicate('INST OUT1\n')
                    # power_supply.Communicate('OUTP ON\n')
                    # power_supply.Communicate('INST OUT2\n')
                    # power_supply.Communicate('OUTP ON\n')
                    # power_supply.Communicate('INST OUT3\n')
                    # power_supply.Communicate('OUTP ON\n')
                    time.sleep(1)
                    self.flag_connect_usb2can = 0
                    self.flag_HV_ON = 0
                    self.connect_interface_usb2can_Ixxat()
                    time.sleep(1)
                    self.set_HV_ON_PDP()
                    time.sleep(1)
                    self.get_temperature_PDP()

                flag_patch = int(self.rx[7])
                temperature_0 = (int(self.rx[8] + self.rx[9], 16) - 272.93) / 5.97403
                temperature_1 = (int(self.rx[10] + self.rx[11], 16) - 272.93) / 5.97403
                temperature_2 = (int(self.rx[12] + self.rx[13], 16) - 272.93) / 5.97403
                if flag_patch==1:
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][0]] = temperature_0
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][1]] = temperature_1
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][2]] = temperature_2
                if flag_patch==21:
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][3]] = temperature_0
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][4]] = temperature_1
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][5]] = temperature_2
                if flag_patch==41:
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][6]] = temperature_0
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][7]] = temperature_1
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][8]] = temperature_2
                if flag_patch==61:
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][9]] = temperature_0
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][10]] = temperature_1
                    self.data_temperature[
                        self.dict_arbitrationId_contains_modules_and_pixelsId[can_node][1][11]] = temperature_2

        test_temprature_critical_or_negative_values=[temp for temp in self.data_temperature if temp>=self.critical_temperature or temp<0]
        if test_temprature_critical_or_negative_values==[]:
            print(self.CVIOLET+ "We Get temperature's PDP properly" +self.CEND)
            print(self.CVIOLET+"THe maximum temperature in PDP is %s" %np.max(self.data_temperature) +self.CEND)
            #print(self.flag_connect_usb2can)
        else:
            self.shutdown_interface_usb2can_Ixxat()
            print(test_temprature_critical_or_negative_values)
            print(self.data_temperature)
            nbre=0
            while nbre<=8:
                print(self.CRED+ "Temperature has reached critical value or is negative. \n Please switch off the power supply of the slow control" + self.CEND)
                nbre+=1
            #raise IOError ("Temperature has reached critical value or is negative")

            #'''
            # power_supply.Communicate('INST OUT1\n')
            # power_supply.Communicate('OUTP OFF\n')
            # power_supply.Communicate('INST OUT2\n')
            # power_supply.Communicate('OUTP OFF\n')
            # power_supply.Communicate('INST OUT3\n')
            # power_supply.Communicate('OUTP OFF\n')

            time.sleep(1200)

            # power_supply.Communicate('INST OUT1\n')
            # power_supply.Communicate('OUTP ON\n')
            # power_supply.Communicate('INST OUT2\n')
            # power_supply.Communicate('OUTP ON\n')
            # power_supply.Communicate('INST OUT3\n')
            # power_supply.Communicate('OUTP ON\n')
            self.flag_connect_usb2can = 0
            self.flag_HV_ON = 0
            time.sleep(1)
            self.connect_interface_usb2can_Ixxat()
            time.sleep(1)
            self.set_HV_ON_PDP()
            time.sleep(1)
            self.get_temperature_PDP()
            #'''


        self.empty_the_fifo()


class Communication_with_babymind_via_socket_server(object):
    def __init__(self):
        self.connect_socket_server_on_or_off = 0 #initrialise flag to specify that i am not cobnnected to the scocket server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ("129.194.53.160", 11000)
        print(sys.stderr, ('connecting to %s port %s' % self.server_address))

    def Connect(self):
        if self.connect_socket_server_on_or_off==0:
            self.sock.connect(self.server_address)
            self.connect_socket_server_on_or_off+=1

    def Communicate(self, string):
        print(string)
        #print(('%s\r,"utf-8"')%string)
        # socket.send(bytes('BoardLib.OpenConfigFile("C:/BabyMindFrontEnd-v1.0.1.614/config/HexSiPM_07_02_2018.xml")\r', "utf-8"))
        self.sock.send(bytes(string,"utf-8"))  # Send command
        time.sleep(0.5)  # wait for one second
        self.message_receive_from_babymind=self.sock.recv(1024).decode()
        print(self.message_receive_from_babymind)  # Wait for reply

    def deconnect(self):
        if self.connect_socket_server_on_or_off == 1:
            self.connect_socket_server_on_or_off = 0
            self.sock.close()
            print("Socket server has been closed")
        else:
            print("Socket server is already deconnected")



class Communication_with_power_supply(object):
    def __init__(self):
        self.dev = usb.core.find(idVendor=0x403, idProduct=0xED72)
        self.dev.set_configuration()
        self.cfg = self.dev.get_active_configuration()
        self.intf = self.cfg[(0, 0)]

        self.ep = usb.util.find_descriptor(
            self.intf,
            # match the first OUT endpoint
            custom_match= \
                lambda e: \
                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                    usb.util.ENDPOINT_OUT)
        assert self.ep is not None


    def Communicate(self, string):

        '''
        :param string:
            -'Opall 0\n' # set all the output Off. Can also use 1 for on

        :return:
        '''
        print(string)
        self.ep.write(bytes(string, "utf-8"))  # Send command
        time.sleep(0.5)  # wait for one second

class Application:#Frame):
    '''Fenêtre principale de l'application'''
    # def __init__(self,fen1,comm,usb2can,power_supply):
    def __init__(self, fen1, comm, usb2can):
        #Frame.__init__(self)
        #self.master.title("Events on the mini camera""Events on the mini camera")
        #self.pack()
        self.fen1=fen1
        self.fen1.wm_title("Events on the mini camera")

        self.flag_start = 0

        self.comm=comm

        self.usb2can=usb2can

        # self.power_supply=power_supply

        self.txt1 = Label(self.fen1, text='Threshold\nDAC :')
        self.txt1.grid(row=2, column=1, sticky='NSEW')

        self.var_threshold_DAC = StringVar(self.fen1)
        self.var_threshold_DAC.set("540")
        self.entr1 = Spinbox(self.fen1, from_=0, to=1023, textvariable=self.var_threshold_DAC)
        self.entr1.grid(row=2, column=2)
        #self.threshold_DAC = int(self.entr1.get())

        self.txt16 = Label(self.fen1, text='Threshold\nHG :')
        self.txt16.grid(row=1, column=1, sticky='NSEW')
        self.var_threshold_HG = StringVar(self.fen1)
        self.var_threshold_HG.set("781")
        self.entr14 = Spinbox(self.fen1, from_=0, to=4095, textvariable=self.var_threshold_HG)
        self.entr14.grid(row=1, column=2)
        self.threshold_HG = int(self.entr14.get())

        self.txt17 = Label(self.fen1, text='Threshold\nLG :')
        self.txt17.grid(row=1, column=3, sticky='NSEW')
        self.var_threshold_LG = StringVar(self.fen1)
        self.var_threshold_LG.set("131")
        self.entr15 = Spinbox(self.fen1, from_=0, to=4095, textvariable=self.var_threshold_LG)
        self.entr15.grid(row=1, column=4)
        self.threshold_LG = int(self.entr15.get())

        """
        if self.flag_start==0:
            self.data_electronics_LG=np.array([random.randint(120, 120+self.threshold_DAC) for r in range(144)])
            self.data_electronics_HG = np.array([random.randint(930, 930+self.threshold_DAC) for r in range(144)])
            self.list_of_pixels_on_events_LG=[None]
            self.list_of_pixels_on_events_HG=[None]
        """


        # this is to plot the initial PDP with random vaues between 0 and threshold
        self.init_PDP = Canon(self.fen1, self.flag_start, self.comm, self.usb2can, self.entr1, self.var_threshold_DAC,
                              self.entr14, self.var_threshold_HG, self.entr15, self.var_threshold_LG)



class Hist1D_global(object):

    def __init__(self, nbins, xlow, xhigh, key=None):

        self.nbins = nbins
        self.xlow = xlow
        self.xhigh = xhigh
        if key:
            self.hist_global, self.edges_global, self.bins_global = {}, {}, {}
            self.hist_global[key], self.edges_global[key] = np.histogram([], bins=self.nbins,
                                                                         range=(self.xlow, self.xhigh))
            self.bins_global[key] = (self.edges_global[key][:-1] + self.edges_global[key][1:]) / 2.
        else:
            self.hist_global, self.edges_global = np.histogram([], bins=self.nbins, range=(self.xlow, self.xhigh))
            self.bins_global = (self.edges_global[:-1] + self.edges_global[1:]) / 2.

    def fill(self, arr, key=None):
        hist, edges = np.histogram(arr, bins=self.nbins, range=(self.xlow, self.xhigh))
        if key:
            self.hist_global[key] += hist
        else:
            self.hist_global += hist

    @property
    def data(self):
        return self.bins_global, self.hist_global

    '''
    if __name__ == "__main__":
        h = Hist1D(100, 0, 1)
        for _ in range(1000):
            a = np.random.random((3,))
            h.fill(a)
            plt.step(*h.data)
            plt.show()

        h = Hist1D(19, -3, 12)
        rng = np.random.RandomState(10)  # deterministic random data
        data = np.hstack((rng.normal(size=1000),rng.normal(loc=5, scale=2, size=1000)))
        h.fill(data)
        plt.step(*h.data)
        plt.show()

        a = np.array([22,87,5,43,56,73,55,54,11,20,51,5,79,31,27])
        hist,bins = np.histogram(a,bins = [0,20,40,60,80,100])
        bins_c=(bins[:-1] + bins[1:]) / 2.
        plt.bar(bins_c,hist,bins_c[1]-bins_c[0],align='center',edgecolor='black')



    '''


class Hist1D_local(object):

    def __init__(self, nbins, xlow, xhigh, key=None):

        self.nbins = nbins
        self.xlow = xlow
        self.xhigh = xhigh
        if key:
            self.hist_local, self.edges_local, self.bins_local = {}, {}, {}
            self.hist_local[key], self.edges_local[key] = np.histogram([], bins=self.nbins,
                                                                       range=(self.xlow, self.xhigh))
            self.bins_local[key] = (self.edges_local[key][:-1] + self.edges_local[key][1:]) / 2.
        else:
            self.hist_local, self.edges_local = np.histogram([], bins=self.nbins, range=(self.xlow, self.xhigh))
            self.bins_local = (self.edges_local[:-1] + self.edges_local[1:]) / 2.

    def fill(self, arr, key=None):
        hist, edges = np.histogram(arr, bins=self.nbins, range=(self.xlow, self.xhigh))
        if key:
            self.hist_local[key] += hist
        else:
            self.hist_local += hist

    @property
    def data(self):
        return self.bins_local, self.hist_local

    '''
    if __name__ == "__main__":
        h = Hist1D(100, 0, 1)
        for _ in range(1000):
            a = np.random.random((3,))
            h.fill(a)
            plt.step(*h.data)
            plt.show()

        h = Hist1D(19, -3, 12)
        rng = np.random.RandomState(10)  # deterministic random data
        data = np.hstack((rng.normal(size=1000),rng.normal(loc=5, scale=2, size=1000)))
        h.fill(data)
        plt.step(*h.data)
        plt.show()

        a = np.array([22,87,5,43,56,73,55,54,11,20,51,5,79,31,27])
        hist,bins = np.histogram(a,bins = [0,20,40,60,80,100])
        bins_c=(bins[:-1] + bins[1:]) / 2.
        plt.bar(bins_c,hist,bins_c[1]-bins_c[0],align='center',edgecolor='black')



    '''


class Hist2D(object):

    def __init__(self, nxbins, xlow, xhigh, nybins, ylow, yhigh):
        self.nxbins = nxbins
        self.xhigh = xhigh
        self.xlow = xlow

        self.nybins = nybins
        self.yhigh = yhigh
        self.ylow = ylow

        self.nbins = (nxbins, nybins)
        self.ranges = ((xlow, xhigh), (ylow, yhigh))

        self.hist, xedges, yedges = np.histogram2d([], [], bins=self.nbins, range=self.ranges)
        self.xbins = (xedges[:-1] + xedges[1:]) / 2.
        self.ybins = (yedges[:-1] + yedges[1:]) / 2.

    def fill(self, xarr, yarr):
        hist, _, _ = np.histogram2d(xarr, yarr, bins=self.nbins, range=self.ranges)
        self.hist += hist

    @property
    def data(self):
        return self.xbins, self.ybins, self.hist

    '''
        if __name__ == "__main__":
            h = Hist2D(100, 0, 1, 100, 0, 1)
            for _ in range(1000):
                x, y = np.random.random((3,)), np.random.random((3,))
                h.fill(x, y)
                plt.pcolor(*h.data)
                plt.show()
        '''


if __name__ =='__main__':


    def kill():
        '''Close event display and stop program when i click on close of the tkinter window'''
        if messagebox.askokcancel("Quit", "Do you really wish to quit?"):

            child_pid = os.getpid() # get children pid of parent pid pycharm
            if type(child_pid) is list:
                for child in child_pid:
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(child)])
            else:
                #os.system('kill -TERM -P {pid}'.format(pid=parent_pid))
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(child_pid)])
            sys.exit(1)

    fen1 = Tk()

    # power_supply = Communication_with_power_supply()
    # power_supply.Communicate('INST OUT1\n')
    # power_supply.Communicate('VOLT 24\n')
    # power_supply.Communicate('CURR 4\n')
    # power_supply.Communicate('INST OUT2\n')
    # power_supply.Communicate('VOLT 24\n')
    # power_supply.Communicate('CURR 2.6\n')
    # power_supply.Communicate('INST OUT3\n')
    # power_supply.Communicate('VOLT 24\n')
    # power_supply.Communicate('CURR 1.6\n')

    comm = Communication_with_babymind_via_socket_server()
    # usb2can=get_data_from_usb2can_ixxat(power_supply)
    usb2can = get_data_from_usb2can_ixxat()

    # fen1.geometry('1300x650+0+0')
    # fen1.resizable(width=False, height=False)
    fen1.protocol("WM_DELETE_WINDOW", kill) #this is reliated to the function callback

    # App=Application(fen1,comm,usb2can,power_supply)
    App = Application(fen1, comm, usb2can)
    fen1.mainloop()
    #fen1.update_idletasks()
    #fen1.update()
