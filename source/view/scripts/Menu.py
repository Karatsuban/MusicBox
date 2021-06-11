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

        self.is_model = False  # aucun modèle n'a été crée ou chargé

        # --------- Configuration ------------ #

        # Création et placement du titre du cadre
        self.configurationLabel = tkinter.Label(self, text="Configuration", bg='white', font=self.policeTitre).grid(row=0, column=0, sticky="W")

        # Création et placement du Bouton ouvrir dossier
        self.openFolderButton = tkinter.Button(self, text="Sélection Dossier", bg="white", font=self.PoliceTexte, bd=1, command=lambda: [self.Browser()])
        self.openFolderButton.grid(row=1, column=0, sticky="W")

        # Création de la variable contenant le chemin
        self.urlVar = tkinter.StringVar()
        self.urlVar.set(self.parametres["URL_Dossier"])
        # Placement de la zone et affectation d'un texte dans cette zone d'affichage
        self.urlEntry = tkinter.Entry(self, state='readonly', text=self.urlVar, width=25)
        self.urlEntry.grid(row=1, column=1, sticky="EW")

        # Création et placement du label Nombre de morceaux
        varnbMorceaux = tkinter.StringVar(self)
        varnbMorceaux.set(self.parametres["NombreMorceaux"])
        self.nbMorceauxLabel = tkinter.Label(self, text="Nombre de morceaux", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=2, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le nombre de morceaux
        self.nbMorceaux = tkinter.Spinbox(self, from_=1, to=200, width=10, textvariable=varnbMorceaux)
        self.nbMorceaux.grid(row=2, column=1, sticky="W")
        self.nbMorceauxLimit = tkinter.Label(self, text="(1-200)", bg="white").grid(row=2, column=1, sticky="e")

        # Création et placement du label Durée max des morceaux
        vardureeMaxMorceau = tkinter.StringVar(self)
        vardureeMaxMorceau.set(self.parametres["DureeMorceaux"])
        tkinter.Label(self, text="Durée max morceaux", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=3, column=0, sticky="W")
        # Création du spinbox de durée  max du morceau
        self.dureeMaxMorceau = tkinter.Spinbox(self, from_=5, to=1000, width=10, textvariable=vardureeMaxMorceau)
        # Placement de la spinbox
        self.dureeMaxMorceau.grid(row=3, column=1, sticky="W")
        # Placement de l'affichage des limites de la durée
        tkinter.Label(self, text="(5-1000)", bg="white").grid(row=3, column=1, sticky="e")

        # Tonalité de morceaux
        tkinter.Label(self, text="Tonalité de morceaux", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=4, column=0, sticky="W")
        # Bouton Tonalite du morceau
        self.tonaliteMorceau = tkinter.Spinbox(self, values=("A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"), width=10)
        self.tonaliteMorceau.grid(row=4, column=1, sticky="W")

        # Vitesse des morceaux
        varbpmMorceau = tkinter.StringVar(self)
        varbpmMorceau.set(self.parametres["VitesseMorceaux"])
        tkinter.Label(self, text="Vitesse des morceaux", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=5, column=0, sticky="W")
        # Bouton vitesse des morceau
        self.bpmMorceau = tkinter.Spinbox(self, from_=1, to=360, width=10, textvariable=varbpmMorceau)
        self.bpmMorceau.grid(row=5, column=1, sticky="W")
        self.bpmMorceauLimit = tkinter.Label(self, text="(1-360)", bg="white").grid(row=5, column=1, sticky="e")

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
        varTxApp.set(float(self.parametres["TauxApprentissage"]))
        tkinter.Label(self, text="Taux apprentissage", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=9, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le taux d'apprentissage
        self.txApprentissage = tkinter.Entry(self, textvariable=varTxApp, width=11, state=tkinter.DISABLED)
        self.txApprentissage.grid(row=9, column=1, sticky="W")
        tkinter.Label(self, text="(0-1)", bg="white").grid(row=9, column=1, sticky="e")

        # Création et placement du label Nombre d'epoch
        varEpoch = tkinter.StringVar(self)
        varEpoch.set(self.parametres["NombreEpoch"])
        tkinter.Label(self, text="Nombre d'Epoch", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=10, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le nombre d'epoch
        self.nbEpoch = tkinter.Spinbox(self, from_=1, to=1000000, width=10, textvariable=varEpoch, state=tkinter.DISABLED)
        self.nbEpoch.grid(row=10, column=1, sticky="W")
        tkinter.Label(self, text="(1-1000000)", bg="white").grid(row=10, column=1, sticky="e")

        # Création et placement du label Nombre de dimension cachée
        self.varDimCach = tkinter.StringVar(self)
        self.varDimCach.set(self.parametres["NombreDimensionCachee"])
        tkinter.Label(self, text="Dimension cachée", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=11, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le nombre de dimension cachée
        self.nbDimCachee = tkinter.Spinbox(self, from_=16, to=2048, width=10, textvariable=self.varDimCach, state=tkinter.DISABLED)
        self.nbDimCachee.grid(row=11, column=1, sticky="W")
        tkinter.Label(self, text="(Entre 2" + chr(0x2074) + "et 2" + chr(0x00B9) + chr(0x00B9) + ")", bg="white").grid(row=11, column=1, sticky="e")

        # Création et placement du label Nombre de layer
        self.varNbLayer = tkinter.StringVar(self)
        self.varNbLayer.set(self.parametres["NombreLayer"])
        tkinter.Label(self, text="Nombre de layer", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=12, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le nombre de layer
        self.nbLayer = tkinter.Spinbox(self, from_=1, to=5, width=10, textvariable=self.varNbLayer, state=tkinter.DISABLED)
        self.nbLayer.grid(row=12, column=1, sticky="W")
        tkinter.Label(self, text="(1-5)", bg="white").grid(row=12, column=1, sticky="e")

        # Création et placement du label Nombre de sequence par batch
        varSeqBa = tkinter.StringVar(self)
        varSeqBa.set(self.parametres["NombreSequenceBatch"])
        tkinter.Label(self, text="Séquences par batch", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=15, column=0, sticky="W")
        # Création et placement d'une spinbox pour choisir le nombre de seq du batch
        self.nbSeqBatch = tkinter.Spinbox(self, from_=1, to=512, width=10, textvariable=varSeqBa, state=tkinter.DISABLED)
        self.nbSeqBatch.grid(row=15, column=1, sticky="W")
        tkinter.Label(self, text="(Entre 2" + chr(0x2070) + "et 2" + chr(0x2079) + ")", bg="white").grid(row=15, column=1, sticky="e")

        # Création et placement du Bouton Lecteur
        self.textBoutonLecteur = tkinter.StringVar()
        self.textBoutonLecteur.set("Accès direct au lecteur")
        self.Lecteur = tkinter.Button(self, textvariable=self.textBoutonLecteur, bg="white", font=self.PoliceTexte, bd=1, command=lambda: [self.master.saveParametres(), master.switch_frame("Lecteur")])
        self.Lecteur.grid(row=16, column=0, sticky="EW")

        # Création et placement du Bouton Entraîner
        self.textBoutonValider = tkinter.StringVar()
        self.textBoutonValider.set("Entraîner")
        self.Valider = tkinter.Button(self, textvariable=self.textBoutonValider, width=20, bg="white", font=self.PoliceTexte, bd=1, command=lambda: [self.charging()])
        self.Valider.grid(row=16, column=1, sticky="E")

        # bouton pour sauvegarder les paramètres
        self.saveParamsButton = tkinter.Button(self, text="Sauvegarder paramètres", bg="white", command=lambda: [self.exportParametres()])
        self.saveParamsButton.grid(row=17, column=0, sticky="W")

        # bouton pour générer d'autres morceaux
        self.genParamsButton = tkinter.Button(self, text="Générer morceaux", state=tkinter.DISABLED, width=20, bg="white", command=lambda: [self.genereNewMorceau(master)])
        self.genParamsButton.grid(row=17, column=1, sticky="E")


    def genereNewMorceau(self, master):
        if self.valide():
            self.master.saveParametres()
            TraitementFichiers.genereNew(self.parametres)
            master.switch_frame("Lecteur")
        return

    def exportParametres(self):
        self.master.saveParametres()
        ImportExportParametres.exportInCSV(self.parametres)


    def changeInterface(self):
        if self.paramsAvancesValue == 0:  # Enable everyone
            self.paramsAvancesValue = 1
            self.paramsAvancesBouton.config(text="Désactiver les paramètres avancés")
            self.txApprentissage["state"] = tkinter.NORMAL
            self.nbEpoch["state"] = tkinter.NORMAL
            self.nbSeqBatch["state"] = tkinter.NORMAL
            if not self.is_model:  # paramètres bloqués si un modèle est chargé
                self.nbDimCachee["state"] = tkinter.NORMAL
                self.nbLayer["state"] = tkinter.NORMAL

        elif self.paramsAvancesValue == 1:  # Disable everyone
            self.paramsAvancesValue = 0
            self.paramsAvancesBouton.config(text="Activer les paramètres avancés")
            self.txApprentissage["state"] = tkinter.DISABLED
            self.nbEpoch["state"] = tkinter.DISABLED
            self.nbDimCachee["state"] = tkinter.DISABLED
            self.nbLayer["state"] = tkinter.DISABLED
            self.nbSeqBatch["state"] = tkinter.DISABLED

    def valide(self):
        valide = True
        if "." in self.nbMorceaux.get() or int(float(self.nbMorceaux.get())) > 200 or int(float(self.nbMorceaux.get())) < 1:
            valide = False
        if "." in self.dureeMaxMorceau.get() or int(float(self.dureeMaxMorceau.get())) < 5 or int(float(self.dureeMaxMorceau.get())) > 1000:
            valide = False
        if "." in self.bpmMorceau.get() or int(float(self.bpmMorceau.get())) < 1 or int(float(self.bpmMorceau.get())) > 360:
            valide = False
        if float(self.txApprentissage.get()) <= 0 or float(self.txApprentissage.get()) > 1:
            valide = False
        if "." in self.nbEpoch.get() or int(float(self.nbEpoch.get())) < 1 or int(float(self.nbEpoch.get())) > 1000000:
            valide = False
        if "." in self.nbDimCachee.get() or int(float(self.nbDimCachee.get())) < 16 or int(float(self.nbDimCachee.get())) > 2048:
            valide = False
        if "." in self.nbSeqBatch.get() or int(float(self.nbSeqBatch.get())) < 1 or int(float(self.nbSeqBatch.get())) > 512:
            valide = False

        if not valide:
            tkinter.messagebox.showwarning("Attention", "Attention : un des paramètre saisi est incorrect! \n Veuillez bien respecter les indications.")
        return valide

    def charging(self):
        if self.valide():
            if not self.is_model:
                self.genParamsButton["state"] = tkinter.NORMAL

            self.master.saveParametres()
            if self.paramsAvancesValue == 1:
                self.nbDimCachee["state"] = tkinter.DISABLED
                self.nbLayer["state"] = tkinter.DISABLED
                self.typeGenComboboite["state"] = tkinter.DISABLED
            self.master.switch_frame("Info")
            self.is_model = True
        return

    # Méthode pour l'explorateur de fichier
    def Browser(self):
        filename = tkinter.filedialog.askdirectory().replace("/", os.sep)
        if filename == "":
            self.urlVar.set(self.urlVar.get())
        else:
            if verifMIDI(filename):
                self.urlVar.set(traitementAffichage(filename, 20))
                self.urlVar.set(filename)
                muchFileWarning(filename)
            else:
                tkinter.messagebox.showerror('Erreur', "Il y a pas de fichier .mid dans ce dossier!\nChemin va être remplacé par défault.")
                self.urlVar.set(self.urlVar.get())


def muchFileWarning(path):
    nb = len(os.listdir(path))
    if nb > 500:
        tkinter.messagebox.showinfo('MuchFilesWarning', "Nombre de fichier .mid détecté est > 500\n Ignorez ce message si vous avez une mémoire suffisante.")


# Verifier si fichiers .mid existe dans le dossier choisi.
def verifMIDI(path):
    files = os.listdir(path)
    for k in range(len(files)):
        files[k] = os.path.splitext(files[k])[1]

    extention = '.mid'
    if extention in files:
        return True
    else:
        return False


def traitementAffichage(chemin, taille):
    if len(chemin) > taille:
        cheminCoupe = chemin[-(len(chemin) - taille):]
        return cheminCoupe
    else:
        return chemin


def geoliste(g):
    # Récupère les infos relatives à l'écran
    r = [i for i in range(0, len(g)) if not g[i].isdigit()]
    return [int(g[0:r[0]]), int(g[r[0] + 1:r[1]]), int(g[r[1] + 1:r[2]]), int(g[r[2] + 1:])]


def centrefenetre(fen):
    # Fonctions pour centrer la fenêtre au milieu de l'écran
    fen.update_idletasks()
    l, h, x, y = geoliste(fen.geometry())
    fen.geometry("%dx%d%+d%+d" % (l, h, (fen.winfo_screenwidth() - l) // 2, (fen.winfo_screenheight() - h) // 2))

