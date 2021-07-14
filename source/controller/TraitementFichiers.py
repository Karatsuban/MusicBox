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
    # fonction permettant de sauvegarder les paramètres d'un modèle
    parametres = rnn_object.getParametres()
    torch.save(parametres, save_path)
    return


def loadModel(load_path, user_param, all_formats):
    # fonction permettant de charger un modèle à partir de paramètres
    global rnn_object
    load_params = torch.load(load_path, map_location=torch.device('cpu'))  # on lit le fichier de sauvegarde
    format_infos = all_formats[load_params["TypeGeneration"]]  # on récupère les infos du format dans lequel a été enregistré le modèle
    check_conversions(user_param, format_infos)  # on vérifie que toutes les conversions ont bien eu lieu
    param_list = get_rnn_parameters(user_param)
    input_list, ensemble_list = get_input_liste(user_param)
    rnn_object = RNN.RNN(input_list, param_list, ensemble_list, load_params)
    return load_params


def getModelParametres():
    # renvoie les paramètres du modèle
    return rnn_object.getParametres()


def lire_fichier(nom):
    # permet de lire un fichier et de renvoyer son contenu
    file = open(nom, 'r')
    lines = file.readlines()
    file.close()
    for a in range(len(lines)):
        lines[a] = lines[a].replace("\n", "")
    return lines


def ecrire_fichier(nom, donnees):
    # écrit les donnees dans le fichier précisé
    with open(nom, 'w') as file:
        for a in donnees:
            file.write(a)
    return


def get_rnn_parameters(parametres):
    # renvoie les paramètres du modèle dans une liste
    L = "TauxApprentissage,NombreEpoch,NombreDimensionCachee,NombreLayer,NombreSequenceBatch,TypeGeneration"
    p = []
    for key in L.split(","):
        p.append(parametres[key])
    return p


def conversion_en_csv(writeAddr, readAddr, name_in):
    # convertit un fichier midi en fichier csv
    filename = name_in.replace(".mid", ".csv")

    csv_list = pm.midi_to_csv(readAddr + os.sep + name_in)  # transformation de midi en csv
    name_out = writeAddr + os.sep + filename

    ecrire_fichier(name_out, csv_list)  # ecriture du fichier
    return


def conversion_en_mid(name_out, csv_content):
    # convertit un fichier csv en fichier midi
    midi_object = pm.csv_to_midi(csv_content)

    with open(name_out, "wb") as output_file:
        midi_writer = pm.FileWriter(output_file)
        midi_writer.write(midi_object)
    return


def check_conversions(parametres, format_infos):
    # crée les dossiers manquants et vérifie que les conversion mid vers csv et csv vers format sont crées, les crée sinon
    global listeMorceaux

    midi_path = parametres["URL_Dossier"]  # chemin du dossier contenant les .mid
    csv_path = parametres["URL_Dossier"] + os.sep + "CSV"  # chemin du dossier contenant les .csv
    format_path = parametres["URL_Dossier"]+os.sep+"Conversion_"+parametres["TypeGeneration"]  # chemin du dossier contenant les .format
    graph_path = parametres["URL_Dossier"]+os.sep+"Graphiques"
    gen_path = parametres["URL_Dossier"]+os.sep+"Resultat"  # chemins des dossiers pour les graphiques, les morceaux générés et les sauvgeardes de modèle
    model_path = parametres["URL_Dossier"]+os.sep+"Modèles save"

    listeFichiersMidi = [i for i in os.listdir(midi_path) if ".mid" in i]  # liste des fichiers midi présents dans le répertoire choisi

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

    # on récupère tous les noms des fichiers du dossier Conversion pour ne pas avoir à reconvertir des fichiers
    listeFichiersConvertis = [i for i in os.listdir(format_path)]

    listeFichiersAConvertir = []
    # on vérifie si les .format existent
    for nom_mid in listeFichiersMidi:
        nom_format = nom_mid.replace(".mid", ".format")  # l'extension des fichiers format est le ".format"
        nom_csv = nom_mid.replace(".mid", ".csv")
        if nom_format not in listeFichiersConvertis:  # si le fichier format associé n'existe pas
            listeFichiersAConvertir.append(nom_csv)  # on le rajoute à la liste des fichiers à convertir

    if listeFichiersAConvertir == [] and listeFichiersConvertis != []:
        listeFichiersAConvertir.append(os.listdir(csv_path)[0])
        # totalement artificiel, pour avoir au moins 1 objet morceau pour plus tard (lors de la conversion sortie du modèle vers csv)

    listeMorceaux = []  # liste d'objets de type Morceau

    if listeFichiersAConvertir:  # on vérifier si liseteFichiersAConvertir est vide.
        # on tranforme les fichiers csv non convertis en objets Morceau
        for csv_files in listeFichiersAConvertir:
            listeMorceaux.append(Morceau.Morceau(csv_path + os.sep + csv_files))

    # conversion des morceaux dans le bon format
    for m in listeMorceaux:
        filenames, files_content = m.getFormat(format_infos)  # récupération de tous les fichiers à écrire et leurs contenus
        for a in range(len(filenames)):
            complete_path = format_path + os.sep + filenames[a]
            ecrire_fichier(complete_path, files_content[a])  # pour chaque fichier, on écrit son contenu dans le dossier des conversions
    return


