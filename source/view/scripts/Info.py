# coding:utf-8

import time
import tkinter
import tkinter.font as tkfont
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
        self.titre = tkfont.Font(family='Helvetica', size=20)
        self.texte = tkfont.Font(family='Helvetica', size=13)

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

        # queues pour communiquer avec le thread
        self.queue = queue.Queue()
        self.finQueue = queue.Queue(maxsize=1)
        self.thread = None

        self.time_received = 0  # heure de reception du dernier message
        self.temps_restant = 0  # temps restant avant la fin du train

        self.is_training = False

    def lanceTrain(self, parametres, is_model, format_choix):
        # lance l'entraînement dans un thread
        self.parametres = parametres  # récupération des paramètres
        self.is_training = True
        self.avancement.set("../..")  # rafraîchissement de l'affichage
        self.restant.set("..s")
        self.time_received = 0
        self.temps_restant = 0
        # lancement de la fonction qui va appeler l'entraînement
        self.thread = threading.Thread(target=TraitementFichiers.train, args=(parametres, is_model, self.queue, self.finQueue, format_choix), daemon=True)
        self.thread.start()  # démarrage du thread
        self.after(0, self.updateEpoch())  # lancement de la fonction de rafraîchissement de l'affichage
        return

    def stopTrain(self):
        # méthode appelée lorsque l'utilisateur appuie sur le bouton "fin d'entraînement"
        print("Arret entrainement")
        self.is_training = False
        self.finQueue.put("FIN")  # envoi du signal d'arrêt au modèle par la queue
        return

    def updateEpoch(self):
        # fonction mettant à jour le nombre d'epoch effectuée et le temps restant sur l'interface
        if not self.thread.is_alive() and self.queue.empty():  # si le thread est fini et que la queue de message est vide
            if self.parametres["ChoixAffichageGraphiques"] == 1:  # on switche la vue...
                self.after(0, self.master.switch_frame("Graph"))  # sur la vue "Graphe"...
            else:
                self.after(0, self.master.switch_frame("Menu"))  # ou la vue "Menu"
            self.is_training = False
            return

        while not self.queue.empty():  # tant qu'il y a des messages dans la queue
            infos = self.queue.get().split(":")  # on récupère les informations
            epoch = infos[0]+"/"+infos[1]
            self.avancement.set(epoch)  # mise à jour de la progression sur la vue
            self.temps_restant = (float(infos[2]) / float(infos[0])) * (float(infos[1]) - float(infos[0]))  # estimation du temps restant
            self.time_received = time.time()  # temps de reception du dernier message

        # calcul du temps restant basé sur la dernière estimation et le temps écoulé depuis son dernier calcul
        temp = max(0.0, self.temps_restant - (time.time() - self.time_received))
        self.restant.set(timeConversion(temp))  # mise à jour du temps restant sur l'affichage
        self.after(100, lambda: self.updateEpoch())  # la fonction se rappelle elle-même sans passer par de la récursion
        return


def timeConversion(N):
    # renvoie le temps restant sour un format sympathique
    n = time.gmtime(N)
    if N < 60:
        return time.strftime("%Ss", n)  # en secondes
    elif N < 3600:
        return time.strftime("%Mm %Ss", n)  # en minutes et secondes
    else:
        return time.strftime("%Hh %Mm %Ss", n)  # en heures, minutes et secondes
