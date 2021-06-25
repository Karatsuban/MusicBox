# coding:utf-8

import time
import tkinter
import tkinter.font as tkFont
import matplotlib.pyplot as plt
from source.controller import TraitementFichiers
import threading
import queue


class Info(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)

        # Couleur de fond
        self.configure(bg='white')

        # paramètres
        self.parametres = None

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
        self.restant.set("")
        self.restantLabel = tkinter.Label(self, textvariable=self.restant, bg='white').grid(row=1, column=1)

        # bouton pour arrêter l'entrainement
        self.stopTrainButton = tkinter.Button(self, text="Arrêt entraînement", width=20, command=lambda: [self.stopTrain()]).grid(row=2, column=0)

        self.queue = queue.Queue()
        self.finQueue = queue.Queue(maxsize=1)
        self.thread = None

        self.time_received = 0  # heure de reception du dernier message
        self.temps_restant = 0  # temps restant avant la fin du train

        self.is_training = False

    def lanceTrain(self, parametres, is_model):
        # lance l'entraînement dans un thread
        self.parametres = parametres
        self.is_training = True
        self.avancement.set("../..")  # rafraîchissement de l'affichage
        self.restant.set("..s")
        self.time_received = 0
        self.temps_restant = 0

        self.thread = threading.Thread(target=TraitementFichiers.train, args=(parametres, is_model, self.queue, self.finQueue), daemon=True)
        self.thread.start()
        self.after(0, self.updateEpoch())

    def stopTrain(self):
        print("Arrêt train")
        self.is_training = False
        self.finQueue.put("FIN")  # envoi du signal d'arrêt au modèle

    def updateEpoch(self):
        if not self.thread.is_alive() and self.queue.empty():
            if self.parametres["ChoixAffichageGraphiques"] == 1:
                self.after(0, self.master.switch_frame("Graph"))
            else:
                self.after(0, self.master.switch_frame("Menu"))
            self.is_training = False
            return

        while not self.queue.empty():
            infos = self.queue.get().split(":")
            epoch = infos[0]+"/"+infos[1]
            self.temps_restant = (float(infos[2]) / float(infos[0])) * (float(infos[1]) - float(infos[0]))

            self.time_received = time.time()  # temps de reception du dernier message
            self.avancement.set(epoch)

        temp = max(0.0, self.temps_restant - (time.time() - self.time_received))
        self.restant.set(timeConversion(temp))
        self.after(100, lambda: self.updateEpoch())
        return


def timeConversion(N):
    n = time.gmtime(N)
    if N < 60:
        return time.strftime("%Ss", n)
    elif N < 3600:
        return time.strftime("%Mm %Ss", n)
    else:
        return time.strftime("%Hh %Mm %Ss", n)
