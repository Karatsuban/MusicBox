# !/usr/bin/python3
# coding: utf-8

import datetime
from source.model import RNN, Morceau
import py_midicsv as pm
import os
import matplotlib.pyplot as plt
import torch

rnn_object = None
listeMorceaux = None


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


def conversion_en_mid(name_out, csv_content):
    midi_object = pm.csv_to_midi(csv_content)
    # Save the parsed MIDI file to disk
    with open(name_out, "wb") as output_file:
        midi_writer = pm.FileWriter(output_file)
        midi_writer.write(midi_object)
    return


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


def check_conversions(parametres):
    global listeMorceaux
    # on récupère tous les noms des fichiers .mid du dossier
    midi_path = parametres["URL_Dossier"]  # chemin du dossier contenant les .mid
    csv_path = parametres["URL_Dossier"] + os.sep + "CSV"  # chemin du dossier contenant les .csv
    format_path = parametres["URL_Dossier"]+os.sep+"Conversion_"+parametres["TypeGeneration"]  # chemin du dossier contenant les .format
    graph_path = parametres["URL_Dossier"]+os.sep+"Graphiques"
    gen_path = parametres["URL_Dossier"]+os.sep+"Resultat"
    model_path = parametres["URL_Dossier"]+os.sep+"Modèles save"

    listeFichiersMidi = [i for i in os.listdir(midi_path) if ".mid" in i]

    # création (s'ils n'existent pas) des dossiers utiles
    os.makedirs(graph_path, exist_ok=True)  # contiendra les graphiques
    os.makedirs(csv_path, exist_ok=True)  # contiendra les conversions en CSV des .mid
    os.makedirs(gen_path, exist_ok=True)  # contiendra les fichiers générés
    os.makedirs(model_path, exist_ok=True)  # contiendra les sauvegardes de modèles
    os.makedirs(format_path, exist_ok=True)  # contiendra les fichiers format

    for midi_files in listeFichiersMidi:  # pour chaque fichier .mid ...
        nom = midi_files.replace(".mid", ".csv")
        if nom not in os.listdir(csv_path):  # ... si sa conversion en .csv n'existe pas
            conversion_en_csv(csv_path, midi_path, midi_files)  # on la crée

    # for fichier_csv in os.listdir(csv_path): #on parcourt les fichiers csv
    #    dessine_graphe(csv_path, fichier_csv, graph_path)

    # on récupère tous les noms des fichiers du dossier Conversion pour ne pas avoir à reconvertir des fichiers
    listeFichiersConvertis = [i for i in os.listdir(format_path)]

    listeFichiersAConvertir = []
    # on vérifie si les .format existe.
    for nom_mid in listeFichiersMidi:
        nom_format = nom_mid.replace(".mid", ".format")  # en admettant que notre extension sera ".format"
        nom_csv = nom_mid.replace(".mid", ".csv")
        if nom_format not in listeFichiersConvertis:
            listeFichiersAConvertir.append(nom_csv)

    if listeFichiersAConvertir == [] and listeFichiersConvertis != []:
        listeFichiersAConvertir.append(os.listdir(csv_path)[0])
        # totalement artificiel, pour avoir au moins 1 objet morceau pour plus tard

    listeMorceaux = []  # liste d'objets de type Morceau
    # on vérifier si liseteFichiersAConvertir est vide.
    if listeFichiersAConvertir:
        # on tranforme les fichiers csv non convertis en objets Morceau
        for csv_files in listeFichiersAConvertir:
            listeMorceaux.append(Morceau.Morceau(csv_path + os.sep + csv_files))

    # conversion des morceaux dans le bon format
    for m in listeMorceaux:
        filenames, files_content = m.getFormat(parametres["TypeGeneration"])  # récupération de tous les fichiers à écrire et leurs contenus
        for a in range(len(filenames)):
            complete_path = format_path + os.sep + filenames[a]
            ecrire_fichier(complete_path, files_content[a])  # pour chaque fichier, on écrit son contenu dans le dossier des conversions
    return


