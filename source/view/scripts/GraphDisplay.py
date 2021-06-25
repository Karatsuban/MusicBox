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

        self.choixGraphListe = ttk.Combobox(self, state="readonly", width=30)
        self.choixGraphListe.grid(row=0, column=0, columnspan=2)
        self.choixGraphListe.bind("<<ComboboxSelected>>", lambda e: [self.displayGraph()])

        self.canvas1 = tkinter.Canvas(self, width=640, height=480, bd=0)
        self.canvas2 = tkinter.Canvas(self, width=640, height=480, bd=0)
        self.canvas1.grid(row=1, column=0)
        self.canvas2.grid(row=1, column=1)

        self.boutonRetour = tkinter.Button(self, text="Retour", bg="white", command=lambda: [self.retour()])
        self.boutonRetour.grid(row=2, column=0)

        self.image1 = None
        self.image2 = None

    def majRepertoire(self):
        self.graphPath = self.parametres["URL_Dossier"]+os.sep+"Graphiques"

        grapheNamesList = list({"_".join(k.split("_")[:3]) for k in os.listdir(self.graphPath)})
        grapheNamesList.sort()
        self.choixGraphListe["values"] = grapheNamesList
        return

    def displayFromApp(self, parametres):
        self.parametres = parametres
        self.majRepertoire()
        last_idx = len(self.choixGraphListe["values"]) - 1
        self.choixGraphListe.current(last_idx)
        self.displayGraph()

    def displayGraph(self):
        prefix = self.graphPath+os.sep+self.choixGraphListe.get()  # récupération du nom du modèle depuis la comboliste

        completePath1 = prefix+"_Graph_Loss.png"
        completePath2 = prefix+"_Graph_Accuracy.png"

        self.image1 = ImageTk.PhotoImage(Image.open(completePath1))
        self.image2 = ImageTk.PhotoImage(Image.open(completePath2))
        self.canvas1.create_image(0, 0, anchor=tkinter.NW, image=self.image1)
        self.canvas2.create_image(0, 0, anchor=tkinter.NW, image=self.image2)
        return

    def retour(self):
        # retour au menu
        self.master.switch_frame("Menu")
