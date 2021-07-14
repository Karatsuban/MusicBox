# coding:utf-8

import tkinter
import tkinter.filedialog
from tkinter import ttk
import tkinter.font as tkfont
import datetime
from source.controller import ImportExportParametres as Iep

hauteurBout = 2


class FormatCreator(tkinter.Frame):

    def __init__(self, master):
        tkinter.Frame.__init__(self, master)

        # Réglage police du titre et du texte
        self.policeTitre = tkfont.Font(family='Helvetica', size=20)
        self.PoliceTexte = tkfont.Font(family='Helvetica', size=13)
        # Réglage arrière plan
        self.configure(bg='white')

        self.typeIndexParElementListe = []
        self.nbElementsListe = []

        self.listeTypes = ["Aucun", "Intervalle inter-notes:TEMPS", "Numéro touche:TOUCHE", "Touche (différentiel):TOUCHE", "Vélocité:VELOCITE",
                           "Type note:TYPE", "Position dans la mesure:POSITION"]
        self.typesAbrev = ["Aucun", "IIN", "TNB", "TD", "V", "TN", "PM"]

        # --------- Fenêtre de Configuration ------------ #

        # Création et placement du titre du cadre
        tkinter.Label(self, text="Génération de format", bg='white', font=self.policeTitre).grid(row=0, column=0, columnspan=2, sticky="W")

        # Création et placement du label nom du format
        tkinter.Label(self, text="Nom du format", width=15, height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=1, column=0, sticky="W")
        self.nomFormatVar = tkinter.StringVar()
        self.nomFormatEntry = tkinter.Entry(self, width=20, text=self.nomFormatVar)  # widget d'entrée du nom du format
        self.nomFormatEntry.grid(row=1, column=1, sticky="E")
        self.nomFormatVar.trace_add("write", self.updateSaveButton)

        # Création et placement du label Nombre d'éléments
        self.nbMorceauxLabel = tkinter.Label(self, text="Nombre d'éléments", height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=2, column=0, sticky="W")
        self.nbElementsVar = tkinter.StringVar()
        self.nbElementsVar.trace_add("write", self.maj_nbElementListe)  # la méthode maj_nbElementListe est appelée lors d'une écriture dans le widget

        self.nbElements = tkinter.Entry(self, width=20, text=self.nbElementsVar)  # Création et placement d'une Entry pour choisir le nombre d'éléments
        self.nbElements.grid(row=2, column=1, sticky="E")

        # Label pour le numero d'élément
        tkinter.Label(self, text="N° élément", width=15, height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=3, column=0)

        # Label pour le type d'élément
        tkinter.Label(self, text="Type de l'élément", width=15, height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=3, column=1)

        # Création de la combobox de Choix de l'élément
        self.numElementBox = tkinter.ttk.Combobox(self, values=[], state=tkinter.DISABLED)  # les values sont vides pour le moment et le widget désactivé
        self.numElementBox.grid(row=4, column=0, sticky="W")
        self.numElementBox.bind("<<ComboboxSelected>>", lambda e: [self.selectionElement()])  # appel de la méthode selectionElement() lorsqu'un élément est sélectionné

        # Création de la combobox pour le choix de type de l'élément
        self.typeElementBox = tkinter.ttk.Combobox(self, values=self.listeTypes, state=tkinter.DISABLED)
        # Placement
        self.typeElementBox.grid(row=4, column=1, sticky="E")
        self.typeElementBox.bind("<<ComboboxSelected>>", lambda e: [self.selectionType()])  # appel de la méthode selectionType() lorsqu'un élément est séléctionné

        # affichage choix d'utilisateur
        tkinter.Label(self, text="Aperçu format", width=15, height=hauteurBout, font=self.PoliceTexte, bg='white').grid(row=5, column=0, sticky="W")
        self.userFormatDisplayVar = tkinter.StringVar()
        self.userFormatDisplay = tkinter.Entry(self, textvariable=self.userFormatDisplayVar, width=50, state='readonly')  # affichage d'un aperçu du modèle
        self.userFormatDisplay.grid(row=6, column=0, columnspan=2)

        # checkButton pour l'option de fusion des pistes
        self.fusionPisteVar = tkinter.IntVar()
        self.fusionPisteCheckB = tkinter.Checkbutton(self, text="Fusion des pistes", variable=self.fusionPisteVar, onvalue=True, offvalue="False", bg="white")
        self.fusionPisteCheckB.grid(row=7, column=0, sticky="W")

        # checkButton pour l'option notes entières ou non
        self.noteEntiereVar = tkinter.IntVar()
        self.noteEntiereCheckB = tkinter.Checkbutton(self, text="Note entière", variable=self.noteEntiereVar, onvalue=True, offvalue="False", bg="white")
        self.noteEntiereCheckB.grid(row=8, column=0, sticky="W")

        # checkbutton pour l'option d'encodage des silences ou non
        self.encodageSilencesVar = tkinter.IntVar()
        self.encodageSilencesCheckB = tkinter.Checkbutton(self, text="Encodage des silences", variable=self.encodageSilencesVar, onvalue=True, offvalue="False", bg="white")
        self.encodageSilencesCheckB.grid(row=9, column=0, sticky="W")

        # widget pour le choix d'un découpage toutes les X mesures
        tkinter.Label(self, text="Découpage toutes les X mesures", bg="white").grid(row=10, column=0, sticky="W")
        self.decoupageMesuresVar = tkinter.StringVar()
        self.decoupageMesuresVar.set("-1")
        self.decoupageMesuresEntry = tkinter.Entry(self, textvariable=self.decoupageMesuresVar, width=20)
        self.decoupageMesuresEntry.grid(row=10, column=1, sticky="E")

        # bouton pour enregistrer le modèle
        self.saveButton = tkinter.Button(self, text="Enregistrer", width=20, bg='white', state=tkinter.DISABLED, command=lambda: [self.save()])
        self.saveButton.grid(row=12, column=0, sticky="W")

        # Bouton annuler
        self.annulerButton = tkinter.Button(self, text="Annuler", width=20, bg='white', command=lambda: [self.retourMenu()])
        self.annulerButton.grid(row=12, column=1, sticky="E")

    def fromApp(self):
        # remise à zéro/effacement des paramètres de l'interface
        self.typeIndexParElementListe = []
        self.nbElementsListe = []
        self.nomFormatVar.set("")
        self.nbElementsVar.set("")
        self.numElementBox["state"] = tkinter.DISABLED
        self.typeElementBox["state"] = tkinter.DISABLED
        self.userFormatDisplayVar.set("")
        self.fusionPisteVar.set(False)
        self.noteEntiereVar.set(False)
        self.encodageSilencesVar.set(False)
        self.decoupageMesuresVar.set("-1")
        return

    def maj_nbElementListe(self, *args):
        # fonction appelée lorsque l'utilisateur change la valeur du nombre d'éléments
        if self.nbElements.get().isdigit() and int(self.nbElements.get()) > 0:  # si la nouvelle valeur est un chiffre positif
            nb = int(self.nbElements.get())

            ecart = nb - len(self.typeIndexParElementListe)  # on calcule l'écart avec le nombre précédemment rentré
            if ecart > 0:  # si l'utilisateur rentre un nombre plus grand que le précédent
                self.typeIndexParElementListe += [0 for _ in range(ecart)]  # on remplit le reste de la liste avec des "Aucun"
            else:  # nombre plus petit que le précédent
                self.typeIndexParElementListe = self.typeIndexParElementListe[:nb]  # on coupe la partie de la liste inutile

            self.nbElementsListe = [k + 1 for k in range(nb)]  # fabrication de la liste des numéros d'éléments

            self.numElementBox["state"] = "readonly"
            self.numElementBox["values"] = self.nbElementsListe  # on affiche cette liste
            self.numElementBox.current(0)

            self.typeElementBox["state"] = "readonly"
            self.typeElementBox.current(self.typeIndexParElementListe[int(self.numElementBox.get()) - 1])

            self.updateFormatDisplay()  # mise à jour de l'aperçu du format

    def selectionType(self):
        # fonction appelée lorsque l'utilisateur a séléctionné un type
        elt_select = int(self.numElementBox.get()) - 1  # on récupère l'indice de l'élément
        self.typeIndexParElementListe[int(elt_select)] = self.typeElementBox.current()  # on enregistre le type choisi à l'index de l'élément choisi
        self.updateFormatDisplay()
        return

    def updateFormatDisplay(self):
        val = ":".join([self.listeTypes[k] for k in self.typeIndexParElementListe])  # création de l'affichage avec les noms des types choisis séparés par le séparateur choisi
        self.userFormatDisplayVar.set(val)  # affichage
        self.updateSaveButton()  # mise à jour de l'état du bouton pour enregistrer le modèle

    def updateSaveButton(self, *args):
        # active ou désactive le bouton pour sauvegarder le modèle
        can_save = True
        can_save &= "Aucun" not in self.userFormatDisplayVar.get()  # vérifie que chaque élément a un type non nul
        can_save &= self.nomFormatEntry.get() != ""  # vérifie que le modèle a un nom

        if can_save:
            self.saveButton["state"] = tkinter.NORMAL  # si tout va bien, débloquage du bouton
        else:
            self.saveButton["state"] = tkinter.DISABLED  # sinon on le bloque
        return

    def selectionElement(self):
        # fonction appelée lorsqu'un élément est sélectionné
        elt_select = int(self.numElementBox.get()) - 1  # récupération du numéro de l'élément
        self.typeElementBox.current(self.typeIndexParElementListe[int(elt_select)])  # affichage du type choisi pour cet élément
        return

    def save(self):
        # fonction appelée pour sauvegarder toutes les informations dans un dictionnaire
        format_dico = {"NomFormat": self.nomFormatVar.get(),
                       "NombreElements": self.nbElements.get(),
                       "FracNote": self.noteEntiereVar.get(),
                       "FusionPiste": self.fusionPisteVar.get(),
                       "EncodeSilences": self.encodageSilencesVar.get(),
                       "DecoupeMesure": self.decoupageMesuresVar.get(),
                       "ListeTypesElements": [self.typesAbrev[k] for k in self.typeIndexParElementListe],
                       }
        Iep.addFormat(format_dico)  # écriture du format créé
        self.retourMenu()  # retour à l'interface Menu
        return

    def retourMenu(self):
        # fonction appelée pour retourner à la vue Menu
        self.master.switch_frame("Menu")
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
