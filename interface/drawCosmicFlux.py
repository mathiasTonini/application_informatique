from math import sin, cos, pi
import os
import numpy as np
from math import cos, sin, sqrt, pi
import random
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
from numpy import arange, sin, pi
from matplotlib import cm, colors
import matplotlib.animation as animation
import sys
import matplotlib.image as image
import time
import ruche
def getValues (folder):
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

    for file_to_open in os.listdir(folder):
        formatFile=folder+"/"+file_to_open
        if (os.path.isdir(formatFile)):
            break; #Saute le dossier de reception
        with open(formatFile, "r+b") as file:
            line = file.read(4)
            out_hex = ['{:02X}'.format(b) for b in line]
            out_hex.reverse()
            line_out = ''.join(out_hex)
            line_out_b = bin(int(line_out, 16))[2:].zfill(32)
            Word_Id = line_out_b[0:4]

            event_data_amplitude_LG = {}
            event_data_amplitude_HG = {}
            event_data_tot = {}

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
            start_time = time.time()
            duration = 0
            pqr = 0
            aux_dict_to_test_coincidence={}

            while line != b'':# and countss < 40000:

                duration += time.time() - start_time
                start_time = time.time()
                countss += 1


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
                                # print("Gtrig + Spill REset for slot {}".format(slot))
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

                                            if len(pin_complete_slots) == 2:  # if pin_complete_slots == [0, 2]:
                                                write_in_new_file = 1
                                                if (gtrig_header[slot] - gtrig_ampli_or_tot_old[slot]) != 0:  # to  verify
                                                    X1_trigger_rate += 1 / ((gtrig_header[slot] - gtrig_ampli_or_tot_old[slot]) * 10e-6)
                                                    X2_trigger_rate += (1 / ((gtrig_header[slot] - gtrig_ampli_or_tot_old[slot]) * 10e-6)) ** 2
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
                                                    if tot >= 0: #testé, on rentre dedans (il faut laisser les old pixels en commentaire sinon ne marche pas)
                                                        global_trigger_header_amplitude[slot].append(gtrig_header[slot])
                                                        global_trigger_header_time[slot].append(gtrig_header_used_for_rate[(slot, Channel_id, Tag_Id,Hit_Id)])

                                                        positive_tot += 1
                                                        val_LG=dict_queue_edge[(slot, Channel_id, Tag_Id,Hit_Id)][2]
                                                        val_HG= dict_queue_edge[(slot, Channel_id, Tag_Id,Hit_Id)][3]

                                                        if Channel_id not in aux_dict_to_test_coincidence.keys():
                                                            aux_dict_to_test_coincidence[Channel_id]=[val_LG]
                                                        else:
                                                            aux_dict_to_test_coincidence[Channel_id].append(val_LG)

                                                        data_LG[pqr][Channel_id]= val_LG


                                                        data_HG[pqr][Channel_id]= val_HG


                                                        data_time[pqr][Channel_id]=tot
                                                        #fill global histo
                                                        # self.old_dict_pixelid_values_LG_for_histo_global[keys].fill(val_LG, Channel_id)
                                                        # self.old_dict_pixelid_values_HG_for_histo_global[keys].fill(val_HG, Channel_id)
                                                        # self.old_dict_pixelid_values_tot_for_histo_global[keys].fill(tot, Channel_id)

                                                        #fill local histo
                                                        # self.old_dict_pixelid_values_LG_for_histo_local[keys].fill(val_LG, Channel_id)
                                                        # self.old_dict_pixelid_values_HG_for_histo_local[keys].fill(val_HG, Channel_id)
                                                        # self.old_dict_pixelid_values_tot_for_histo_local[keys].fill(tot, Channel_id)

                                                        event_data_amplitude_LG[nmo] = [(Channel_id,dict_queue_edge[(slot, Channel_id,Tag_Id,Hit_Id)][2])]
                                                        event_data_amplitude_HG[nmo] = [(Channel_id,dict_queue_edge[(slot, Channel_id,Tag_Id,Hit_Id)][3])]
                                                        event_data_tot[nmo] = (Channel_id,tot)

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

                                    if duration > time_allowed_to_display_events:
                                        #add for ruche
                                        data_LG.append([0]*144)
                                        data_HG.append([0]*144)
                                        data_time.append([0]*144)
                                        index_max_sum = [np.sum(l) for l in data_LG].index(np.max([np.sum(l) for l in data_LG]))
                                        data_electronics_LG = data_LG[index_max_sum]
                                        data_electronics_HG = data_HG[index_max_sum]
                                        data_electronics_tot = data_time[index_max_sum]

                                        pqr = 0
                                        data_LG = [[0] * 144]
                                        data_HG = [[0] * 144]
                                        data_time = [[0] * 144]

                                        duration = 0
                                        start_time = time.time()

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


    std_rate = dict((keys,np.mean(mean_rate[keys])) for keys in std_rate.keys())
    mean_rate = dict((keys,np.mean(mean_rate[keys])) for keys in mean_rate.keys())

    mean_trigger_rate=np.mean(mean_trigger_rate)
    std_trigger_rate=np.mean(std_trigger_rate)

    list_rate_components = [mean_rate, std_rate, mean_trigger_rate, std_trigger_rate]

    # print("[mean_rate ,std_rate,mean_trigger_rate,std_trigger_rate]===",[aux[74] for aux in list_rate_components[0:2]], mean_trigger_rate, std_trigger_rate)
    list_mean_cosmicray_rate_HG.append(list_rate_components[0][0])
    list_std_cosmicray_rate_HG.append(list_rate_components[1][0])
    list_mean_cosmicray_rate_LG.append(list_rate_components[0][0])
    list_std_cosmicray_rate_LG.append(list_rate_components[1][0])
    list_mean_cosmicray_rate_tot.append(list_rate_components[0][0])
    list_std_cosmicray_rate_tot.append(list_rate_components[1][0])

    list_mean_trigger_rate_ampli.append(list_rate_components[2])
    list_std_trigger_rate_ampli.append(list_rate_components[3])
    list_mean_trigger_rate_tot.append(list_rate_components[2])
    list_std_trigger_rate_tot.append(list_rate_components[3])


