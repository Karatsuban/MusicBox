# !/usr/bin/python3
#coding: utf-8

import tkinter
import tkinter.font as tkFont
from tkinter import ttk
import pygame
from PIL import Image,ImageTk
from source.view.scripts import Menu

import os
from source.controller import ImportExportParametres as iep

hauteurBout = 10
largeurBout = 15
hauteurBout = 2
margeX = 0
margeY = 0


#######################################################
# Classe du lecteur de musique
#######################################################

class Lecteur(tkinter.Frame):
    def __init__(self, master, parametres):
        #Initialisation du Cadre du lecteur MP3
        tkinter.Frame.__init__(self, master)

        self.parametres = parametres

        #URL du répertoire Resultat
        self.URL = self.parametres["URL_Dossier"]+os.sep+"Resultat"+os.sep
        
        #Réglages de la police du titre puis du texte
        self.titre = tkFont.Font(family='Helvetica', size=20)
        self.texte = tkFont.Font(family='Helvetica', size=13)
        
        #Couleur de fond
        self.configure(bg='white')
        
        #Quelques variables utiles pour la gestion des musiques
        self.numeroTitre = 0
        self.listeMusiques = []
        #Titre
        tkinter.Label(self, text="Résultat de la génération", font = self.titre, height = hauteurBout, bg='white').grid(row = 0, column = 0, sticky="W") 
        #Titre de la musique en cours
        self.titreMusique = ""
        self.boxTitreMusique = tkinter.Label(self, text="Titre: ", bg='white', font = self.texte).grid(row=1,column=0, sticky="w")
        
        #tkinter.Label(self, text="",height = hauteurBout,bg='white').grid(row = 2, column = 0) 
        
        #Bouton Skip Left
        #Affectation d'une image de bouton à une variable
        self.skip_left = tkinter.PhotoImage(file="."+os.sep+"source"+os.sep+"view"+os.sep+"button"+os.sep+"sl1.png")
        
        #Création du bouton
        self.skip_left_button = tkinter.Button(self)
        #Placement du bouton
        self.skip_left_button.grid(row = 3, column = 0, sticky="W")
        #Quelques réglages d'apparence : couleur du background, épaisseur des bordures, et affectation de l'image au bouton
        self.skip_left_button.config(image = self.skip_left, bd=0,bg='white', command= lambda:[self.previousSong()])
        self.grid(row=3, column=0, pady=(100, 10))
        
        #Bouton Play
        #Ajout d'un compteur au bouton play
        self.comptePlay = 0
        #Affectation d'une image de bouton à une variable
        self.play = tkinter.PhotoImage(file="."+os.sep+"source"+os.sep+"view"+os.sep+"button"+os.sep+"pl1.png")    
        
        #Création du bouton
        self.play_button = tkinter.Button(self)
        #Placement du bouton
        self.play_button.grid(row = 3, column = 0)
        #Quelques réglages d'apparence : couleur du background, épaisseur des bordures, et affectation de l'image au bouton
        self.play_button.config(image = self.play, bd=0,bg='white', command= lambda: [self.playUnPause()])
        
        
        #Bouton Pause
        #Affectation d'une image de bouton à une variable
        self.pause = tkinter.PhotoImage(file="."+os.sep+"source"+os.sep+"view"+os.sep+"button"+os.sep+"pa1.png")

        

        #Création du bouton
        self.pause_button = tkinter.Button(self)
        #Placement du bouton
        self.pause_button.grid(row = 3, column =0, sticky="e")
        #Quelques réglages d'apparence : couleur du background, épaisseur des bordures, et affectation de l'image au bouton
        self.pause_button.config(image = self.pause, bd=0, bg='white', command = lambda: [pygame.mixer.music.pause()])
        
        #Bouton Skip Right
        #Affectation d'une image de bouton à une variable
        self.skip_right = tkinter.PhotoImage(file="."+os.sep+"source"+os.sep+"view"+os.sep+"button"+os.sep+"sr1.png")
        
        #Création du bouton
        self.skip_right_button = tkinter.Button(self)
        #Placement du bouton
        self.skip_right_button.grid(row = 3, column = 2)
        #Quelques réglages d'apparence : couleur du background, épaisseur des bordures, et affectation de l'image au bouton
        self.skip_right_button.config(image = self.skip_right, bd=0,bg='white', command = lambda:[self.nextSong()])
        
        #Un espace 
        tkinter.Label(self,text=" ",bg="white").grid(row=6)
        tkinter.Label(self,text=" ",bg="white").grid(row=2)
        
        #Bouton Supprimer les fichiers
        #Création du bouton
        self.download_button = tkinter.Button(self, text="Supprimer les fichiers", font = self.texte,  command = lambda:[self.supprimerFichiers()])
        #Placement
        self.download_button.grid(row = 7, column =2, sticky="W")
        #Réglage du background
        self.download_button.config(bg='white', bd=1)
            
        #Bouton Retour
        #Creation du bouton retour, relié à la classe menu 
        self.retour = tkinter.Button(self, text="Retour", font = self.texte, command=lambda : [pygame.mixer.music.pause(),master.switch_frame()])
        #Placement
        self.retour.grid(row=7,column=0, sticky="WS")
        #Réglage de la bordure du bouton et du background
        self.retour.config(bd=1, bg="white")
        
        #Combobox listant tous les titres
        self.comboTitres = ttk.Combobox(self,state="readonly", width=30)
        #Placement
        self.comboTitres.grid(row=1, column=0, columnspan=3)
        self.comboTitres.bind("<<ComboboxSelected>>", lambda e:[master.focus(),self.selectionMusique("<<ComboboxSelected>>")])

        # mise à jour du répértoire des musiques        
        self.miseAJourRepertoire(self.parametres)
        
        #Initialisation des musiques lecteur 
        self.initLecteur()
        self.master.protocol('WM_DELETE_WINDOW', lambda : [pygame.mixer.music.stop(), self.master.destroy()])
        
    def supprimerFichiers(self):
        for filename in os.listdir(self.URL) :
            os.remove(self.URL + filename)
    
    
    def initLecteur(self):
        #initiliastion du lecteur
        pygame.init()
        pygame.mixer.init()
        

    def miseAJourRepertoire(self, parametres):
        #parcours les fichiers du repertoire
        self.parametres = parametres
        self.URL = self.parametres["URL_Dossier"]+os.sep+"Resultat"+os.sep
        print("Lecteur.initLecteur, self.URL = ",self.URL)


        self.listeMusiques = os.listdir(self.URL)
        print("Lecteur.initLecteur, self.listeMusiques = ", self.listeMusiques)


        self.listeMusiques = [i for i in self.listeMusiques if ".mid" in i] #Filtre les fichiers pour n'avoir que du .mid
        if len(self.listeMusiques) > 0:
                        try:
                            pygame.mixer.music.load(self.URL+str(self.listeMusiques[0]))    #Charge le premier titre
                        except pygame.error:
                            print("Echec de chargement du fichier midi\n")
                        self.comboTitres["values"]=self.listeMusiques
                        self.comboTitres.current(0)
    
    
    def playUnPause(self):
        if(self.comptePlay ==0):
            pygame.mixer.music.play()
            self.comptePlay = 1
        else:
            pygame.mixer.music.unpause()
        return 
    
    def nextSong(self):
        if self.comptePlay == 1: #Si c'est 1 c'est qu'un son est joué
            pygame.mixer.music.stop() # stop current song
        if self.numeroTitre+1 == len(self.listeMusiques): # if it's the last song
            self.numeroTitre = 0 # set the var to represent the first song
        else:
            self.numeroTitre += 1 # else, next song
        pygame.mixer.music.load(self.URL+str(self.listeMusiques[self.numeroTitre]))
        pygame.mixer.music.play() # play the song var corresponds to
        #self.titreMusique.set("Titre: "+self.listeMusiques[self.numeroTitre])
        self.comboTitres.current(self.numeroTitre)

    def previousSong(self):
        if self.comptePlay == 1: #Si c'est 1 c'est qu'un son est joué
            pygame.mixer.music.stop() # stop current song
        if self.numeroTitre == 0: # if it's the first song
            self.numeroTitre = len(self.listeMusiques)-1 # set the var to represent the last song
        else:
            self.numeroTitre -= 1 # else, previous song
        pygame.mixer.music.load(self.URL+str(self.listeMusiques[self.numeroTitre]))
        pygame.mixer.music.play() # play the song var corresponds to
        #self.titreMusique.set("Titre: "+self.listeMusiques[self.numeroTitre])
        self.comboTitres.current(self.numeroTitre)

    def selectionMusique(self, event):
        if self.comptePlay == 1: #Si c'est 1 c'est qu'un son est joué
            pygame.mixer.music.stop() # stop current song
        pygame.mixer.music.load(self.URL+self.comboTitres.get()) #Charge le titre 
        pygame.mixer.music.play() # play the song var corresponds to
        self.numeroTitre = self.comboTitres.current() #On met à jour le numero de titre joué

