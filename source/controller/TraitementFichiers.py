# !/usr/bin/python3
# coding: utf-8

import datetime
from source.model import RNN, Morceau
import py_midicsv as pm
import operator
import os
import matplotlib.pyplot as plt
import torch

rnn_object = None
listeMorceaux = None


def genereNew(parametres):
    genereMorceaux(parametres, listeMorceaux, rnn_object)


def saveModel(save_path):
    parametres = rnn_object.getParametres()
    torch.save(parametres, save_path)


def loadModel(load_path, user_param):
    global rnn_object
    load_params = torch.load(load_path, map_location=torch.device('cpu'))  # on lit le fichier de sauvegarde
    check_conversions(user_param)  # on vérifie que toutes les conversions ont bien eu lieu
    param_list = get_rnn_parameters(user_param)
    input_list, ensemble_list = get_input_liste(user_param)
    rnn_object = RNN.RNN(input_list, param_list, ensemble_list, load_params)
    return load_params


def getModelParametres():
    return rnn_object.getParametres()


def lire_fichier(nom):
    file = open(nom, 'r')
    lines = file.readlines()
    file.close()
    for a in range(len(lines)):
        lines[a] = lines[a].replace("\n", "")
    return lines


def ecrire_fichier(nom, donnees):
    with open(nom, 'w') as file:
        for a in donnees:
            file.write(a)


def get_rnn_parameters(parametres):
    L = "TauxApprentissage,NombreEpoch,NombreDimensionCachee,NombreLayer,NombreSequenceBatch,TypeGeneration"
    p = []
    for key in L.split(","):
        p.append(parametres[key])
    return p


def conversion_en_csv(writeAddr, readAddr, name_in):
    filename = name_in.replace(".mid", ".csv")

    csv_list = pm.midi_to_csv(readAddr + os.sep + name_in)  # transformation de midi en csv
    name_out = writeAddr + os.sep + filename

    # ecriture du fichier
    with open(name_out, 'w+') as file_out:
        for row in csv_list:
            file_out.write(row)
    return


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

    X = list(x1.union(x2))  # abscisse du graphe
    X.sort()

    y1 = [notes_non_quantif.count(k) for k in X]
    y2 = [notes_quantif.count(k) for k in X]

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


