# -*- coding:utf-8 -*-

# Morceau.py 
# extrait les données d'un morceau de musique depuis un fichier MIDI CSV et les mets dans un objet
import py_midicsv as pm
import os

class Morceau:
    def __init__(self, path):
        
        self.path = path
        self.filename = self.path.split(os.sep)[-1]

        # Header information
        self.format = None
        self.nbTracks = None
        self.division = None

        # SMPTE_offset information
        self.smpteHour = None
        self.smpteMinute = None
        self.smpteSecond = None
        self.smpteFrame = None
        self.smpteFracFrame = None

        # Time signature information
        self.tsNum = None
        self.tsDenom = None
        self.tsClick = None
        self.tsNotesQ = None

        # Key signature information
        self.ksKey = None
        self.ksMinMaj = None

        # Tempo information
        self.tempoList = []

        # Tracks information
        self.trackList = []

        # Dictionnaire temps vers note, note vers temps et liste des notes
        self.time_to_note_dict = None
        self.note_to_time_dict = None
        self.liste_notes = []

        if not ".csv" in self.filename:
            print("Erreur :  format invalide (.csv expected, .{} got)".format(self.filename.split('.')[-1]))
        else:
            self.get_info()
        

    def __str__(self):
        return "\nFILE INFO :\nfilename =\t{0}\nformat =\t{1}\nnbTracks =\t{2}\ndivision =\t{3}\n\nSMPTE INFO :\nsmpteHour =\t{4}\nsmpteMinute =\t{5}\nsmpteSecond =\t{6}\nsmpteFrame =\t{7}\nsmpteFracFrame = {8}\n\nTIME SIGNATURE INFO :\ntsNum =\t\t{9}\ntsDenom =\t{10}\ntsClick =\t{11}\ntsNotesQ =\t{12}\n\nKEY SIGNATURE INFO :\nself.ksKey =\t{13}\nself.ksMinMaj =\t{14}".format(self.path,
                        self.format,
                        self.nbTracks,
                        self.division,
                        self.smpteHour,
                        self.smpteMinute,
                        self.smpteSecond,
                        self.smpteFrame,
                        self.smpteFracFrame,
                        self.tsNum,
                        self.tsDenom,
                        self.tsClick,
                        self.tsNotesQ,
                        self.ksKey,
                        self.ksMinMaj)

    def get_info(self):
        file = open(self.path, 'r') #ouverture du fichier
        lines = file.readlines() #lecture des lignes
        file.close() #fermetures du fichier
        rest = self.get_header(lines) # on récupère toutes les lignes autres que le header
        if rest == None:
            print("Error : No Header found\n")
        else:
            self.get_tracks(rest)

    def get_header(self, lines):
        header = lines[0].upper()
        if 'HEADER' not in header:
            #Error : No Header found
            return None
        else:
            h = header.split(",") # on transforme la ligne en tableau
            self.format = int(h[3])
            self.nbTracks = int(h[4]) # on enregistre les informations du header dans l'objet
            self.division = int(h[5])
            self.trackList = [[] for k in range(self.nbTracks)] # on crée  la liste des pistes
        return lines[1:]

    def get_tracks(self, lines):
        # cette méthode a pour but de lire le reste du fichier et d'en tirer les informations néncessaires
        for line in lines:
            if "TIME_SIGNATURE" in line.upper():
                self.get_time_signature(line)
            elif "KEY_SIGNATURE" in line.upper():
                self.get_key_signature(line)
            elif "SMPTE_OFFSET" in line.upper():
                self.get_smpte_offset(line)
            elif "TEMPO" in line.upper():
                self.tempoList.append(line)
            elif "NOTE_" in line.upper() :
                h = line.split(",") # on transforme la ligne en tableau
                no_track = int(h[0]) # string vers entier
                self.trackList[no_track - 1].append(line)
                

    def get_time_signature(self, line):
        # cette méthode récupère les données relatives à la signature temporelle d'un morceau
        line = line.split(",")
        self.tsNum = int(line[3])
        self.tsDenom = int(line[4])
        self.tsClick = int(line[5])
        self.tsNotesQ = int(line[6])
        h = self.division * (4 / 2 ** self.tsDenom)  # durée de la note de référence
        # création du dictionnaire de corrélation entre la durée et le type d'une note
        self.time_to_note_dict = {
            4 * h: "b",
            2 * h: "d",
            h: "h",
            1 / 2 * h: "l",
            1 / 4 * h: "p",
            1 / 8 * h: "t",
            1 / 16 * h: "x",
            6 * h: "a",
            3 * h: "c",
            3 / 2 * h: "g",
            3 / 4 * h: "k",
            3 / 8 * h: "o",
            3 / 16 * h: "s",
            3 / 32 * h: "w",
            4 / 3 * h: "f",
            2 / 3 * h: "j",
            1 / 3 * h: "n",
            1 / 6 * h: "r",
            1 / 12 * h: "v",
            1 / 24 * h: "z",
            8 / 5 * h: "e",
            4 / 5 * h: "i",
            2 / 5 * h: "m",
            1 / 5 * h: "q",
            1 / 10 * h: "u",
            1 / 20 * h: "y",
        }
        self.note_to_time_dict = {val: ind for ind, val in self.time_to_note_dict.items()}
        self.liste_notes = [k for k in self.time_to_note_dict]

    def get_key_signature(self, line):
        # cette méthode récupère les données relatives à la key_signature d'un morceau
        line = line.split(",")
        self.ksKey = int(line[3])
        self.ksMinMaj = line[4]
            
    def get_smpte_offset(self, line):
        # cette méthode récupère les données relatives à au smpte_offset d'un morceau
        line = line.split(",")
        self.smpteHour = int(line[3])
        self.smpteMinute = int(line[4])
        self.smpteSecond = int(line[5])
        self.smpteFrame = int(line[6])
        self.smpteFracFrame = int(line[7])
            

    def get_track(self, numero):
        # renvoie la piste correspond au numéro si le numéro est valide
        if numero > 0 and numero <= self.nbTracks:
            return self.trackList[numero-1]
        else:
            #Error : Incorrect track number
            return None


    def arrondi_note(self, time): 
        # arrondit une note à la plus proche existante et renvoie la nouvelle note
        l = [abs(k-time) for k in self.liste_notes]
        note = self.liste_notes[l.index(min(l))]
        return note



    def get_notes(self, quantif=False):
        #renvoie toutes les notes présentes dans le morceau (non ordonnées)
        notesListe = []
        for piste in range(1, self.nbTracks+1):
            L = self.get_track(piste)
            while L != []:
                line1 = L[0].split(",")
                time1 = int(line1[1]) #récupération Time
                note = int(line1[4]) #récupération n° touche

                b=0
                line2 = [-1,-1,-1,-1,-1]
                while int(line2[4]) != note :
                    b += 1
                    line2 = L[b].split(",")

                time2 = int(line2[1]) # récupération deuxième temps
                duree = time2-time1
                if quantif:
                    duree = self.arrondi_note(duree)
                L = L[1:b]+L[b+1:] # on enleve les deux lignes
                notesListe.append(duree)
        return notesListe


