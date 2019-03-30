import event #file with the definition of event
#event is an object wich contains 3 methods:
 # -modPixels(idPixel,value) pixel n° idPixel take the value of value
 # -getPixels() return the list of getPixels
 # -getID() return the id of the event
def getRightLine(line):
    out_hex = ['{:02X}'.format(b) for b in line]
    out_hex.reverse()
    line_out = ''.join(out_hex)
    line_out_b = bin(int(line_out, 16))[2:].zfill(32)
    return line_out_b

def makeEventListFromFile(file):
    #initalisation des constantes

    TDM_ID = 0b1110
    Hit_Amplitude_Id = 0b0011
    Hit_Time_Id = 0b0010
    Gtrig_Header_Id = 0b0001
    Gtrig_trailer_1_Id = 0b0100
    Gtrig_trailer_2_Id = 0b0101
    Special_Word_id = 0b1111
    #variable
    pin_complete_slots = []
    #retour
    nbLigne=0
    listEvent=[]
    #lecture
    with open(file, "r+b") as file:
        line = file.read(4)
        nbLigne=nbLigne+1
        rightLine = getRightLine(line)
        Word_Id = rightLine[0:4]
        while line != b'':
            if int(Word_Id, 2) == TDM_ID and int(rightLine[4:6], 2) == 0:
            # si nous somme dans au début d'un slot (0 ou 2)
                slot = int(rightLine[6:11], 2)
                # on définit notre numero de slot 1 ou 2 et on lit la ligne suivante

                line = file.read(4)
                nbLigne=nbLigne+1
                if line != b'':
                    Word_Id = getRightLine(line)[0:4]

                # Si le slot actuel n'est pas dans la liste de slots deja traiter alors on l'ajoute,
                # Si on l'a dejà traité alors on a nouvel évenement: liste de slots traiter à vide et on ajoute ce slot là
                if slot not in pin_complete_slots:
                    pin_complete_slots.append(slot)
                else:
                    pin_complete_slots = []
                    pin_complete_slots.append(slot)
                while int(Word_Id, 2) != TDM_ID and line != b'':
                    if int(Word_Id, 2) == Special_Word_id and int(rightLine[11], 2) == 0 and int(rightLine[12:32], 2) == 3:
                        print("Gtrig + Spill Reset for slot {}".format(slot))
                        nmo = 1
                    else:
                        #A ce moment, on est soit dans un évenement, soit en début d'évenement soit à la fin

                        # Pour rappel:
                        # un évenemtn est de la forme:
                        #     GTRIGHeader0 -> GTRIGtrailer0
                        #                     +
                        #     GTRIGheader2 -> GTRIGtrailer2
                        line = file.read(4)
                        nbLigne=nbLigne+1
                        print(nbLigne)
makeEventListFromFile("/home/mathias/Documents/unige/UNIGE/2eme/appliInfo/donnee/acdcscan_0dacAc_400dacDC_40HG_4LG/0tdacAc_400dacDC_540thrasic_151thrfpgalg_901thrfpgahg_2sec_100hz.daq")
