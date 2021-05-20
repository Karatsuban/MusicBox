# !/usr/bin/python3
#coding: utf-8

import datetime
from source.model import RNN, Morceau
import py_midicsv as pm
import operator
import os
import matplotlib.pyplot as plt

def lire_fichier(nom):
    file = open(nom, 'r')
    lines = file.readlines()
    file.close()
    return "".join(lines) #on retourne la concaténation des lignes du fichier

def ecrire_fichier(nom, donnees):
    with open(nom, 'w') as file :
        for a in donnees:
            file.write(a)


def get_rnn_parameters(parametres):
    l = "TauxApprentissage,NombreEpoch,NombreDimensionCachee,NombreLayer,LongeurSequence,BatchBool,NombreSequenceBatch,NombreMorceaux,DureeMorceaux"
    p = []
    for key in l.split(","):
        p.append(parametres[key])
    return p
##########################################################################
def conversion_en_csv(writeAddr, readAddr, name_in):
    filename = name_in.replace(".mid", ".csv")

    # convertit un fichier .mid en fichier .csv
    csv_list = pm.midi_to_csv(readAddr + os.sep + name_in)  # transformation de midi en csv
    name_out = writeAddr + os.sep + filename

    # ecriture du fichier
    with open(name_out, 'w+') as file_out:
        for row in csv_list:
            file_out.write(row)
    return

###############################################
def list2string(liste):
    string = "".join(liste)
    return string

def count_freq_dico(dico):
    long = 0
    tabValue = dico.values()
    for i in tabValue:
        long += i
    for i in dico:
        dico[i] /= long
        dico[i] = round(dico[i], 2)
    dico = sorted(dico.items(), key=operator.itemgetter(1), reverse=True)
    return dico

def count_long_seq(string):
    res = len(string)
    return res


def moyenne_seq(nbT, nbF):
    moyenneSeq = nbT / nbF
    return moyenneSeq



def dessine_graphe(readpath, filename, savepath):
	plt.clf()
	morceau = Morceau.Morceau(readpath+os.sep+filename)
	notes_non_quantif = morceau.get_notes()
	notes_quantif = morceau.get_notes(True)
	x1 = set(notes_non_quantif)
	x2 = set(notes_quantif)
	print(x1)
	print(x2)
	X = list(x1.union(x2)) # abscisse du graphe
	X.sort()
	print(X)

	y1 = [notes_non_quantif.count(k) for k in X]
	y2 = [notes_quantif.count(k) for k in X]

	print(y1)
	print(y2)
	
	pos = range(len(X))
	rects1 = plt.bar(x=[x+0.2 for x in pos], height=y1, width=0.4, color='red', label="Notes non quantifiees")
	rects2 = plt.bar(x=[x+0.6 for x in pos], height=y2, width=0.4, color='green', label="Notes quantifiees")
	plt.ylabel("Nombre")
	plt.xlabel("Duree notes")
	plt.title("Comparaison notes sur "+filename)
	plt.xticks([index + 0.4 for index in pos], X)

	for rect in rects1:
		height = rect.get_height()
		plt.text(rect.get_x() + rect.get_width() / 2 - 0.05*len(str(height)), height, str(height), ha="center", va="bottom")

	for rect in rects2:
		height = rect.get_height()
		plt.text(rect.get_x() + rect.get_width() / 2 + 0.05*len(str(height)), height, str(height), ha="center", va="bottom")

	plt.legend(loc="upper right")
	plt.savefig(savepath+os.sep+filename.split('.')[0]+'.jpg')

#######################################################

