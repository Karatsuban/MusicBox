# !/usr/bin/python3
# coding: utf-8

import csv
import os


def export(parametres):
    fichier = open("data" + os.sep + "parametres.txt", 'w')

    fichier.write(str(parametres))

    fichier.close()
    print("Fichier de paramètres exporté")
    return


def exportInCSV(parametres):
    with open("data" + os.sep + "parametres.csv", 'w') as fichier:
        w = csv.DictWriter(fichier, parametres.keys())
        w.writeheader()
        w.writerow(parametres)
    return


def importFromCSV():
    with open("data" + os.sep + "parametres.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            parametres = dict(row)
    return parametres


def getURL():
    with open("data" + os.sep + "parametres.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            return row['URL_Dossier']