def check_conversions(parametres):  # anciennement main
    global listeMorceaux
    # on récupère tous les noms des fichiers .mid du dossier
    listeFichiers = [i for i in os.listdir(parametres["URL_Dossier"]) if ".mid" in i]

    # Bloc 1
    os.makedirs(parametres["URL_Dossier"]+os.sep+"CSV", exist_ok=True)
    os.makedirs(parametres["URL_Dossier"]+os.sep+"Conversion_rythme", exist_ok=True)
    os.makedirs(parametres["URL_Dossier"]+os.sep+"Conversion_melodie", exist_ok=True)
    os.makedirs(parametres["URL_Dossier"]+os.sep+"Resultat", exist_ok=True)
    os.makedirs(parametres["URL_Dossier"]+os.sep+"Graphiques", exist_ok=True)
    os.makedirs(parametres["URL_Dossier"]+os.sep+"Modèles save", exist_ok=True)

    # on récupère tous les fichier csv du dossier csv avec addresse: csv_path
    csv_path = parametres["URL_Dossier"] + os.sep + "CSV"

    # Bloc 2
    # on vérifi si .csv existe déjà (si non, on les crée).
    for midi_files in listeFichiers:
        nom = midi_files.replace(".mid", ".csv")
        if nom not in os.listdir(csv_path):
            conversion_en_csv(csv_path, parametres["URL_Dossier"], midi_files)

    # for fichier_csv in os.listdir(csv_path): #on parcourt les fichiers csv
    #    dessine_graphe(csv_path, fichier_csv, parametres["URL_Dossier"]+os.sep+"Graphiques")

    # Bloc 3
    # on récupère tous les fichiers .format dans listeFichiersConvertis
    if parametres["TypeGeneration"] == "Rythme seulement":
        # on récupère tous les noms des fichiers du dossier /Conversion_rythme pour ne pas avoir à reconvertir des fichiers
        listeFichiersConvertis = [i for i in os.listdir(parametres["URL_Dossier"]+os.sep+"Conversion_rythme")]

    if parametres["TypeGeneration"] == "Rythme et mélodie":
        # on récupère tous les noms des fichiers du dossier /Conversion_melodie pour ne pas avoir à reconvertir des fichiers
        listeFichiersConvertis = [i for i in os.listdir(parametres["URL_Dossier"]+os.sep+"Conversion_melodie")]

    listeFichiersAConvertir = []
    # on vérifie si les .format existe.
    for nom_mid in listeFichiers:
        nom_format = nom_mid.replace(".mid", ".format")  # en admettant que notre extension sera ".format"
        nom_csv = nom_mid.replace(".mid", ".csv")
        if nom_format not in listeFichiersConvertis:
            listeFichiersAConvertir.append(nom_csv)

    if listeFichiersAConvertir == [] and listeFichiersConvertis != []:
        listeFichiersAConvertir.append(os.listdir(csv_path)[0])
        # totalement artificiel, pour avoir au moins 1 objet morceau pour plus tard

    # Bloc 4
    listeMorceaux = []  # liste d'objets de type Morceau
    # on vérifier si liseteFichiersAConvertir est vide.
    if listeFichiersAConvertir:
        # on tranforme les fichiers csv non convertis en objets Morceau
        for csv_files in listeFichiersAConvertir:
            listeMorceaux.append(Morceau.Morceau(csv_path + os.sep + csv_files))

    # Bloc 5
    # on prépare les morceaux pour le RNN et afficher les info de data setting
    longTotale = 0
    counter = 0
    contentTotaleDico = {}
    tempDico = {}
    noteDico = {}
    toucheDico = {}
    for m in listeMorceaux:
        counter += 1
        if parametres["TypeGeneration"] == "Rythme seulement":
            nom = parametres["URL_Dossier"]+os.sep+"Conversion_rythme"+os.sep+m.filename.replace(".csv", "")
            content, ensemble_elements = m.preparer_track_rythme()  # on récupère toutes les pistes du morceau dans une liste

            if parametres["ChoixAffichageDataInfo"] == 1:  # si utilisateur a choisi d'afficher les Data info
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
                    nb_elements = len(ensemble_elements)  # nombre d'éléments dans une note
                    elements = "\n".join([str(ensemble_elements[k]) for k in range(nb_elements)])  # transformation en string des ensembles
                    a_ecrire = "\n".join([str(nb_elements), elements]) + "\n" + content[index]  # chaine à ecrire
                    ecrire_fichier(savename, a_ecrire)  # on écrit chaque piste dans un fichier différent

        if parametres["TypeGeneration"] == "Rythme et mélodie":
            resTab = []
            nom = parametres["URL_Dossier"]+os.sep+"Conversion_melodie"+os.sep+m.filename.replace("csv", "format")
            content, ensemble_elements = m.preparer_track_melodie()  # on récupère toutes les pistes du morceau

            nb_elements = len(ensemble_elements)  # nombre d'éléments
            elements = "\n".join([str(ensemble_elements[k]) for k in range(nb_elements)])  # transformations
            a_ecrire = "\n".join([str(nb_elements), elements]) + "\n" + content
            ecrire_fichier(nom, a_ecrire)  # on écrit tout dans un seul morceau

            if parametres["ChoixAffichageDataInfo"] == 1:
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

    if parametres["ChoixAffichageDataInfo"] == 1:
        if parametres["TypeGeneration"] == "Rythme seulement":
            print("----------Rythme seulement------------")
            print("****** Nombre total de fichiers entrainés : ", counter)
            print("****** Moyenne des sequences : ", moyenne_seq(longTotale, counter))
            print("****** Nombre d'occurence de chaque note des sequences : ", count_freq_dico(contentTotaleDico))
            print("--------------------------------------")
        if parametres["TypeGeneration"] == "Rythme et mélodie":
            print("----------Rythme et mélodie-----------")
            print("****** Nombre total de fichiers entrainés : ", counter)
            print("****** Moyenne des sequences : ", moyenne_seq(longTotale, counter))
            print("****** Nombre d'occurence de chaque temp des sequences : ", len(count_freq_dico(tempDico)), count_freq_dico(tempDico))
            print("****** Nombre d'occurence de chaque note des sequences : ", len(count_freq_dico(noteDico)), count_freq_dico(noteDico))
            print("****** Nombre d'occurence de chaque touche des sequences : ", len(count_freq_dico(toucheDico)), count_freq_dico(toucheDico))
            print("--------------------------------------")


