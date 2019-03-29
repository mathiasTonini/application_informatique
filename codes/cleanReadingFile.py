import numpy as np
import time
def getWordId(line):
    out_hex = ['{:02X}'.format(b) for b in line]
    out_hex.reverse()
    line_out = ''.join(out_hex)
    line_out_b = bin(int(line_out, 16))[2:].zfill(32)
    Word_Id = line_out_b[0:4]
    return Word_Id

def readFile(file_to_open):

    # initialisation

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
                Word_Id = getRightLine(line)

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

                if entr5.get() == '':  # attribute value 0 to entry 5 if it is equal to 0
                    entr5.delete(0, END)
                    entr5.insert(0, "0")

                time_allowed_to_display_events = int(self.entr10.get()) * 1e-3
                start_time = time.time()
                duration = 0
                pqr = 0
                aux_dict_to_test_coincidence={}

                while line != b'':# and countss < 40000:

                    countss += 1
                    duration += time.time() - start_time
                    start_time = time.time()


                    if int(Word_Id, 2) == TDM_ID and int(line_out_b[4:6], 2) == 0:
                    # si nous somme dans au début d'un slot (0 ou 2)

                        slot = int(line_out_b[6:11], 2)
                        # on définit notre numero de slot 1 ou 2 et on lit la ligne suivante

                        line = file.read(4)
                        if line != b'':
                            Word_Id = getWordId(line)

                        # Si le slot actuel n'est pas dans la liste de slots deja traiter alors on l'ajoute,
                        # Si on l'a dejà traité alors on a nouvel évenement: liste de slots traiter à vide et on ajoute ce slot là
                        if slot not in pin_complete_slots:
                            pin_complete_slots.append(slot)
                        else:
                            pin_complete_slots = []
                            pin_complete_slots.append(slot)

                        # Tant qu'on a pas un nouveau slot
                        while int(Word_Id, 2) != TDM_ID and line != b'':


                             # test inutile mais galère de ré-indenter
                            if int(Word_Id, 2) == TDM_ID and int(line_out_b[4:6], 2) == 1:
                                break
                            else:

                                # Si l'on a special word on change nmo (a demander ce que c'est)
                                if int(Word_Id, 2) == Special_Word_id and int(line_out_b[11], 2) == 0 and int(
                                        line_out_b[12:32], 2) == 3:
                                    print("Gtrig + Spill REset for slot {}".format(slot))
                                    nmo = 1
                                else:
                                    #A ce moment, on est soit dans un évenement, soit en début d'évenement soit à la fin

                                    # Pour rappel:
                                    # un évenemtn est de la forme:
                                    #     GTRIGHeader0 -> GTRIGtrailer0
                                    #                     +
                                    #     GTRIGheader2 -> GTRIGtrailer2


                                    #Tant qu'on a pas eu au moins Gtrig header on s'en bas les couilles de ce qu'on lit
                                    if int(Word_Id, 2) == Gtrig_Header_Id:
                                        #C'est bon, on a eu notre header on rentre dans la création d'évenents

                                        #On comment par regarder le header de quel slot c'est
                                        gtrig_header[slot] = int(line_out_b[4:32], 2)

                                        # tant que nous sommes pas la fin de l' evenement ou du fichier...
                                        while int(Word_Id, 2) != Gtrig_trailer_1_Id and line != b'':

                                            # Si ça a quelque chose à voire avec  l'amplitude
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





readFile("/home/mathias/Documents/unige/UNIGE/2eme/appliInfo/donnee/acdcscan_0dacAc_400dacDC_40HG_4LG/0tdacAc_400dacDC_540thrasic_151thrfpgalg_901thrfpgahg_2sec_100hz.daq")