#********************************************************************************** 

    def preparer_track_rythme_select(self, numero):
        # encode la piste numero sous le format adapté au rythme et renvoie le résultat
        L = self.get_track(numero)  # on récupère la piste
        chaine_retour = ""
        time2 = 0
        while L != []:
            line1 = L[0].split(",")  # transformation en liste
            time1 = int(line1[1])  # récupérer le Time
            note = int(line1[4])  # récupérer la Note

            if time1 != time2:  # la note ne commence pas immédiatement après la fin de la précédente
                duree = self.arrondi_note(time1 - time2)
                type_note = self.time_to_note_dict[duree].upper()  # on met en majuscule car c'est un silence
                chaine_retour += str(type_note)+" "

            line2 = L[1].split(",")
            time2 = int(line2[1])  # récupération deuxième temps
            duree = self.arrondi_note(time2-time1)

            type_note = self.time_to_note_dict[duree]

            chaine_retour += str(type_note)+" "

            L = L[2:]  # on enleve les deux premières lignes
        return chaine_retour
    

    def preparer_track_rythme(self, numero = None):
        chaine_retour = ""
        if numero == None:
            L_chaine_retour = []
            for i in range(self.nbTracks):
                chaine = self.preparer_track_rythme_select(i+1)
                L_chaine_retour.append(chaine) 
            return L_chaine_retour
        else:
            chaine_retour = self.preparer_track_rythme_select(numero)
            return chaine_retour
        
        
        
        
      