def get_input_liste(parametres):
    format_path = parametres["URL_Dossier"]+os.sep+"Conversion_"+parametres["TypeGeneration"]
    is_stat = parametres["ChoixAffichageStatistiques"] == 1  # l'utilisateur veut afficher les statistiques
    nb_elements = 0
    liste_textes = []
    liste_ensemble = None
    liste_dicos = []  # contiendra les nombres d'occurences de chaques élément de note
    sum_len_seq = 0
    nb_seq = 0
    nb_notes = 0
    nb_fichiers = 0

    for m in os.listdir(format_path):
        nb_fichiers += 1

        content = lire_fichier(format_path + os.sep + m)  # contenu du fichier

        if liste_ensemble is None:
            nb_elements = int(content[0])  # la première ligne du fichier donne le nombre d'éléments composant une note
            liste_ensemble = [set() for _ in range(nb_elements)]  # création de la liste des ensembles si elle n'existe pas
            liste_dicos = [{} for _ in range(nb_elements)]

        for a in range(nb_elements):  # pour chaque dictionnaire lu
            new_ensemble = eval(content[a+1])
            liste_ensemble[a] = liste_ensemble[a].union(new_ensemble)  # on le rajoute à l'ensemble correspondant
            if is_stat:
                for key in new_ensemble:
                    if key not in liste_dicos[a]:  # si cet élément n'a pas été repertorié, on le crée avec un compteur à 0
                        liste_dicos[a][key] = 0

        if is_stat:
            for num_seq in range(len(content[nb_elements+1:])):  # parcourt des séquences
                nb_seq += 1
                seq = content[nb_elements+1+num_seq].replace("\n", "").split()
                sum_len_seq += len(seq)
                for note in seq:  # parcourt des notes
                    nb_notes += 1
                    for idx, val in enumerate(note.split(":")):  # parcourt des éléments des notes
                        liste_dicos[idx][val] += 1  # mise à jour du compteur

        liste_textes += content[nb_elements + 1:]  # recuperation des donnees sur les notes

    if is_stat:
        print("---------- Statistiques -----------")
        print("Format : ", parametres["TypeGeneration"])
        print("Nombre total fichiers entraines : ", nb_fichiers)
        print("Nb notes moyen par sequences : ", round(sum_len_seq / nb_seq, 3))
        for i in range(nb_elements):
            for key, _ in liste_dicos[i].items():
                liste_dicos[i][key] = round((liste_dicos[i][key] / nb_notes) * 100, 3)
            print("{} valeurs possible pour element n°{}\nNb occurences valeurs element n°{} : {}".format(len(liste_dicos[i]), i, i, liste_dicos[i]))
        print("-----------------------------------")

    return liste_textes, liste_ensemble


def train(parametres, is_model, queue, finQueue):
    global rnn_object
    rnn_parametres = get_rnn_parameters(parametres)

    if not is_model:  # s'il n'y a pas de modèle en cours...
        check_conversions(parametres)  # on vérifie que toutes les conversions ont bien été faites
        liste_textes, liste_ensembles = get_input_liste(parametres)
        rnn_object = RNN.RNN(liste_textes, rnn_parametres, liste_ensembles)  # ...on crée un modèle avec les bons paramètres
    list_losses, list_acc = rnn_object.train(int(parametres["NombreEpoch"]), int(parametres["NombreSequenceBatch"]), queue, finQueue)  # on entraîne le modèle
    if parametres["ChoixAffichageGraphiques"] == 1:
        graph_path = parametres["URL_Dossier"]+os.sep+"Graphiques"
        saveGraph(graph_path, list_losses, list_acc)
    return


def genereMorceaux(parametres):
    out = rnn_object.generate(int(parametres["NombreMorceaux"]), int(parametres["DureeMorceaux"]))  # on génère les morceaux en fonction des paramètres
    gen_path = parametres["URL_Dossier"] + os.sep + "Resultat"
    temp = getDate()
    temp += "_"+parametres["TypeGeneration"]

    for index in range(len(out)):
        save_name = gen_path+os.sep+str(temp)+"_"+str(index)+".mid"
        csv_content = listeMorceaux[0].getCSV(out[index], parametres["TypeGeneration"])
        conversion_en_mid(save_name, csv_content)
    return


def getDate():
    date = datetime.datetime.now()
    dateG = datetime.date(date.year, date.month, date.day)
    dg = dateG.isoformat()
    heureG = datetime.time(date.hour, date.minute, date.second)
    hg = heureG.strftime('%H-%M-%S')
    temp = "_".join([dg, hg])
    return temp


def saveGraph(graph_path, list_losses, list_acc):
    nb_epoch = len(list_acc)  # nombre d'epoch effectuée
    nb_elements = len(list_losses)  # nombre d'éléments par note
    couleurs = ['b', 'g', 'r', 'k', 'c', 'm', 'y', 'w']

    fig_losses, axe_losses = plt.subplots()  # une figure par loss d'élément
    fig_acc, axe_acc = plt.subplots()  # une figure pour l'accuracy

    x = [k for k in range(nb_epoch)]  # abscisse des graphes (numéro d'epoch)
    for a in range(nb_elements):
        label_name = "Loss element n°" + str(a)
        axe_losses.plot(x, list_losses[a], label=label_name, color=couleurs[a % 8])  # un graphe par élément
    axe_losses.set_title("Loss de chaque element de note par epoch")
    axe_losses.set_xlabel("Nb Epochs")
    axe_losses.set_ylabel("Loss")
    axe_losses.legend()

    axe_acc.plot(x, list_acc, label="Accuracy", color="b")  # création du graphe pour l'accuracy
    axe_acc.set_title("Accuracy du modèle par epoch")
    axe_acc.set_xlabel("Nb Epochs")
    axe_acc.set_ylabel("Accuracy")
    axe_acc.legend()

    total_epoch = getModelParametres()["TotalEpoch"]  # on récupère le nombre total depoch du modèle
    loss_savename = getDate()+"_"+str(total_epoch)+"_Graph_Loss.png"  # création du nom de sauvegarde
    acc_savename = getDate()+"_"+str(total_epoch)+"_Graph_Accuracy.png"

    # enregistrement des graphiques
    fig_losses.savefig(graph_path+os.sep+loss_savename)
    fig_acc.savefig(graph_path+os.sep+acc_savename)

    return
