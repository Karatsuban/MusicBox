# !/usr/bin/python3
# coding: utf-8

import tkinter
import tkinter.font as tkfont
from tkinter import ttk, messagebox
import subprocess
import platform
import pygame
import os


class Lecteur(tkinter.Frame):
    def __init__(self, master, parametres):
        # Initialisation du Cadre du lecteur
        tkinter.Frame.__init__(self, master)

        self.parametres = parametres

        # URL du répertoire Resultat
        self.URL = self.parametres["URL_Dossier"] + os.sep + "Resultat" + os.sep

        self.userReponse = None  # variables pour gérer les interactions avec les utilisateurs

        # Réglages de la police du texte
        self.texte = tkfont.Font(family='Helvetica', size=13)

        # Couleur de fond
        self.configure(bg='white')

        # variables utiles pour la gestion des musiques
        self.numeroTitre = 0
        self.listeMusiques = []
        self.lecteurState = "Stop"  # peut avoir les états "Pause", "Play", "Stop"

        # Initialisation du lecteur
        initLecteur()

        # Combobox listant tous les titres
        self.titreMusique = ""
        self.comboTitres = ttk.Combobox(self, font=self.texte, state="readonly", width=30)
        # Placement
        self.comboTitres.grid(row=0, column=0, columnspan=4)
        self.comboTitres.bind("<<ComboboxSelected>>", lambda e: [master.focus(), self.selectionMusique("<<ComboboxSelected>>")])

        image_folder = "." + os.sep + "source" + os.sep + "view" + os.sep + "button" + os.sep

        # Bouton Previous Song
        self.previousSongImage = tkinter.PhotoImage(file=image_folder + "previous.gif")  # Affectation d'une image de bouton à une variable
        self.previousSongButton = tkinter.Button(self)  # Création
        self.previousSongButton.grid(row=2, column=0)  # Placement
        # réglages d'apparence : couleur du background, épaisseur des bordures, et affectation de l'image au bouton
        self.previousSongButton.config(image=self.previousSongImage, bd=0, bg='white', command=lambda: [self.previousSong()])

        # Bouton Play
        self.playImage = tkinter.PhotoImage(file=image_folder + "play.gif")  # Affectation d'une image de bouton à une variable
        self.playButton = tkinter.Button(self)  # Création
        self.playButton.grid(row=2, column=1)   # Placement
        # réglages d'apparence : couleur du background, épaisseur des bordures et affectation de l'image au bouton
        self.playButton.config(image=self.playImage, bd=0, bg='white', command=lambda: [self.play()])

        # Bouton Pause
        self.pauseImage = tkinter.PhotoImage(file=image_folder + "pause.gif")  # Affectation d'une image de bouton à une variable
        self.pauseButton = tkinter.Button(self)  # Création
        self.pauseButton.grid(row=2, column=2)  # Placement
        # réglages d'apparence : couleur du background, épaisseur des bordures, et affectation de l'image au bouton
        self.pauseButton.config(image=self.pauseImage, bd=0, bg='white', command=lambda: [self.pause()])

        # Bouton Next Song
        self.nextSongImage = tkinter.PhotoImage(file=image_folder + "next.gif")  # Affectation d'une image de bouton à une variable
        self.nextSongButton = tkinter.Button(self)  # Création
        self.nextSongButton.grid(row=2, column=3)  # Placement
        # réglages d'apparence : couleur du background, épaisseur des bordures, et affectation de l'image au bouton
        self.nextSongButton.config(image=self.nextSongImage, bd=0, bg='white', command=lambda: [self.nextSong()])

        # espaces pour améliorer la visibilité
        tkinter.Label(self, text=" ", bg="white").grid(row=1)
        tkinter.Label(self, text=" ", bg="white").grid(row=3)

        # Bouton Retour
        # Creation du bouton retour, relié à la classe menu
        self.retourMenu = tkinter.Button(self, text="Retour", font=self.texte, command=lambda: [self.stop(), master.switch_frame("Menu")])
        self.retourMenu.grid(row=5, column=0, columnspan=4, sticky="W")  # Placement
        self.retourMenu.config(bd=1, bg="white")  # Réglage de la bordure du bouton et du background

        # Bouton ouvrir l'emplacement des fichiers
        self.deleteButton = tkinter.Button(self, text="Accéder au dossier", font=self.texte, command=lambda: [self.opendir()])  # Création du bouton
        self.deleteButton.grid(row=5, column=1, columnspan=4, sticky="E")  # Placement
        self.deleteButton.config(bg='white', bd=1)  # Réglage du background

        # Bouton Supprimer les fichiers
        self.deleteButton = tkinter.Button(self, text="Supprimer les fichiers", font=self.texte, command=lambda: [self.supprimerFichiers()])  # Création du bouton
        self.deleteButton.grid(row=6, column=1, columnspan=4, sticky="E")  # Placement
        self.deleteButton.config(bg='white', bd=1)  # Réglage du background

        # mise à jour du répértoire des musiques
        self.miseAJourRepertoire(self.parametres)

    def supprimerFichiers(self):
        # demande à l'utilisateur une confirmation de suppression et supprime les fichiers si nécessaire
        if tkinter.messagebox.askyesno("Attention", "Voulez vraiment supprimer les fichiers ?"):
            for filename in os.listdir(self.URL):
                os.remove(self.URL + filename)
            self.miseAJourRepertoire(self.parametres)
        return

    def miseAJourRepertoire(self, parametres):
        # parcours les fichiers du repertoire
        self.parametres = parametres
        self.URL = self.parametres["URL_Dossier"] + os.sep + "Resultat" + os.sep

        self.listeMusiques = os.listdir(self.URL)

        self.comboTitres["values"] = self.listeMusiques
        self.comboTitres.set("")
        pygame.mixer.music.pause()

        self.listeMusiques = [i for i in self.listeMusiques if ".mid" in i]  # Filtre les fichiers pour n'avoir que du .mid
        if len(self.listeMusiques) > 0:
            try:
                pygame.mixer.music.load(self.URL + str(self.listeMusiques[0]))  # Charge le premier titre
            except pygame.error:
                print("Erreur : fichier midi non valide")
            self.comboTitres.current(0)
        return

    def play(self):
        # joue le morceau séléectionné
        if len(self.listeMusiques) == 0:  # rien à faire s'il n'y a pas de fichier dans la liste
            return

        if pygame.mixer.music.get_busy() == 0:  # le lecteur ne joue rien
            if self.lecteurState == "Pause":
                pygame.mixer.music.unpause()

            if self.lecteurState == "Stop" or self.lecteurState == "Play":
                pygame.mixer.music.play()

        self.lecteurState = "Play"
        return

    def pause(self):
        # met en pause le morceau joué
        if len(self.listeMusiques) == 0:  # rien à faire s'il n'y a pas de fichier dans la liste
            return

        if self.lecteurState == "Play":  # si un son est en cours
            pygame.mixer.music.pause()  # on pause le lecteur
            self.lecteurState = "Pause"
        return

    def stop(self):
        # arrêt complet de la lecture
        self.lecteurState = "Stop"
        pygame.mixer.music.stop()
        return

    def nextSong(self):
        # joue le morceau suivant dans la liste
        if len(self.listeMusiques) == 0:  # rien à faire s'il n'y a pas de fichier dans la liste
            return
        if self.lecteurState == "Play":  # si un morceau est joué
            pygame.mixer.music.stop()  # on l'arrête

        self.numeroTitre = (self.numeroTitre + 1) % len(self.listeMusiques)  # indice du prochain son à jouer

        pygame.mixer.music.load(self.URL + str(self.listeMusiques[self.numeroTitre]))  # chargement du fichier
        pygame.mixer.music.play()  # lecture
        self.lecteurState = "Play"
        self.comboTitres.current(self.numeroTitre)  # affichage du nouveau titre
        return

    def previousSong(self):
        # joue le morceau précédent dans la liste
        if len(self.listeMusiques) == 0:  # rien à faire s'il n'y a pas de fichier dans la liste
            return
        if self.lecteurState == "Play":  # si un morceau est joué
            pygame.mixer.music.stop()  # on l'arrête

        self.numeroTitre = (self.numeroTitre - 1) % len(self.listeMusiques)  # indice du prochain son à jouer

        pygame.mixer.music.load(self.URL + str(self.listeMusiques[self.numeroTitre]))  # chargement du fichier
        pygame.mixer.music.play()  # lecture
        self.lecteurState = "Play"
        self.comboTitres.current(self.numeroTitre)  # affichage du nouveau titre
        return

    def selectionMusique(self, event):
        # joue le morceau sélectionné dans la liste
        if self.lecteurState == "Play":  # si un morceau est joué
            pygame.mixer.music.stop()  # arrêt

        pygame.mixer.music.load(self.URL + self.comboTitres.get())  # chargement du titre
        pygame.mixer.music.play()  # lecture
        self.lecteurState = "Play"
        self.numeroTitre = self.comboTitres.current()  # mise à jour le numero de titre joué
        return

    def opendir(self):
        # ouverture de l'emplacement des fichiers en fonction de la plateforme
        dir_name = os.path.dirname(self.URL)
        osName = platform.system()
        if osName == "Windows":
            os.system('explorer ' + dir_name)
        elif osName == "Darwin":
            subprocess.Popen(["open", dir_name])
        else:
            subprocess.Popen(["xdg-open", dir_name])
        return


def initLecteur():
    # initialisation du lecteur
    pygame.init()
    pygame.mixer.init()
    return