#********************************************************************************************************

    def format_to_csv_rythme(self, entree, save_name="default"): 
        # transforme une chaine encodé au format rythme et renvoie le csv associé
        output_path = self.path
        header = "0, 0, Header, {0}, {1}, {2}\n".format(self.format,self.nbTracks, self.division)
        start1 = "1, 0, Start_track\n"
        smpte = "1, 0, SMPTE_offset, {0}, {1}, {2}, {3}, {4}\n".format(self.smpteHour, self.smpteMinute, self.smpteSecond, self.smpteFrame, self.smpteFracFrame)
        time_s = "1, 0, Time_signature, {0}, {1}, {2}, {3}\n".format(self.tsNum, self.tsDenom, self.tsClick, self.tsNotesQ)
        key_s = "1, 0, Key_signature, {0},{1}".format(self.ksKey, self.ksMinMaj)
        tempo1 = "1, 0, Tempo, {0}\n".format(857142)
        origine = '1, 0, Text_t, "Song generated by MusicBox (https://github.com/Karatsuban/MusicBox)"'

        csv_notes_list = [header, start1, origine]
        if not "None" in smpte:
            csv_notes_list += [smpte]
        
        csv_notes_list += [time_s, key_s, tempo1]

        temps = 0
        liste_note = []
        is_silence = False
        for note in entree.split():
            if note.upper() == note:  # c'est un silence
                note = note.lower()
                is_silence = True
            else:
                is_silence = False

            duree_n = int(self.note_to_time_dict[note])

            if not is_silence:
                liste_note.append([temps, "2, {0}, Note_on_c, 0, 69, 80\n".format(temps)]) # la velocité est mise à 80 par défaut (choix sans raison)
                liste_note.append([temps+duree_n,"2, {0}, Note_on_c, 0, 69, 0\n".format(temps+duree_n)]) # la vélocité est mise à 0 (équivalent de Note_off_c)
            temps += duree_n
        liste_note.sort() #on trie les notes dans l'ordre croissant


        tempo2 = "1, {0}, Tempo, {1}\n".format(temps, 857142)
        end1 = "1, {0}, End_track\n".format(temps) # fin du track au temps du dernier tempo
        start2 = "2, 0, Start_track\n"

        csv_notes_list += [tempo2, end1, start2]

        for note in liste_note:
            csv_notes_list.append(note[1])

        end2 = "2, {0}, End_track\n".format(temps) # temps de la dernière note
        end_of_file = "0, 0, End_of_file"

        csv_notes_list += [end2, end_of_file]

        midi_object = pm.csv_to_midi(csv_notes_list)
        
        if(save_name !="default"):
            name_out = output_path.replace("CSV"+os.sep+self.filename, "Resultat"+os.sep+save_name+".mid")
        else:
            name_out = output_path.replace("CSV"+os.sep+self.filename, "Resultat"+os.sep+self.filename+".mid")


        # Save the parsed MIDI file to disk
        with open(name_out, "wb") as output_file:
            midi_writer = pm.FileWriter(output_file)
            midi_writer.write(midi_object)

#*********************************************************************************************

    def preparer_track_melodie_select(self, L):
         chaine_retour = ""  # chaine de retour
         save = None
         while L != []:
             line1 = L[0].split(",")  # transformation en liste
             time1 = int(line1[1])  # récupérer le Time
             note = int(line1[4])  # récupérer la Note
             
             b = 0
             line2 = [-1, -1, -1, -1, -1]
             while int(line2[4]) != note:  # on cherche la note qui termine
                 b += 1
                 line2 = L[b].split(",")
 
             time2 = int(line2[1])  # récupération deuxième temps
             duree = self.arrondi_note(time2-time1)
             type_note = self.time_to_note_dict[duree]
 
             if save == None:
                 chaine_retour = str(time1)+":"+str(type_note)+":"+str(note)+" "
             else:
                 chaine_retour += str(time1-save)+":"+str(type_note)+":"+str(note)+" "
 
             save = time1
             
             L = L[1:b]+L[b+1:]  # on enleve les deux lignes
         return chaine_retour
     

    def preparer_track_melodie(self, numero = None):
        if(numero == None): #on récupère toutes les pistes
            L = []
            for a in range(self.nbTracks):
                for note in self.trackList[a]:
                    time = int(note.split(",")[1])  # on récupère le temps pour le triage
                    L.append([time,note])  # on ajoute toutes les notes dans la même liste
            L.sort()  # triage de la liste des notes
            L = [k[1] for k in L]
        else:
            L = self.get_track(numero)  # on récupère la seule piste demandée
        return self.preparer_track_melodie_select(L)
    
    
    
