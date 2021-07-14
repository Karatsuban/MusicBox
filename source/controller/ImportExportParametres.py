# !/usr/bin/python3
# coding: utf-8

import csv
import os


def exportInCSV(parametres):
    # exporte les paramètres en .csv
    with open("data" + os.sep + "parametres.csv", 'w') as fichier:
        w = csv.DictWriter(fichier, parametres.keys())
        w.writeheader()
        w.writerow(parametres)
    return


def importFromCSV():
    # lit les paramètres depuis un fichier .csv
    with open("data" + os.sep + "parametres.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            parametres = dict(row)
    return parametres


def importFormat():
    # renvoie tous les formats présents dans le fichier de sauvegarde des formats
    if "formats.csv" not in os.listdir("."):
        return None
    dico_formats = {}  # dictionnaire de dictionnaires
    with open("formats.csv") as formatFile:
        reader = csv.DictReader(formatFile)
        for row in reader:  # pour chaque ligne
            infos = dict(row)  # on récupère les informations d'un format sous forme de dictionnaire
            nom_format = infos["NomFormat"]  # récupération du nom de format
            infos["ListeTypesElements"] = eval(infos["ListeTypesElements"])
            dico_formats[nom_format] = infos  # on stocke le dictionnaire à l'index correspondant à son nom
    return dico_formats


def addFormat(format_infos):
    # ajout un format au fichier de sauvegarde des formats
    createFormatFile()
    with open("formats.csv", "r") as formatFile:
        is_header = formatFile.readlines() != []  # on s'assure que le header est déjà écrit
        print(formatFile.readlines())
    with open("formats.csv", "a") as formatFile:
        w = csv.DictWriter(formatFile, format_infos.keys())
        if not is_header:
            w.writeheader()
        w.writerow(format_infos)
    return


def createFormatFile():
    # crée le fichier de sauvegarde des formats s'il n'existe pas
    if "formats.csv" not in os.listdir("."):
        with open("formats.csv", "x"):
            pass
    return