def main(parametres):
    rnn_parametres = get_rnn_parameters(parametres)
    # on récupère tous les noms des fichiers .mid du dossier
    listeFichiers = [i for i in os.listdir(parametres["URL_Dossier"]) if ".mid" in i]

    #Bloc 1
    os.makedirs(parametres["URL_Dossier"]+os.sep+"CSV",exist_ok=True)
    os.makedirs(parametres["URL_Dossier"]+os.sep+"Conversion_rythme",exist_ok=True)
    os.makedirs(parametres["URL_Dossier"]+os.sep+"Conversion_melodie",exist_ok=True)
    os.makedirs(parametres["URL_Dossier"]+os.sep+"Resultat",exist_ok=True)
    os.makedirs(parametres["URL_Dossier"]+os.sep+"Graphiques",exist_ok=True)

    # on récupère tous les fichier csv du dossier csv avec addresse: csv_path
    csv_path = parametres["URL_Dossier"] + os.sep + "CSV"

    #Bloc 2
    # on vérifier si .csv existe déjà (si non, on les crée).
    for midi_files in listeFichiers:
        nom = midi_files.replace(".mid", ".csv")
        if nom not in os.listdir(csv_path):
            conversion_en_csv(csv_path, parametres["URL_Dossier"], midi_files)

    for fichier_csv in os.listdir(csv_path): #on parcourt les fichiers csv
        dessine_graphe(csv_path, fichier_csv, parametres["URL_Dossier"]+os.sep+"Graphiques")


    # Bloc 3
    # on récupère tous les fichiers .format dans listeFichiersConvertis
    if (parametres["TypeGeneration"] == "Rythme seulement"):
        #on récupère tous les noms des fichiers du dossier /Conversion_rythme pour ne pas avoir à reconvertir des fichiers
        listeFichiersConvertis = [i for i in os.listdir(parametres["URL_Dossier"]+os.sep+"Conversion_rythme")]

    if (parametres["TypeGeneration"] == "Rythme et mélodie"):
        #on récupère tous les noms des fichiers du dossier /Conversion_melodie pour ne pas avoir à reconvertir des fichiers
        listeFichiersConvertis = [i for i in os.listdir(parametres["URL_Dossier"]+os.sep+"Conversion_melodie")]

    listeFichiersAConvertir = []
    # on vérifier si les .format existe.
    for nom_csv in os.listdir(csv_path):
        nom = nom_csv.replace(".csv",".format") #en admettant que notre extension sera ".format"
        if nom not in listeFichiersConvertis:
            listeFichiersAConvertir.append(nom_csv)

    if (listeFichiersAConvertir == [] and listeFichiersConvertis != []):
        listeFichiersAConvertir.append(listeFichiersConvertis[0])
        #totalement artificiel, pour avoir au moins 1 objet morceau pour plus tard

    #Bloc 4
    listeMorceaux = [] # liste d'objets de type Morceau
    # on vérifier si liseteFichiersAConvertir est vide.
    if listeFichiersAConvertir:
        # on tranforme les fichiers csv non convertis en objets Morceau
        for csv_files in listeFichiersAConvertir:
            listeMorceaux.append(Morceau.Morceau(csv_path + os.sep + csv_files))


    #Bloc 5
    #on prépare les morceaux pour le RNN et afficher les info de data setting
    liste_textes = []
    longTotale = 0
    counter = 0
    contentTotaleDico = {}
    tempDico = {}
    noteDico = {}
    toucheDico = {}
    for m in listeMorceaux:
        counter += 1
        if (parametres["TypeGeneration"] == "Rythme seulement"):
            nom = parametres["URL_Dossier"]+os.sep+"Conversion_rythme"+os.sep+m.filename
            content = m.preparer_track_rythme() #on récupère toutes les pistes du morceau dans une liste
            contentString = list2string(content)
            longTotale += count_long_seq(contentString)
            for data in contentString:
                if data in contentTotaleDico:
                    contentTotaleDico[data] += 1
                else:
                    contentTotaleDico[data] = 1
            for index in range(len(content)):
                if content[index] != '':
                    savename = nom+"-"+str(index+1)+".format"
                    ecrire_fichier(savename, content[index]) #on écrit chaque piste dans un fichier différent

        if (parametres["TypeGeneration"] == "Rythme et mélodie"):
            resTab = []
            nom = parametres["URL_Dossier"]+os.sep+"Conversion_melodie"+os.sep+m.filename+".format"
            content = m.preparer_track_melodie() # on récupère toutes les pistes du morceau
            contentTab = content.rstrip(' ').split(' ')
            longTotale += count_long_seq(contentTab)
            for i in range(len(contentTab)):
                splitTab = contentTab[i].rstrip(':').split(':')
                resTab.append(splitTab)
            for data in resTab:
                if data[0] in tempDico:
                    tempDico[data[0]] += 1
                if data[0] not in tempDico:
                    tempDico[data[0]] = 1
                if data[1] in noteDico:
                    noteDico[data[1]] += 1
                if data[1] not in tempDico:
                    noteDico[data[1]] = 1
                if data[2] in toucheDico:
                    toucheDico[data[2]] += 1
                if data[2] not in toucheDico:
                    toucheDico[data[2]] = 1
            ecrire_fichier(nom, [content]) # on écrit tout dans un seul morceau

    if (parametres["TypeGeneration"] == "Rythme seulement"):
        print("----------Rythme seulement------------\n" +
              "****** Nombre total de fichier entrainé : %s\n" %counter +
              "****** Moyenne des sequences : %d\n" % moyenne_seq(longTotale, counter) +
              "****** Nombre d'occurence de chaque note des sequences : %s \n" %count_freq_dico(contentTotaleDico)+
              "--------------------------------------")
    if (parametres["TypeGeneration"] == "Rythme et mélodie"):
        print("----------Rythme et mélodie-----------\n" +
              "****** Nombre total de fichier entrainé : %s\n" % counter +
              "****** Moyenne des sequences : %d\n" % moyenne_seq(longTotale, counter) +
              "****** Nombre d'occurence de chaque temp des sequences : %s \n" % count_freq_dico(tempDico) +
              "****** Nombre d'occurence de chaque note des sequences : %s \n" % count_freq_dico(noteDico) +
              "****** Nombre d'occurence de chaque touche des sequences : %s \n" % count_freq_dico(toucheDico) +
              "--------------------------------------")




    #Bloc 6
    for m in listeFichiersConvertis:
        if (parametres["TypeGeneration"] == "Rythme seulement"):
            content = lire_fichier(parametres["URL_Dossier"]+os.sep+"Conversion_rythme"+os.sep+m)
            liste_textes.append(content) #recuperation des donnees

        if (parametres["TypeGeneration"] == "Rythme et mélodie"):
            content = lire_fichier(parametres["URL_Dossier"]+os.sep+"Conversion_melodie"+os.sep+m)
            liste_textes.append(content) #recuperation des donnees

    #Bloc 7
    rnn_object = RNN.RNN(parametres["TypeGeneration"], liste_textes, rnn_parametres) # on crée un objet de type RNN avec les bons paramètres
    out = rnn_object.generate() # on génère les morceaux en fonction des paramètres

    #Bloc 8
    date = datetime.datetime.now()
    temp = "".join([str(date.year),"-",str(date.month),"-",str(date.day)," ",str(date.hour),"-",str(date.minute),"-",str(date.second)])

    for index in range(len(out)):
        save_name = str(temp)+" "+str(index)
        if (parametres["TypeGeneration"] == "Rythme seulement"):
            listeMorceaux[0].format_to_csv_rythme(out[index], save_name) # enregistre le morceau sous format MIDI
        elif (parametres["TypeGeneration"] == "Rythme et mélodie"):
            listeMorceaux[0].format_to_csv(out[index], save_name) # enregistre le morceau sous format MIDI


if __name__ == "__main__":
    main()