#*********************************************************************************************

    def format_to_csv(self, entree, save_name="default"): # transforme une chaine sous le format et renvoie le csv associé
        output_path= self.path
        header = "0, 0, Header, {0}, {1}, {2}\n".format(self.format,self.nbTracks, self.division)
        start1 = "1, 0, Start_track\n"
        smpte = "1, 0, SMPTE_offset, {0}, {1}, {2}, {3}, {4}\n".format(self.smpteHour, self.smpteMinute, self.smpteSecond, self.smpteFrame, self.smpteFracFrame)
        time_s = "1, 0, Time_signature, {0}, {1}, {2}, {3}\n".format(self.tsNum, self.tsDenom, self.tsClick, self.tsNotesQ)
        key_s = "1, 0, Key_signature, {0},{1}".format(self.ksKey, self.ksMinMaj)
        tempo1 = "1, 0, Tempo, {0}\n".format(857142)
        origine = '1, 0, Text_t, "Song generated by MusicBox (https://github.com/Karatsuban/MusicBox)"'

        csv_notes_list = [header, start1, origine]
        if not "None" in smpte:
            csv_notes_list += [smpte]
        
        csv_notes_list += [time_s]

        if not "None" in key_s:
            csv_notes_list += [key_s]

        csv_notes_list += [tempo1]

        all_notes = entree.replace("\n", "").split(" ")  # on découpe l'entrée note par note
        temps = 0
        duree_n = 0
        liste_note = []

        for note in all_notes:
            triplet = note.split(":")
            if(len(triplet) == 3):
                tps, duree_n, note_nb = triplet
                tps = int(tps)
                duree_n = int(list(self.time_to_note_dict.keys())[list(self.time_to_note_dict.values()).index(duree_n)])
                note_nb = int(note_nb)
                temps += tps #on incrémente le temps global
                liste_note.append([temps, "2, {0}, Note_on_c, 0, {1}, {2}\n".format(temps,note_nb,80)]) # la velocité est mise à 80 par défaut (choix sans raison)
                liste_note.append([temps+duree_n,"2, {0}, Note_on_c, 0, {1}, {2}\n".format(temps+duree_n,note_nb,0)]) # la vélocité est mise à 0 (équivalent de Note_off_c)
        temps += duree_n
        liste_note.sort() #on trie les notes dans l'ordre croissant


        tempo2 = "1, {0}, Tempo, {1}\n".format(temps, 857142)
        end1 = "1, {0}, End_track\n".format(temps) # fin du track au temps du dernier tempo
        start2 = "2, 0, Start_track\n"

        csv_notes_list += [tempo2, end1, start2]

        for note in liste_note:
            csv_notes_list.append(note[1])

        end2 = "2, {0}, End_track\n".format(temps) # temps de la dernière note
        end_of_file = "0, 0, End_of_file"

        csv_notes_list += [end2, end_of_file]

        midi_object = pm.csv_to_midi(csv_notes_list)

        if(save_name !="default"):
            name_out = output_path.replace("CSV"+os.sep+self.filename, "Resultat"+os.sep+save_name+".mid")
        else:
            name_out = output_path.replace("CSV"+os.sep+self.filename, "Resultat"+os.sep+self.filename+".mid")

           
        # Save the parsed MIDI file to disk
        with open(name_out, "wb") as output_file:
            midi_writer = pm.FileWriter(output_file)
            midi_writer.write(midi_object)