def train(parametres, is_model, queue, finQueue):
    global rnn_object
    rnn_parametres = get_rnn_parameters(parametres)

    if not is_model:  # s'il n'y a pas de modèle en cours...
        check_conversions(parametres)  # on vérifie que toutes les conversions ont bien été faites
        liste_textes, liste_ensembles = get_input_liste(parametres)
        rnn_object = RNN.RNN(liste_textes, rnn_parametres, liste_ensembles)  # ...on crée un modèle avec les bons paramètres
    rnn_object.train(int(parametres["NombreEpoch"]), int(parametres["NombreSequenceBatch"]), queue, finQueue)  # on entraîne le modèle


def get_input_liste(parametres):
    liste_textes = []
    liste_ensemble = None
    if parametres["TypeGeneration"] == "Rythme seulement":
        format_path = parametres["URL_Dossier"] + os.sep + "Conversion_rythme"
    elif parametres["TypeGeneration"] == "Rythme et mélodie":
        format_path = parametres["URL_Dossier"] + os.sep + "Conversion_melodie"

    for m in os.listdir(format_path):
        content = lire_fichier(format_path + os.sep + m)
        nb_elements = int(content[0])  # la première ligne du fichier donne le nombre d'éléments composant une note

        if liste_ensemble is None:
            liste_ensemble = [set() for _ in range(nb_elements)]

        for a in range(nb_elements):
            liste_ensemble[a] = liste_ensemble[a].union(eval(content[a+1]))  # on rajoute à l'ensemble

        liste_textes += content[nb_elements + 1:]  # recuperation des donnees sur les notes
    return liste_textes, liste_ensemble


def genereMorceaux(parametres, listeMorceaux, rnn_object):
    out = rnn_object.generate(int(parametres["NombreMorceaux"]), int(parametres["DureeMorceaux"]))  # on génère les morceaux en fonction des paramètres
    date = datetime.datetime.now()
    dateG = datetime.date(date.year, date.month, date.day)
    dg = dateG.isoformat()
    heureG = datetime.time(date.hour, date.minute, date.second)
    hg = heureG.strftime('%H-%M-%S')
    if parametres["TypeGeneration"] == "Rythme seulement":
        temp = "".join([dg, " ", hg, " ", "R"])
    elif parametres["TypeGeneration"] == "Rythme et mélodie":
        temp = "".join([dg, " ", hg, " ", "M"])

    for index in range(len(out)):
        save_name = str(temp)+" "+str(index)
        if parametres["TypeGeneration"] == "Rythme seulement":
            listeMorceaux[0].format_to_csv_rythme(out[index], save_name)  # enregistre le morceau sous format MIDI
        elif parametres["TypeGeneration"] == "Rythme et mélodie":
            listeMorceaux[0].format_to_csv(out[index], save_name)  # enregistre le morceau sous format MIDI


# if __name__ == "__main__":
#     main()