def draw(folder,  depuis,to, step, choice):

    pedestal_LG=[15]*144
    Gain_LG=[4.5]*144
    pedestal_HG = [144]*144
    Gain_HG = [47]*144
    pedestal_tot = [0]*144
    Gain_tot = [3]*144
    threshold_x_shape_in_trigger_plot=np.arange(depuis,to,step)
    for threshold_aux in threshold_x_shape_in_trigger_plot:
        if choice=="HG":
            var_threshold_HG= threshold_aux
            getValues(folder)
        elif choice=="LG":
            var_threshold_LG=threshold_aux
            getValues(folder)
    threshold_x_shape_in_trigger_plot_in_PE_LG=[(threshold_LG - np.mean(pedestal_LG))/np.mean(Gain_LG) for threshold_LG in threshold_x_shape_in_trigger_plot]
    threshold_x_shape_in_trigger_plot_in_PE_HG = [(threshold_HG - np.mean(pedestal_HG)) / np.mean(Gain_HG) for threshold_HG in threshold_x_shape_in_trigger_plot]
    threshold_x_shape_in_trigger_plot_in_PE_LG=['%s'%e for e in threshold_x_shape_in_trigger_plot_in_PE_LG]
    threshold_x_shape_in_trigger_plot_in_PE_HG = ['%s' % e for e in threshold_x_shape_in_trigger_plot_in_PE_HG]

    fig_trigger_0 = plt.figure()
    fig_trigger_1 = plt.figure()
    fig_trigger_2 = plt.figure()
    fig_trigger_3 = plt.figure()

    axs_trigger_0 = fig_trigger_0.add_subplot(111)
    axs_trigger_1 = fig_trigger_1.add_subplot(111)
    axs_trigger_2 = fig_trigger_2.add_subplot(111)
    axs_trigger_3 = fig_trigger_3.add_subplot(111)

    axs_trigger_0.errorbar(threshold_x_shape_in_trigger_plot,list_mean_trigger_rate_ampli,list_std_trigger_rate_ampli,fmt='-o')
    axs_trigger_1.errorbar(threshold_x_shape_in_trigger_plot, list_mean_trigger_rate_tot, list_std_trigger_rate_tot, fmt='-o')
    axs_trigger_2.errorbar(threshold_x_shape_in_trigger_plot, list_mean_cosmicray_rate_HG, list_std_cosmicray_rate_HG, fmt='-o')
    axs_trigger_3.errorbar(threshold_x_shape_in_trigger_plot, list_mean_cosmicray_rate_tot, list_std_cosmicray_rate_tot, fmt='-o')

    axs_trigger_0.set_yscale("log")
    axs_trigger_0.set_title("Trigger in amplitude")
    axs_trigger_0.grid()
    axs_trigger_0_prime=axs_trigger_0.twiny()
    axs_trigger_0_prime.set_xlim(axs_trigger_0.get_xlim())
    axs_trigger_0_prime.set_xticks(threshold_x_shape_in_trigger_plot)
    axs_trigger_0_prime.set_xticklabels(threshold_x_shape_in_trigger_plot_in_PE_HG)

    axs_trigger_1.set_yscale("log")
    axs_trigger_1.set_title("Trigger in tot")
    axs_trigger_1.grid()
    axs_trigger_1_prime = axs_trigger_1.twiny()
    axs_trigger_1_prime.set_xlim(axs_trigger_1.get_xlim())
    axs_trigger_1_prime.set_xticks(threshold_x_shape_in_trigger_plot)
    axs_trigger_1_prime.set_xticklabels(threshold_x_shape_in_trigger_plot_in_PE_HG)

    axs_trigger_2.set_yscale("log")
    axs_trigger_2.set_title("CR flux in amplitude")
    axs_trigger_2.grid()
    axs_trigger_2_prime = axs_trigger_2.twiny()
    axs_trigger_2_prime.set_xlim(axs_trigger_2.get_xlim())
    axs_trigger_2_prime.set_xticks(threshold_x_shape_in_trigger_plot)
    axs_trigger_2_prime.set_xticklabels(threshold_x_shape_in_trigger_plot_in_PE_LG)

    axs_trigger_3.set_yscale("log")
    axs_trigger_3.set_title("CR flux in tot")
    axs_trigger_3.grid()
    axs_trigger_3_prime =axs_trigger_3.twiny()
    axs_trigger_3_prime.set_xlim(axs_trigger_3.get_xlim())
    axs_trigger_3_prime.set_xticks(threshold_x_shape_in_trigger_plot)
    axs_trigger_3_prime.set_xticklabels(threshold_x_shape_in_trigger_plot_in_PE_LG)

    fig_trigger_0.savefig(folderResult+"/fig_trigger_0.svg",format='svg')
    fig_trigger_1.savefig(folderResult+"/fig_trigger_1.svg",format='svg')
    fig_trigger_2.savefig(folderResult+"/fig_trigger_2.svg",format='svg')
    fig_trigger_3.savefig(folderResult+"/fig_trigger_3.svg",format='svg')


