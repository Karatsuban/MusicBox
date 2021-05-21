# coding:utf-8

import tkinter
import tkinter.filedialog
import tkinter.font as tkFont
from tkinter import ttk, messagebox
from source.controller import TraitementFichiers, ImportExportParametres
import os


hauteurBout = 2

#######################################################
# Classe du menu de l'interface
#######################################################

class Menu(tkinter.Frame):

    def __init__(self, master, parametres):
        tkinter.Frame.__init__(self, master)

        # Réglage police du titre et du texte
        self.policeTitre = tkFont.Font(family='Helvetica', size=20)
        self.PoliceTexte = tkFont.Font(family='Helvetica', size=13)
        # Réglage police combobox
        master.option_add("*Font", "Helvetica 13")
        # Réglage arrière plan
        self.configure(bg='white')

        self.parametres = parametres

        # --------- Configuration ------------ #
        # Création et placement du titre du cadre
        self.configurationLabel = tkinter.Label(self, text="Configuration", bg='white', font=self.policeTitre).grid(row=0, column=0)

        # Barre de Menu
        self.menuBarre = tkinter.Menu(self.master)

        self.menuPropos = tkinter.Menu(self.menuBarre, tearoff=0)
        self.menuPropos.add_command(label="À propos", command=self.about)
        self.menuPropos.add_command(label="Crédits", command=self.credits)

        self.menuBarre.add_cascade(label="À propos", menu=self.menuPropos)  # Menu déroulant

        self.master.config(menu=self.menuBarre)

        # Création et placement du Bouton ouvrir dossier
        self.openFolderButton = tkinter.Button(self, text="Sélection Dossier", bg="white", font=self.PoliceTexte, bd=1, command=lambda: [self.Browser()])
        self.openFolderButton.grid(row=1, column=0, sticky="W")

        # Création de la variable contenant le chemin
        self.urlVar = tkinter.StringVar()
        self.urlVar.set(self.parametres["URL_Dossier"])
        # Placement de la zone et affectation d'un texte dans cette zone d'affichage
        self.urlEntry = tkinter.Entry(self, state='readonly', text=self.urlVar, width=25)
        self.urlEntry .grid(row=1, column=1, sticky="EW")

        # Création et placement du label Nombre de morceaux
        self.nbMorceauxLabel = tkinter.Label(self, text="Nombre de morceaux", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=2, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le nombre de morceaux
        self.nbMorceaux = tkinter.Spinbox(self, from_=1, to=20, width=10)
        self.nbMorceaux.grid(row=2, column=1, sticky="W")
        self.nbMorceauxLimit = tkinter.Label(self, text="(1-20)", bg="white").grid(row=2, column=1, sticky="e")

        # Création et placement du label Durée max des morceaux
        tkinter.Label(self, text="Durée max morceaux", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=3, column=0, sticky="W")
        # Création du spinbox de durée  max du morceau
        self.dureeMaxMorceau = tkinter.Spinbox(self, from_=60, to=340, width=10)
        # Placement de la spinbox
        self.dureeMaxMorceau.grid(row=3, column=1, sticky="W")
        # Placement de l'affichage des limites de la durée
        tkinter.Label(self, text="(5-340)", bg="white").grid(row=3, column=1, sticky="e")

        # Tonalité de morceaux
        tkinter.Label(self, text="Tonalité de morceaux", height=hauteurBout,  font=self.PoliceTexte, bg='white').grid(row=4, column=0, sticky="W")
        # Bouton Tonalite du morceau
        self.tonaliteMorceau = tkinter.Spinbox(self, values=("A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"), width=10)
        self.tonaliteMorceau.grid(row=4, column=1, sticky="W")

        # Vitesse des morceaux
        tkinter.Label(self, text="Vitesse des morceaux", height=hauteurBout,  font=self.PoliceTexte, bg='white').grid(row=5, column=0, sticky="W")
        # Bouton vitesse des morceau
        self.bpmMorceau = tkinter.Spinbox(self, from_=30, to=240, width=10)
        self.bpmMorceau.grid(row=5, column=1, sticky="W")
        self.bpmMorceauLimit = tkinter.Label(self, text="(30-240)", bg="white").grid(row=5, column=1, sticky="e")

        # Choix de génération
        tkinter.Label(self, text="Type de génération", width=15, height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=6, column=0, sticky="W")
        # Création de la combobox de Choix de generation
        self.typeGenComboboite = tkinter.ttk.Combobox(self, values=["Rythme seulement", "Rythme et mélodie"], state="readonly")
        # Réglage de l'item actuel sur 1
        self.typeGenComboboite.current(1)
        # Placement
        self.typeGenComboboite.grid(row=6, column=1, sticky="W")

        # --------- Choix avancés ------------ #
        # Création et placement du titre choix avancés
        tkinter.Label(self, text="Choix avancés", bg='white', font=self.policeTitre).grid(row=7, column=0, sticky="W")
        tkinter.Label(self, text="Non recommandé", bg='white', font=self.PoliceTexte).grid(row=8, column=0, sticky="W")
        # Bouton pour (dés)activer les choix avancés
        self.paramsAvancesValue = 0  # désactivé
        self.paramsAvancesBouton = tkinter.Button(self, text="Activer les paramètres avancés", width=30, bg="white", command=lambda: [self.changeInterface()])
        self.paramsAvancesBouton.grid(row=8, column=1, sticky="W")

        # Création et placement du label Taux apprentissage
        varTxApp = tkinter.StringVar(self)
        varTxApp.set(self.parametres["TauxApprentissage"])
        tkinter.Label(self, text="Taux apprentissage", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=9, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le taux d'apprentissage
        self.txApprentissage = tkinter.Spinbox(self, from_=0, to=1, width=10, format='%4.3f', increment=0.001, textvariable=varTxApp, state=tkinter.DISABLED)
        self.txApprentissage.grid(row=9, column=1, sticky="W")
        tkinter.Label(self, text="(0-1)", bg="white").grid(row=9, column=1, sticky="e")

        # Création et placement du label Nombre d'epoch
        varEpoch = tkinter.StringVar(self)
        varEpoch.set(self.parametres["NombreEpoch"])
        tkinter.Label(self, text="Nombre d'Epoch", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=10, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le nombre d'epoch
        self.nbEpoch = tkinter.Spinbox(self, from_=1, to=7000, width=10, textvariable=varEpoch, state=tkinter.DISABLED)
        self.nbEpoch.grid(row=10, column=1, sticky="W")
        tkinter.Label(self, text="(1-7000)", bg="white").grid(row=10, column=1, sticky="e")

        # Création et placement du label Nombre de dimension cachée
        varDimCach = tkinter.StringVar(self)
        varDimCach.set(self.parametres["NombreDimensionCachee"])
        tkinter.Label(self, text="Dimension cachée", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=11, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le nombre de dimension cachée
        self.nbDimCachee = tkinter.Spinbox(self, from_=16, to=2048, width=10, textvariable=varDimCach, state=tkinter.DISABLED)
        self.nbDimCachee.grid(row=11, column=1, sticky="W")
        tkinter.Label(self, text="(2"+chr(0x2074)+"-2"+chr(0x00B9)+chr(0x00B9)+")", bg="white").grid(row=11, column=1, sticky="e")

        # Création et placement du label Nombre de layer
        varNbLayer = tkinter.StringVar(self)
        varNbLayer.set(self.parametres["NombreLayer"])
        tkinter.Label(self, text="Nombre de layer", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=12, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le nombre de layer
        self.nbLayer = tkinter.Spinbox(self, from_=1, to=5, width=10, textvariable=varNbLayer, state=tkinter.DISABLED)
        self.nbLayer.grid(row=12, column=1, sticky="W")
        tkinter.Label(self, text="(1-5)", bg="white").grid(row=12, column=1, sticky="e")

        # Création et placement du label Nombre de sequence par batch
        varSeqBa = tkinter.StringVar(self)
        varSeqBa.set(self.parametres["NombreSequenceBatch"])
        tkinter.Label(self, text="Séquences par batch", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=15, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le nombre de seq du batch
        self.nbSeqBatch = tkinter.Spinbox(self, from_=1, to=512, width=10, textvariable=varSeqBa, state=tkinter.DISABLED)
        self.nbSeqBatch.grid(row=15, column=1, sticky="W")
        tkinter.Label(self, text="(2"+chr(0x2070)+"-2"+chr(0x2079)+")", bg="white").grid(row=15, column=1, sticky="e")

        # Création et placement du Bouton Lecteur
        self.textBoutonLecteur = tkinter.StringVar()
        self.textBoutonLecteur.set("Accès direct au lecteur")
        self.Lecteur = tkinter.Button(self, textvariable=self.textBoutonLecteur, bg="white", font=self.PoliceTexte, bd=1, command=lambda: [self.saveParametres(), master.switch_frame()])
        self.Lecteur.grid(row=16, column=0, sticky="EW")

        # Création et placement du Bouton valider
        self.textBoutonValider = tkinter.StringVar()
        self.textBoutonValider.set("Valider")
        self.Valider = tkinter.Button(self, textvariable=self.textBoutonValider, width=20, bg="white", font=self.PoliceTexte, bd=1, command=lambda: [self.charging(master)])
        self.Valider.grid(row=16, column=1, sticky="E")

        # bouton pour sauvegarder les paramètres
        self.saveParamsButton = tkinter.Button(self, text="Sauvegarder paramètres", bg="white", command=lambda: [self.exportParametres()])
        self.saveParamsButton.grid(row=17, column=0, sticky="W")

    def exportParametres(self):
        self.saveParametres()
        ImportExportParametres.exportInCSV(self.parametres)

    def saveParametres(self):
        self.parametres = {"URL_Dossier": self.urlVar.get(),
                            "NombreMorceaux": self.nbMorceaux.get(),
                            "DureeMorceaux": self.dureeMaxMorceau.get(),
                            "TonaliteMorceaux": self.tonaliteMorceau.get(),
                            "VitesseMorceaux": self.bpmMorceau.get(),
                            "TypeGeneration": self.typeGenComboboite.get(),
                            "TauxApprentissage": self.txApprentissage.get(),
                            "NombreEpoch": self.nbEpoch.get(),
                            "NombreDimensionCachee": self.nbDimCachee.get(),
                            "NombreLayer": self.nbLayer.get(),
                            "NombreSequenceBatch": self.nbSeqBatch.get()}

    def getParametres(self):
        return self.parametres

    def changeInterface(self):
        if self.paramsAvancesValue == 0:  # Enable everyone
            self.paramsAvancesValue = 1
            self.paramsAvancesBouton.config(text="Désactiver les paramètres avancés")
            self.txApprentissage["state"] = tkinter.NORMAL
            self.nbEpoch["state"] = tkinter.NORMAL
            self.nbDimCachee["state"] = tkinter.NORMAL
            self.nbLayer["state"] = tkinter.NORMAL
            self.nbSeqBatch["state"] = tkinter.NORMAL
        elif self.paramsAvancesValue == 1:  # Disable everyone
            self.paramsAvancesValue = 0
            self.paramsAvancesBouton.config(text="Activer les paramètres avancés")
            self.txApprentissage["state"] = tkinter.DISABLED
            self.nbEpoch["state"] = tkinter.DISABLED
            self.nbDimCachee["state"] = tkinter.DISABLED
            self.nbLayer["state"] = tkinter.DISABLED
            self.nbSeqBatch["state"] = tkinter.DISABLED

    def traitementAffichage(self, chemin, taille):
        if len(chemin) > taille:
            cheminCoupe = chemin[-(len(chemin)-taille):]
            return cheminCoupe
        else:
            return chemin

    def valide(self):
        valide = True
        if int(self.nbMorceaux.get()) > 20 or int(self.nbMorceaux.get()) < 1:
            valide = False
        if int(self.dureeMaxMorceau.get()) < 5 or int(self.dureeMaxMorceau.get()) > 340:
            valide = False
        if int(self.bpmMorceau.get()) < 30 or int(self.bpmMorceau.get()) > 240:
            valide = False
        if not valide:
            tkinter.messagebox.showwarning("Attention", "Attention : Le nombre de morceaux, ou \nla durée, ou les bpm est incorrect")
        return valide

    def charging(self, master):
        if self.valide():
            self.textBoutonValider.set("En chargement...")
            self.saveParametres()
            TraitementFichiers.main(self.parametres)
            master.switch_frame()
            self.textBoutonValider.set("Valider")

        return

    # Méthode pour l'explorateur de fichier
    def Browser(self):
        filename = tkinter.filedialog.askdirectory().replace("/", os.sep)
        self.urlVar.set(self.traitementAffichage(filename, 20))
        self.urlVar.set(filename)

    def credits(self):
        tkinter.messagebox.showinfo("Crédits", "Créé par:\nAntoine Escriva\nFlorian Bossard\nClément Guérin\nRaphaël Garnier\nClément Bruschini\n\nRepris par:\nYunfei Jia\nRaphaël Garnier")

    def about(self):
        tkinter.messagebox.showinfo("À propos", "Application développée dans le cadre de la matière Conduite et gestion de projet en 2ème année du cycle Ingénieur à Sup Galilée.\nApplication poursuivie en stage du 03/05/2021 au 02/07/21\nVersion 1.5, 2021")


def geoliste(g):
    # Récupère les infos relatives à l'écran
    r = [i for i in range(0, len(g)) if not g[i].isdigit()]
    return [int(g[0:r[0]]), int(g[r[0]+1:r[1]]), int(g[r[1]+1:r[2]]), int(g[r[2]+1:])]


def centrefenetre(fen):
    # Fonctions pour centrer la fenêtre au milieu de l'écran
    fen.update_idletasks()
    l, h, x, y = geoliste(fen.geometry())
    fen.geometry("%dx%d%+d%+d" % (l, h, (fen.winfo_screenwidth()-l)//2, (fen.winfo_screenheight()-h)//2))