def get_input_liste(parametres):
    # renvoie toutes les séquences sur lesquelles va s'entraîner le modèle
    format_path = parametres["URL_Dossier"]+os.sep+"Conversion_"+parametres["TypeGeneration"]
    is_stat = parametres["ChoixAffichageStatistiques"] == 1  # l'utilisateur veut afficher les statistiques
    nb_elements = 0
    liste_textes = []
    liste_ensemble = None
    liste_dicos = []  # contiendra les nombres d'occurences de chaques élément de note

    # variables pour les statistiques
    sum_len_seq = 0
    nb_seq = 0
    nb_notes = 0
    nb_fichiers = 0

    for m in os.listdir(format_path):  # on parcourt tous les fichiers présents dans le répertoir des fichiers format
        nb_fichiers += 1

        content = lire_fichier(format_path + os.sep + m)  # contenu du fichier

        if liste_ensemble is None:  # on va créer la liste des ensembles des éléments
            nb_elements = int(content[0])  # la première ligne du fichier donne le nombre d'éléments composant une note
            liste_ensemble = [set() for _ in range(nb_elements)]  # création de la liste des ensembles si elle n'existe pas
            liste_dicos = [{} for _ in range(nb_elements)]

        for a in range(nb_elements):  # pour chaque dictionnaire lu
            new_ensemble = eval(content[a+1])  # transformation de la chaîne en dictionnaire
            liste_ensemble[a] = liste_ensemble[a].union(new_ensemble)  # on rajoute le nouveau dictionnaire à l'ensemble correspondant
            if is_stat:  # si l'utilisateur veut des statistiques
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
        print("-----------------------------------\n")

    return liste_textes, liste_ensemble


def train(parametres, is_model, queue, finQueue, format_infos):
    # fonction appelée pour lancer l'entraînement du modèle
    global rnn_object
    rnn_parametres = get_rnn_parameters(parametres)
    if not is_model:  # s'il n'y a pas de modèle en cours...
        check_conversions(parametres, format_infos)  # on vérifie que toutes les conversions ont bien été faites
        liste_textes, liste_ensembles = get_input_liste(parametres)
        rnn_object = RNN.RNN(liste_textes, rnn_parametres, liste_ensembles)  # ...on crée un modèle avec les bons paramètres
    list_losses, list_acc = rnn_object.train(int(parametres["NombreEpoch"]), int(parametres["NombreSequenceBatch"]), queue, finQueue)  # on entraîne le modèle
    if parametres["ChoixAffichageGraphiques"] == 1:  # si l'utilisateur veut des graphiques sur l'entraînement
        graph_path = parametres["URL_Dossier"]+os.sep+"Graphiques"  # chemin de sauvegarde des graphiques
        saveGraph(graph_path, list_losses, list_acc, parametres)  # sauvegarde
    return


def genereMorceaux(parametres):
    # fonction appelée pour générer des morceaux
    out = rnn_object.generate(int(parametres["NombreMorceaux"]), int(parametres["DureeMorceaux"]))  # on génère les morceaux en fonction des paramètres
    gen_path = parametres["URL_Dossier"] + os.sep + "Resultat"
    base = getDate()+"_"+parametres["TypeGeneration"]  # base des noms de morceaux générés

    for index in range(len(out)):
        save_name = gen_path+os.sep+base+"_"+str(index)+".mid"  # nom complet du morceau
        csv_content = listeMorceaux[0].format_to_csv(out[index])  # utilisation d'un objet morceau pour la conversion de format vers csv
        conversion_en_mid(save_name, csv_content)  # conversion finale en .mid
    return


def getDate():
    # renvoie la date sous un format pratique
    date = datetime.datetime.now()
    dateG = datetime.date(date.year, date.month, date.day)
    dg = dateG.isoformat()
    heureG = datetime.time(date.hour, date.minute, date.second)
    hg = heureG.strftime('%H-%M-%S')
    temp = "_".join([dg, hg])
    return temp


def saveGraph(graph_path, list_losses, list_acc, parametres):
    nb_epoch = len(list_acc)  # nombre d'epoch effectuée
    nb_elements = len(list_losses)  # nombre d'éléments par note
    couleurs = ['b', 'g', 'r', 'k', 'c', 'm', 'y', 'w']  # liste des couleurs possibles sur un graph

    fig_losses, axe_losses = plt.subplots()  # une figure par loss d'élément
    fig_acc, axe_acc = plt.subplots()  # une figure pour l'accuracy

    x = [k for k in range(nb_epoch)]  # abscisse des graphes (numéro d'epoch)
    for a in range(nb_elements):
        label_name = "Loss element n°" + str(a)  # nom de l'élément
        axe_losses.plot(x, list_losses[a], label=label_name, color=couleurs[a % 8])  # un graphe par élément
    # titre du graphe et nommage des axes
    axe_losses.set_title("Loss de chaque element de note par epoch")
    axe_losses.set_xlabel("Nb Epochs")
    axe_losses.set_ylabel("Loss")
    axe_losses.legend()

    axe_acc.plot(x, list_acc, label="Accuracy", color="b")  # création du graphe pour l'accuracy
    # titre du graphe et nommage des axes
    axe_acc.set_title("Accuracy du modèle par epoch")
    axe_acc.set_xlabel("Nb Epochs")
    axe_acc.set_ylabel("Accuracy")
    axe_acc.legend()

    total_epoch = getModelParametres()["TotalEpoch"]  # on récupère le nombre total d'epoch du modèle
    model_type = parametres["TypeGeneration"]
    loss_savename = "_".join([getDate(), str(total_epoch), model_type, "Graph_Loss.png"])  # création des noms de sauvegarde
    acc_savename = "_".join([getDate(), str(total_epoch), model_type, "Graph_Accuracy.png"])

    # enregistrement des graphiques
    fig_losses.savefig(graph_path+os.sep+loss_savename)
    fig_acc.savefig(graph_path+os.sep+acc_savename)

    return
