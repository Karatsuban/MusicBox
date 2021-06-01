# coding:utf-8

import tkinter
import tkinter.font as tkFont
from source.controller import TraitementFichiers
import threading
import queue


class Info(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)

        # Couleur de fond
        self.configure(bg='white')

        # Réglages de la police du titre puis du texte
        self.titre = tkFont.Font(family='Helvetica', size=20)
        self.texte = tkFont.Font(family='Helvetica', size=13)

        # Création du label affichant la progression
        tkinter.Label(self, text="Progression : ", bg='white').grid(row=0, column=0)
        self.avancement = tkinter.StringVar()
        self.avancement.set("../..")
        self.avancementLabel = tkinter.Label(self, textvariable=self.avancement, bg='white').grid(row=0, column=1)

        # Création du Label affichant le temps restant
        tkinter.Label(self, text="Temps restant estimé : ", bg='white').grid(row=1, column=0)
        self.restant = tkinter.StringVar()
        self.restant.set("..s")
        self.restantLabel = tkinter.Label(self, textvariable=self.restant, bg='white').grid(row=1, column=1)

        # bouton pour arrêter l'entrainement
        self.stopTrainButton = tkinter.Button(self, text="Arrêt entraînement", width=20,command=lambda: [self.stopTrain()]).grid(row=2, column=0)

        self.queue = queue.Queue()
        self.finQueue = queue.Queue(maxsize=1)
        self.thread = None

    def lanceTrain(self, parametres, is_model):
        # mettre traitementFichiers dans thread

        self.thread = threading.Thread(target=TraitementFichiers.train, args=(parametres, is_model, self.queue, self.finQueue), daemon=True)
        self.thread.start()
        self.after(0, self.updateEpoch())

    def stopTrain(self):
        print("Arrête train")
        self.finQueue.put("FIN")

    def updateEpoch(self):
        if not self.thread.is_alive() and self.queue.empty():
            self.after(0, self.master.switch_frame("Menu"))
            return

        while not self.queue.empty():
            infos = self.queue.get().split(":")
            epoch = infos[0]+"/"+infos[1]
            restant = (float(infos[2]) / float(infos[0])) * (float(infos[1]) - float(infos[0]))

            self.avancement.set(epoch)
            self.restant.set(str(int(restant))+"s")

        self.after(100, lambda: self.updateEpoch())
        return