list_mean_cosmicray_rate_HG=[]
list_std_cosmicray_rate_HG=[]
list_mean_cosmicray_rate_LG=[]
list_std_cosmicray_rate_LG=[]
list_mean_cosmicray_rate_tot=[]
list_std_cosmicray_rate_tot=[]

list_mean_trigger_rate_ampli=[]
list_std_trigger_rate_ampli=[]
list_mean_trigger_rate_tot=[]
list_std_trigger_rate_tot=[]

folder=sys.argv[1]
depuis=int(sys.argv[2])
to=int(sys.argv[3])
step=int(sys.argv[4])
choice=sys.argv[5]
time_allowed_to_display_events=int(sys.argv[6])* 1e-3

data_electronics_LG = np.array([random.randint(0, 300) for r in range(144)])
data_electronics_HG = np.array([random.randint(0, 300) for r in range(144)])
data_electronics_tot = np.array([random.randint(0, 300) for r in range(144)])

#make the folder where the figures will be stored
folderResult=folder+"/figures"
if not os.path.exists(folderResult):
    os.makedirs(folderResult)
else:
    if os.listdir(folderResult) is not []:
        for element in os.listdir(folderResult):
            os.remove(folderResult+"/"+element)

draw(folder,depuis,to,step,choice)#make plots
ruche.Makeruche(choice,data_electronics_HG,data_electronics_LG,data_electronics_tot,folderResult)
