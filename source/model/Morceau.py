# -*- coding:utf-8 -*-
import os
import copy


class Morceau:
    def __init__(self, path):

        self.path = path  # chemin complet du fichier
        self.filename = self.path.split(os.sep)[-1]  # nom du fichier

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

        # Temps note référence
        self.tempsNoteRef = None

        # Dictionnaire temps vers note, note vers temps et liste des notes
        self.time_to_note_dict = None
        self.note_to_time_dict = None
        self.liste_notes = []

        self.elt_sep = None  # séparateur d'éléments dans une note
        self.format_infos = None  # contiendra un dictionnaire avec toutes les informations sur un format
        self.all_types = {"IIN": "TEMPS", "TNB": "TOUCHE", "TD": "TOUCHE", "V": "VELOCITE", "TN": "TYPE", "PM": "POSITION"}  # liste des types possible pour un élément de note
        self.types_presents = None

        if ".csv" not in self.filename:  # si le fichier n'est pas un csv
            print("Erreur :  format invalide (.csv expected, .{} got)".format(self.filename.split('.')[-1]))  # erreur
        else:
            self.get_info()  # lancement du parsing

    def get_info(self):
        # fonction s'occupant de récupérer les informations dans le fichier .csv
        file = open(self.path, 'r')  # ouverture du fichier
        lines = file.readlines()  # lecture des lignes
        file.close()  # fermeture du fichier
        rest = self.get_header(lines)  # on récupère toutes les lignes autres que le header
        if rest is None:
            print("Error : No Header found\n")
        else:
            self.get_tracks(rest)
        return

    def get_header(self, lines):
        # récupère le header du fichier .csv
        header = lines[0].upper()
        if 'HEADER' not in header:
            return None  # erreur : No Header found
        else:
            h = header.split(",")  # on transforme la ligne en tableau
            self.format = int(h[3])
            self.nbTracks = int(h[4])  # on enregistre les informations du header dans l'objet
            self.division = int(h[5])
            self.trackList = [[] for _ in range(self.nbTracks)]  # on crée  la liste des pistes
        return lines[1:]  # on renvoie le reste du fichier

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
            elif "NOTE_" in line.upper():
                h = line.split(",")  # on transforme la ligne en tableau
                no_track = int(h[0])  # string vers entier
                self.trackList[no_track - 1].append(line)
        return

    def get_time_signature(self, line):
        # cette méthode récupère les données relatives à la signature temporelle d'un morceau
        line = line.split(",")
        self.tsNum = int(line[3])
        self.tsDenom = int(line[4])
        self.tsClick = int(line[5])
        self.tsNotesQ = int(line[6])
        self.tempsNoteRef = int(self.division * (4 / 2 ** self.tsDenom))  # durée de la note de référence
        h = self.tempsNoteRef
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
        self.note_to_time_dict = {val: ind for ind, val in self.time_to_note_dict.items()}  # création du dictionnaire inverse
        self.liste_notes = [int(k) for k in self.time_to_note_dict]  # liste des notes

    def get_key_signature(self, line):
        # cette méthode récupère les données relatives à la key_signature d'un morceau
        line = line.split(",")
        self.ksKey = int(line[3])
        self.ksMinMaj = line[4]

    def get_smpte_offset(self, line):
        # cette méthode récupère les données relatives au smpte_offset d'un morceau
        line = line.split(",")
        self.smpteHour = int(line[3])
        self.smpteMinute = int(line[4])
        self.smpteSecond = int(line[5])
        self.smpteFrame = int(line[6])
        self.smpteFracFrame = int(line[7])

    def get_track(self, numero):
        # renvoie la piste correspondant au numéro si le numéro est valide
        if 0 < numero <= self.nbTracks:
            return self.trackList[numero - 1]
        else:
            return None  # Error : Incorrect track number

    def arrondi_note(self, time):
        # arrondit une note à la plus proche existante et renvoie la nouvelle note
        L = [abs(k - abs(time)) for k in self.liste_notes]
        note = self.liste_notes[L.index(min(L))]
        return note

    def positionMesure(self, piste):
        # pour la piste demandée, renvoie la même piste avec les positions de chaque appui/relâchement de touche dans sa mesure ajoutées en fin d'évènement
        L = []
        duree_mesure = self.tsNum * self.tempsNoteRef  # durée totale d'une mesure
        time2 = 0  # temps de "fin" de la note "0"
        debut_mesure = 0  # temps de début de la mesure
        position = 1
        while piste:

            note_deb = piste[0].split(",")
            time1 = int(note_deb[1])  # temps de début de la note
            touche = int(note_deb[4])  # numéro de la touche

            if time1 > time2:  # si la note actuelle n'est pas jouée directement après la fin de la note précédente
                position += 1

            b = 0
            note_fin = [-1, -1, -1, -1, -1]
            while int(note_fin[4]) != touche:  # on cherche la note qui termine
                b += 1
                note_fin = piste[b].split(",")
            time2 = int(note_fin[1])  # récupération temps de fin de la note

            if time1 - debut_mesure >= duree_mesure:  # la nouvelle note est dans une autre mesure
                position = 1
                debut_mesure = time1

            L.append(piste[0] + ", " + str(position))  # on sauvegarde la position dans la mesure
            L.append(piste[b] + ", " + str(position))

            position += 1

            piste = piste[1:b] + piste[b + 1:]  # on enleve les deux lignes

        return L

    def getFormat(self, format_infos):
        # renvoie l'encodage du fichier dans le format spécifié par le parametre format_infos
        filenames = []
        files_content = []

        self.format_infos = format_infos
        self.types_presents = [self.all_types[k] for k in self.format_infos["ListeTypesElements"]]  # on liste tous les types présents (pour avoir un comportement par défaut si un n'apparaît pas)

        if self.format_infos["FusionPiste"] == "1":  # on veut fusionner les pistes
            content, ensemble_elements = self.csv_to_format_select()  # on récupère toutes les pistes du morceau

            filenames.append(self.filename.replace("csv", "format"))  # ajout du nom de sauvegarde
            nb_elements = len(ensemble_elements)  # nombre d'éléments
            elements = "\n".join([str(ensemble_elements[k]) for k in range(nb_elements)])  # fabrication de l'affchage des dictionnaires d'éléments
            a_ecrire = "\n".join([str(nb_elements), elements]) + "\n" + content  # contenu à écrire
            files_content.append(a_ecrire)
        else:  # on prend toutes les pistes séparément
            for a in range(self.nbTracks):  # on parcourt les pistes
                if self.trackList[a]:  # la piste n'est pas vide de notes
                    content, ensemble_elements = self.csv_to_format_select(a + 1)  # récupération d'une piste en particulier
                    if content != '':
                        filenames.append(self.filename.replace(".csv", "") + "-" + str(a + 1) + ".format")  # ajout du nom de fichier
                        nb_elements = len(ensemble_elements)  # nombre d'éléments dans une note
                        elements = "\n".join([str(ensemble_elements[k]) for k in range(nb_elements)])  # transformation en string des ensembles
                        a_ecrire = "\n".join([str(nb_elements), elements]) + "\n" + content  # chaine à ecrire
                        files_content.append(a_ecrire)

        return filenames, files_content

    def csv_to_format_select(self, numero=None):
        # transforme la piste spécifiée par numero dans le format demandé
        if numero is None:  # on doit fusionner les pistes
            L = []
            for a in range(self.nbTracks):  # parcourt des pistes
                piste = self.get_track(a)
                if piste:  # si la piste n'est pas vide
                    if "PM" in self.format_infos["ListeTypesElements"] or self.format_infos["DecoupeMesure"] != -1:
                        # si une des valeurs implique la position de la note dans la mesure ou que les mesures doivent être découpées
                        piste = self.positionMesure(piste)  # on récupère les positions des notes
                    for note in piste:
                        time = int(note.split(",")[1])  # on récupère le temps pour le triage
                        L.append([time, note])  # on ajoute toutes les notes dans la même liste
            L.sort()  # triage de la liste des notes
            L = [k[1] for k in L]
        else:
            L = self.get_track(numero)  # on récupère la seule piste demandée
            if "PM" in self.format_infos["ListeTypesElements"] or self.format_infos["DecoupeMesure"] != -1:
                # si une des valeurs implique la position de la note dans la mesure ou que les mesures doivent être découpées
                L = self.positionMesure(L)  # on récupère les positions des notes
        chaine_retour, ensemble_elements = self.csv_to_format(L)
        return chaine_retour, ensemble_elements

    def csv_to_format(self, L):
        # renvoie la liste L transformée au format .csv
        nb_elements = int(self.format_infos["NombreElements"])  # récupération du nombre d'éléments dans une note
        liste_types_elements = self.format_infos["ListeTypesElements"]  # et des types pour chaque élément

        if self.format_infos["FracNote"] == "0":  # la note doit être fractionnée
            self.elt_sep = ":"  # séparateur d'éléments
            nb_ensemble = nb_elements
        else:
            self.elt_sep = ";"
            nb_ensemble = 1

        bos = self.elt_sep.join(["@" for _ in range(int(nb_elements / nb_ensemble))])
        eos = self.elt_sep.join(["&" for _ in range(int(nb_elements / nb_ensemble))])
        note_bos = self.elt_sep.join(["@" for _ in range(nb_elements)])  # création du
        note_eos = self.elt_sep.join(["&" for _ in range(nb_elements)])
        ensemble_elements = [{bos, eos} for _ in range(nb_ensemble)]  # on crée autant les ensembles d'éléments

        chaine_retour = note_bos + " "  # la chaine de retour commence par un BOS suivi par un espace

        last_touche = 45  # dernière touche appuyée (pour encodage différentiel des touches)
        time2 = 0  # temps de fin de la dernière note
        save = 0
        numero_mesure = 1
        max_mesures = int(self.format_infos["DecoupeMesure"])  # nombre de mesures dans une séquence
        if "PM" in liste_types_elements or max_mesures != -1:  # si on a besoin de la position d'une manière ou d'une autre
            old_position = int(L[0].split(",")[6])  # on la récupère
        else:
            old_position = None

        while L:
            line1 = L[0].split(",")  # récupération de la note de début et transformation en liste
            piste1 = int(line1[0])  # récupération numéro piste
            time1 = int(line1[1])  # récupération du Time
            touche = int(line1[4])  # récupération de la Note
            velocite1 = int(line1[5])  # récupération de la vélocité
            if "PM" in liste_types_elements or max_mesures != -1:  # si on a besoin de la position d'une manière ou d'une autre
                position = int(line1[6])  # on la récupère
            else:
                position = None

            b = 0  # indice de l'évènement "relâcher touche"
            line2 = [-1, -1, -1, -1, -1, -1]
            while int(line2[4]) != touche or int(line2[0]) != piste1:  # on cherche l'évènement "relâcher touche"
                b += 1
                line2 = L[b].split(",")

            velocite2 = int(line2[5])  # récuperation de la deuxième vélocité

            if time1 != time2 and self.format_infos["EncodeSilences"] == 1:  # la nouvelle note ne se finit pas à la fin de la précédente
                new_note = self.createNote(True, time1, time2, touche, last_touche, velocite1, velocite2, position + 1)  # on crée la note comme un silence
                note_split = new_note.split(":")
                for a in range(nb_ensemble):
                    ensemble_elements[a].add(note_split[a])  # on ajoute les nouveaux éléments à leurs ensembles respectifs
                chaine_retour += new_note + " "  # on ajoute la note suivie d'un espace au morceau

            if max_mesures != -1 or "PM" in liste_types_elements:
                if position < old_position:  # lorsqu'on rentre dans une nouvelle mesure
                    numero_mesure += 1
                    if numero_mesure > max_mesures:
                        chaine_retour += "\n"  # on saute une ligne dans le fichier
                        numero_mesure = 1

            time2 = int(line2[1])  # récupération deuxième temps
            new_note = self.createNote(False, time1, save, touche, last_touche, velocite1, velocite2, position)  # on crée la note comme note jouée
            note_split = new_note.split(":")
            for a in range(nb_ensemble):
                ensemble_elements[a].add(note_split[a])  # on ajoute les nouveaux éléments à leurs ensembles respectifs

            chaine_retour += new_note + " "  # on ajoute la note suivie d'un espace au morceau

            old_position = position
            last_touche = touche
            save = time1

            L = L[1:b] + L[b + 1:]  # on enleve les deux lignes
        chaine_retour += note_eos  # on finit la chaine par un eos
        return chaine_retour, ensemble_elements

    def createNote(self, is_silence, time1, time2, touche, last_touche, velocite1, velocite2, position):
        # fonction appelée pour créer une note en fonction des paramètres
        liste_types_elements = self.format_infos["ListeTypesElements"]
        types_values = dict()

        if "TEMPS" in self.types_presents:  # différentiation selon les différents moyens de coder le temps
            TEMPS = None
            if "IIN" in liste_types_elements:  # codage par intervalle entre notes
                TEMPS = self.arrondi_note(time1 - time2)
            types_values["TEMPS"] = str(TEMPS)
        if "TOUCHE" in self.types_presents:  # différentiation selon les différents moyens de coder les touches
            TOUCHE = None
            if "TD" in liste_types_elements:  # encodage différentiel des touches
                saut_touche = touche - last_touche
                TOUCHE = saut_touche
            if "TNB" in liste_types_elements:  # encodage classique des touches
                TOUCHE = touche
            types_values["TOUCHE"] = str(TOUCHE)
        if "VELOCITE" in self.types_presents:  # différentiation selon les différents moyens de coder la vélocité
            VELOCITE = None
            if "V" in liste_types_elements:  # on prend la vélocité la plus grande
                VELOCITE = max(velocite1, velocite2)
            types_values["VELOCITE"] = str(VELOCITE)
        if "TYPE" in self.types_presents:  # différentiation selon les différents moyens de coder le type d'une note (longueur)
            TYPE = None
            if "TN" in liste_types_elements:
                duree = self.arrondi_note(time2 - time1)
                TYPE = self.time_to_note_dict[duree]
                if is_silence:
                    TYPE = TYPE.upper()
            types_values["TYPE"] = str(TYPE)
        if "POSITION" in self.types_presents:
            POSITION = None
            if "PM" in liste_types_elements:
                POSITION = position
            types_values["POSITION"] = str(POSITION)

        # on renvoie les éléments de la note dans une liste selon l'ordre précis spécifié par le format
        return self.elt_sep.join([types_values[val] for val in self.types_presents])

    def format_to_csv(self, values):
        # transforme une chaine encodée selon le format choisi et renvoie le csv associé
        liste_types_elements = self.format_infos["ListeTypesElements"]
        default_values_by_elements = {"TEMPS": None, "TOUCHE": "69", "VELOCITE": "80", "TYPE": self.time_to_note_dict[self.tempsNoteRef], "POSITION": None}  # valeurs par défaut pour chaque champ

        # lignes à écrire dans le .csv
        header = "0, 0, Header, {0}, {1}, {2}\n".format(self.format, self.nbTracks, self.division)
        start1 = "1, 0, Start_track\n"
        smpte = "1, 0, SMPTE_offset, {0}, {1}, {2}, {3}, {4}\n".format(self.smpteHour, self.smpteMinute, self.smpteSecond, self.smpteFrame, self.smpteFracFrame)
        time_s = "1, 0, Time_signature, {0}, {1}, {2}, {3}\n".format(self.tsNum, self.tsDenom, self.tsClick, self.tsNotesQ)
        key_s = "1, 0, Key_signature, {0},{1}".format(self.ksKey, self.ksMinMaj)
        tempo1 = "1, 0, Tempo, {0}\n".format(857142)
        origine = '1, 0, Text_t, "Song generated by MusicBox (https://github.com/Karatsuban/MusicBox)"\n'

        csv_notes_list = [header, start1, origine]
        # ajout des lignes complètes (=auxquelles il ne manque pas d'information)
        if "None" not in smpte:
            csv_notes_list += [smpte]
        csv_notes_list += [time_s]
        if "None" not in key_s:
            csv_notes_list += [key_s]
        csv_notes_list += [tempo1]

        all_notes = values.split()  # on découpe l'entrée note par note
        temps = 0
        liste_note = []
        last_touche = 45  # dernière touche appuyée

        for note in all_notes:
            nuplet = note.split(self.elt_sep)  # on découpe selon le séparateur d'éléments

            element_values = copy.deepcopy(default_values_by_elements)  # copie des valeurs par défaut de chaque élément
            for a in range(len(nuplet)):
                element_values[self.types_presents[a]] = nuplet[a]  # à l'élément de type "types_present[a]" de element_values, on assigne la valeur extraite du n-uplet

            if element_values["TYPE"].upper() == element_values["TYPE"]:  # c'est un silence
                element_values["TYPE"] = element_values["TYPE"].lower()
                is_silence = True
            else:
                is_silence = False

            element_values["TYPE"] = self.note_to_time_dict[element_values["TYPE"]]  # conversion du type de la note en durée

            if element_values["TEMPS"] is None:  # si on a pas l'information du temps entre deux notes...
                element_values["TEMPS"] = element_values["TYPE"]  # par défaut, on y met la longueur de la note elle-même

            temps += int(element_values["TEMPS"])  # on incrémente le temps global
            if not is_silence:
                if "TD" in liste_types_elements:  # si l'encodage des touches se fait par saut
                    element_values["TOUCHE"] = (int(element_values["TOUCHE"]) + last_touche) % 89  # on ne doit pas jouer une touche qui n'existe pas
                    last_touche = element_values["TOUCHE"]  # la dernière touche appuyée est celle qu'on vient de calculer

                # création de deux évènements par note
                liste_note.append([temps, "2, {0}, Note_on_c, 0, {1}, {2}\n".format(temps, element_values["TOUCHE"], element_values["VELOCITE"])])  # création de l'évènement "appui de touche"
                temps_fin = temps + int(element_values["TYPE"])
                liste_note.append([temps_fin, "2, {0}, Note_on_c, 0, {1}, {2}\n".format(temps_fin, element_values["TOUCHE"], 0)])  # la vélocité est mise à 0 (équivalent de Note_off_c)
        liste_note.sort()  # on trie les notes dans l'ordre croissant

        # dernière lignes à écrire
        tempo2 = "1, {0}, Tempo, {1}\n".format(temps, 857142)
        end1 = "1, {0}, End_track\n".format(temps)  # fin du track au temps du dernier tempo
        start2 = "2, 0, Start_track\n"

        csv_notes_list += [tempo2, end1, start2]

        for note in liste_note:
            csv_notes_list.append(note[1])  # ajout de tous les évènements des touches

        end2 = "2, {0}, End_track\n".format(temps)  # temps de la dernière note
        end_of_file = "0, 0, End_of_file"

        csv_notes_list += [end2, end_of_file]

        return csv_notes_list
