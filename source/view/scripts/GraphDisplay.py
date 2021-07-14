# coding:utf-8
import os
import tkinter
from PIL import ImageTk, Image
from tkinter import ttk


class GraphDisplay(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)

        self.master = master
        self.parametres = None
        self.graphPath = None

        self.choixGraphListe = ttk.Combobox(self, state="readonly", width=30)  # combobox listant les graphiques existants
        self.choixGraphListe.grid(row=0, column=0, columnspan=2)
        self.choixGraphListe.bind("<<ComboboxSelected>>", lambda e: [self.displayGraph()])

        self.canvas1 = tkinter.Canvas(self, width=640, height=480, bd=0)  # création des canvas pour afficher les graphiques
        self.canvas2 = tkinter.Canvas(self, width=640, height=480, bd=0)
        self.canvas1.grid(row=1, column=0)  # positionnement des canvas
        self.canvas2.grid(row=1, column=1)

        self.boutonRetour = tkinter.Button(self, text="Retour", bg="white", command=lambda: [self.retour()])  # bouton pour retourner au menu
        self.boutonRetour.grid(row=2, column=0)

        self.image1 = None
        self.image2 = None

    def majRepertoire(self):
        # méthode appelée pour mettre à jour la liste des graphiques
        self.graphPath = self.parametres["URL_Dossier"]+os.sep+"Graphiques"  # chemin du dossier contenant les graphiques

        grapheNamesList = list({"_".join(k.split("_")[:-2]) for k in os.listdir(self.graphPath)})  # récupération de tous les noms de graphiques
        grapheNamesList.sort()
        self.choixGraphListe["values"] = grapheNamesList  # mise à jour de l'affichage de la liste
        return

    def displayFromApp(self, parametres):
        # méthode pour afficher les graphiques depuis le Menu
        self.parametres = parametres
        self.majRepertoire()
        if len(self.choixGraphListe["values"]) != 0:  # le dossier contient des graphiques
            last_idx = len(self.choixGraphListe["values"]) - 1
            self.choixGraphListe.current(last_idx)
        self.displayGraph()
        return

    def displayGraph(self):
        # méthode appelée pour afficher les graphiques ou le message d'erreur à leur place
        if len(self.choixGraphListe["values"]) != 0:  # le dossier contient des graphiques
            prefix = self.graphPath+os.sep+self.choixGraphListe.get()  # récupération du nom du modèle depuis la comboliste

            completePath1 = prefix+"_Graph_Loss.png"
            completePath2 = prefix+"_Graph_Accuracy.png"

            self.image1 = ImageTk.PhotoImage(Image.open(completePath1))
            self.image2 = ImageTk.PhotoImage(Image.open(completePath2))
            self.canvas1.create_image(0, 0, anchor=tkinter.NW, image=self.image1)  # remplissage des canvas avec les images
            self.canvas2.create_image(0, 0, anchor=tkinter.NW, image=self.image2)
        else:
            canvas1_id = self.canvas1.create_text(10, 10, anchor="nw")
            canvas2_id = self.canvas2.create_text(10, 10, anchor="nw")
            self.canvas1.itemconfig(canvas1_id, text="Aucun graphique à afficher !")
            self.canvas2.itemconfig(canvas2_id, text="Aucun graphique à afficher !")
        return

    def retour(self):
        # retour au menu
        self.master.switch_frame("Menu")
        return
