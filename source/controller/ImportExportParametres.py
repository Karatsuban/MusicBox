# !/usr/bin/python3
#coding: utf-8

import csv
import os

def export(parametres):
	fichier = open("data"+os.sep+"parametres.txt", 'w')
	
	fichier.write(str(parametres))
	
	fichier.close()
	print("Fichier de paramètres exporté")
	return
	
	
def exportInCSV(parametres):
	with open("data"+os.sep+"parametres.csv", 'w') as fichier :
		w = csv.DictWriter(fichier, parametres.keys())
		w.writeheader()
		w.writerow(parametres)
	return
	
def importFromCSV():
	with open("data"+os.sep+"parametres.csv", newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		parametres = {}
		for row in reader:
			parametres['URL_Dossier'] = row['URL_Dossier']
			parametres['NombreMorceaux'] = row['NombreMorceaux']
			parametres['DureeMorceaux']= row['DureeMorceaux']
			parametres['TonaliteMorceaux']= row['TonaliteMorceaux']
			parametres['VitesseMorceaux']= row['VitesseMorceaux']
			parametres['TypeGeneration'] = row['TypeGeneration']
			parametres['TauxApprentissage'] = row['TauxApprentissage']
			parametres['NombreEpoch'] = row['NombreEpoch']
			parametres['NombreDimensionCachee'] = row['NombreDimensionCachee']
			parametres['NombreLayer'] = row['NombreLayer']
			parametres['LongeurSequence'] = row['LongeurSequence']
			parametres['BatchBool'] = row['BatchBool']
			parametres['NombreSequenceBatch'] = row['NombreSequenceBatch']
	return parametres
	
def getURL():
	with open("data"+os.sep+"parametres.csv", newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		parametres = {}
		for row in reader:
			return row['URL_Dossier']
