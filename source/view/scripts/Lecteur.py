# !/usr/bin/python3
# coding: utf-8

import tkinter
import tkinter.font as tkFont
from tkinter import ttk, messagebox
import subprocess
import platform
import pygame
import os

largeurBout = 15
hauteurBout = 2
margeX = 0
margeY = 0


#######################################################
# Classe du lecteur de musique
#######################################################

class Lecteur(tkinter.Frame):
    def __init__(self, master, parametres):
        # Initialisation du Cadre du lecteur MP3
        tkinter.Frame.__init__(self, master)

        self.parametres = parametres

        # URL du répertoire Resultat
        self.URL = self.parametres["URL_Dossier"] + os.sep + "Resultat" + os.sep

        self.userReponse = None  # pour gérer le interactions avec les utilisateurs

        # Réglages de la police du titre puis du texte
        self.titre = tkFont.Font(family='Helvetica', size=20)
        self.texte = tkFont.Font(family='Helvetica', size=13)

        # Couleur de fond
        self.configure(bg='white')

        # variables utiles pour la gestion des musiques
        self.numeroTitre = 0
        self.listeMusiques = []
        self.lecteurState = "Stop"  # peut avoir les états "Pause", "Play", "Stop"

        # Initialisation du lecteur
        initLecteur()
        self.master.protocol('WM_DELETE_WINDOW', lambda: [pygame.mixer.music.stop(), self.master.destroy()])

        # Titre
        tkinter.Label(self, text="Résultat de la génération", font=self.titre, height=hauteurBout, bg='white').grid(row=0, column=0, columnspan=4, sticky="W")
        # Titre de la musique en cours
        self.boxTitreMusique = tkinter.Label(self, text="Titre:", bg='white', font=('Helvetica', 16)).grid(row=2, column=0, sticky="w")

        # Combobox listant tous les titres
        self.titreMusique = ""
        self.comboTitres = ttk.Combobox(self, state="readonly", width=30)
        # Placement
        self.comboTitres.grid(row=2, column=1, columnspan=3)
        self.comboTitres.bind("<<ComboboxSelected>>", lambda e: [master.focus(), self.selectionMusique("<<ComboboxSelected>>")])

        # Bouton Previous Song
        # Affectation d'une image de bouton à une variable
        self.previousSongImage = tkinter.PhotoImage(file="." + os.sep + "source" + os.sep + "view" + os.sep + "button" + os.sep + "sl1.gif")
        # Création du bouton
        self.previousSongButton = tkinter.Button(self)
        # Placement du bouton
        self.previousSongButton.grid(row=4, column=0)
        # Quelques réglages d'apparence : couleur du background, épaisseur des bordures, et affectation de l'image au bouton
        self.previousSongButton.config(image=self.previousSongImage, bd=0, bg='white', command=lambda: [self.previousSong()])
        #self.grid(row=4, column=0)

        # Bouton Play
        # Affectation d'une image de bouton à une variable
        self.playImage = tkinter.PhotoImage(file="." + os.sep + "source" + os.sep + "view" + os.sep + "button" + os.sep + "pl1.gif")
        # Création du bouton
        self.playButton = tkinter.Button(self)
        # Placement du bouton
        self.playButton.grid(row=4, column=1)
        # Quelques réglages d'apparence : couleur du background, épaisseur des bordures, et affectation de l'image au bouton
        self.playButton.config(image=self.playImage, bd=0, bg='white', command=lambda: [self.play()])

        # Bouton Pause
        # Affectation d'une image de bouton à une variable
        self.pauseImage = tkinter.PhotoImage(file="." + os.sep + "source" + os.sep + "view" + os.sep + "button" + os.sep + "pa1.gif")
        # Création du bouton
        self.pauseButton = tkinter.Button(self)
        # Placement du bouton
        self.pauseButton.grid(row=4, column=2)
        # Quelques réglages d'apparence : couleur du background, épaisseur des bordures, et affectation de l'image au bouton
        self.pauseButton.config(image=self.pauseImage, bd=0, bg='white', command=lambda: [self.pause()])

        # Bouton Next Song
        # Affectation d'une image de bouton à une variable
        self.nextSongImage = tkinter.PhotoImage(file="." + os.sep + "source" + os.sep + "view" + os.sep + "button" + os.sep + "sr1.gif")
        # Création du bouton
        self.nextSongButton = tkinter.Button(self)
        # Placement du bouton
        self.nextSongButton.grid(row=4, column=3)
        # Quelques réglages d'apparence : couleur du background, épaisseur des bordures, et affectation de l'image au bouton
        self.nextSongButton.config(image=self.nextSongImage, bd=0, bg='white', command=lambda: [self.nextSong()])

        # Un espace
        tkinter.Label(self, text=" ", bg="white").grid(row=6)
        tkinter.Label(self, text=" ", bg="white").grid(row=3)

        # Bouton Retour
        # Creation du bouton retour, relié à la classe menu
        self.retourMenu = tkinter.Button(self, text="Retour", font=self.texte, command=lambda: [self.stop(), master.switch_frame("Menu")])
        # Placement
        self.retourMenu.grid(row=7, column=0, sticky="WS")
        # Réglage de la bordure du bouton et du background
        self.retourMenu.config(bd=1, bg="white")

        # Bouton acceder directement au dossier
        # Création du bouton
        self.deleteButton = tkinter.Button(self, text="Accéder au dossier", font=self.texte, command=lambda: [self.opendir()])
        # Placement
        self.deleteButton.grid(row=7, column=2, columnspan=2, sticky="E")
        # Réglage du background
        self.deleteButton.config(bg='white', bd=1)

        # Bouton Supprimer les fichiers
        # Création du bouton
        self.deleteButton = tkinter.Button(self, text="Supprimer les fichiers", font=self.texte, command=lambda: [self.supprimerFichiers()])
        # Placement
        self.deleteButton.grid(row=8, column=2, columnspan=2, sticky="E")
        # Réglage du background
        self.deleteButton.config(bg='white', bd=1)

        # mise à jour du répértoire des musiques
        self.miseAJourRepertoire(self.parametres)

    def supprimerFichiers(self):
        if tkinter.messagebox.askyesno("Attention", "Voulez vraiment supprimer les fichiers ?"):
            for filename in os.listdir(self.URL):
                os.remove(self.URL + filename)
            self.miseAJourRepertoire(self.parametres)

    def miseAJourRepertoire(self, parametres):
        # parcours les fichiers du repertoire
        self.parametres = parametres
        self.URL = self.parametres["URL_Dossier"] + os.sep + "Resultat" + os.sep

        self.listeMusiques = os.listdir(self.URL)

        self.comboTitres["values"] = self.listeMusiques  # HERE
        self.comboTitres.set("")
        pygame.mixer.music.pause()

        self.listeMusiques = [i for i in self.listeMusiques if ".mid" in i]  # Filtre les fichiers pour n'avoir que du .mid
        if len(self.listeMusiques) > 0:
            try:
                pygame.mixer.music.load(self.URL + str(self.listeMusiques[0]))  # Charge le premier titre
            except pygame.error:
                print("Erreur : fichier midi non valide")
            self.comboTitres.current(0)

    def play(self):
        if len(self.listeMusiques) == 0:
            return

        if pygame.mixer.music.get_busy() == 0:  # le lecteur ne joue rien
            if self.lecteurState == "Pause":
                pygame.mixer.music.unpause()

            if self.lecteurState == "Stop" or self.lecteurState == "Play":
                pygame.mixer.music.play()

        self.lecteurState = "Play"
        return

    def pause(self):
        if len(self.listeMusiques) == 0:
            return

        if self.lecteurState == "Play":
            pygame.mixer.music.pause()
            self.lecteurState = "Pause"
        return

    def stop(self):
        self.lecteurState = "Stop"
        pygame.mixer.music.stop()
        return

    def nextSong(self):
        if len(self.listeMusiques) == 0:
            return
        if self.lecteurState == "Play":  # si un morceau est joué
            pygame.mixer.music.stop()  # on l'arrête

        self.numeroTitre = (self.numeroTitre + 1) % len(self.listeMusiques)  # indice du prochain son à jouer

        pygame.mixer.music.load(self.URL + str(self.listeMusiques[self.numeroTitre]))
        pygame.mixer.music.play()
        self.lecteurState = "Play"
        self.comboTitres.current(self.numeroTitre)

    def previousSong(self):
        if len(self.listeMusiques) == 0:
            return
        if self.lecteurState == "Play":  # si un morceau est joué
            pygame.mixer.music.stop()  # on l'arrête

        self.numeroTitre = (self.numeroTitre - 1) % len(self.listeMusiques)  # indice du prochain son à jouer

        pygame.mixer.music.load(self.URL + str(self.listeMusiques[self.numeroTitre]))
        pygame.mixer.music.play()
        self.lecteurState = "Play"
        self.comboTitres.current(self.numeroTitre)

    def selectionMusique(self, event):
        if self.lecteurState == "Play":  # S si un morceau est joué
            pygame.mixer.music.stop()  # on l'arrête
        pygame.mixer.music.load(self.URL + self.comboTitres.get())  # Charge le titre
        pygame.mixer.music.play()  # on joue le morceau
        self.lecteurState = "Play"
        self.numeroTitre = self.comboTitres.current()  # On met à jour le numero de titre joué

    def opendir(self):
        print(self.URL)
        dir = os.path.dirname(self.URL)
        osName = platform.system()
        if osName == "Windows":
            os.system('explorer ' + dir)
        elif osName == "Darwin":
            subprocess.Popen(["open", dir])
        else:
            subprocess.Popen(["xdg-open", dir])

def initLecteur():
    # initialisation du lecteur
    pygame.init()
    pygame.mixer.init()
