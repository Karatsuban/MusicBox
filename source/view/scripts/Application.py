# coding:utf-8

import tkinter
import tkinter.filedialog
from tkinter import messagebox
from source.view.scripts import Lecteur, Menu, Info
from source.controller import TraitementFichiers, ImportExportParametres
import webbrowser
import platform
import datetime
import os

if os.name != "posix":
    from ctypes import windll


#######################################################
# Classe mère de l'interface
#######################################################

class Application(tkinter.Tk):
    def __init__(self):
        # Initialisation d'une fenetre TKinter
        tkinter.Tk.__init__(self)
        # Affectation du titre de la fenêtre
        self.title("MusicBox")

        # Réglage du fond en blanc
        self.configure(bg='white')

        osName = platform.system()

        # Si modele a deja ete enregistrer
        self.is_saved = False

        if osName == "Windows":
            self.dicoTaille = {
                "Lecteur": "390x295",
                "Menu": "525x680",
                "Info": "300x120",
            }
        elif osName == "Darwin":
            self.dicoTaille = {
                "Lecteur": "410x265",
                "Menu": "525x680",
                "Info": "300x120",
            }
        else:
            self.dicoTaille = {
                "Lecteur": "400x275",
                "Menu": "600x650",
                "Info": "300x120",
            }

        # Barre de Menu
        self.menuBarre = tkinter.Menu(self)

        self.menuFichier = tkinter.Menu(self.menuBarre, tearoff=0)
        self.menuFichier.add_command(label="Nouveau", command=self.newModel)
        self.menuFichier.add_command(label="Sauvegarder", command=self.saveModel)
        self.menuFichier.add_command(label="Charger", command=self.loadModel)

        self.menuParam = tkinter.Menu(self.menuBarre, tearoff=0)
        self.choisiAffichageVar = tkinter.IntVar()
        self.menuParam.add_checkbutton(label="Affichage Data Info", variable=self.choisiAffichageVar)

        self.menuPropos = tkinter.Menu(self.menuBarre, tearoff=0)
        self.menuPropos.add_command(label="À propos", command=about)
        self.menuPropos.add_command(label="Crédits", command=credits)
        self.menuPropos.add_command(label="GitHub", command=github)

        self.menuBarre.add_cascade(label="Modèle", menu=self.menuFichier)  # Menu déroulant "Fichier"
        self.menuBarre.add_cascade(label="Paramètre", menu=self.menuParam)  # Menu déroulant "Paramètre"
        self.menuBarre.add_cascade(label="À propos", menu=self.menuPropos)  # Menu déroulant "À propos"

        self.config(menu=self.menuBarre)

        ########################################################################
        # Parametre par defaut
        ##########################################################################

        self.format_liste = ["Rythme", "Melodie", "Melodie_ttt", "Melodie_saut"]  # formats disponibles

        self.parametres = {"URL_Dossier": os.getcwd()+os.sep+"data"+os.sep+"midi",
                           "NombreMorceaux": "2",
                           "DureeMorceaux": "30",
                           "TonaliteMorceaux": "A",
                           "VitesseMorceaux": "30",
                           "TypeGeneration": self.format_liste[1],
                           "TauxApprentissage": "0.01",
                           "NombreEpoch": "200",
                           "NombreDimensionCachee": "128",
                           "NombreLayer": "1",
                           "NombreSequenceBatch": "16",
                           "ChoixAffichageDataInfo": 0
                           }

        path = os.listdir(path=os.getcwd() + os.sep + "data")

        if "parametres.csv" in path:  # Si un fichier de configuration existe
            self.parametres = ImportExportParametres.importFromCSV()  # on le charge dans self.parametres
            self.parametres["NombreMorceaux"] = "2"
            self.parametres["DureeMorceaux"] = "30"

        # on crée le dossier Resultat s'il n'existe pas
        os.makedirs(self.parametres["URL_Dossier"]+os.sep+"Resultat", exist_ok=True)

        self.dicoFrame = {
            "Lecteur": Lecteur.Lecteur(self, self.parametres),
            "Menu": Menu.Menu(self, self.parametres, self.format_liste),
            "Info": Info.Info(self),
        }

        self.frame = self.dicoFrame["Lecteur"]  # frame de base

        self.switch_frame("Menu")
        self.protocol('WM_DELETE_WINDOW', lambda: [self.askWhenClose()])  # fonction à éxécuter lors de la fermeture de la fenêtre

    def askWhenClose(self):
        is_model = self.dicoFrame["Menu"].is_model
        is_training = self.dicoFrame["Info"].is_training

        if is_training:
            choix = tkinter.messagebox.askokcancel("Attention", "Entraînement est en cours, voulez-vous l'arrêter?")
            if choix:
                self.dicoFrame["Info"].stopTrain()
            else:
                return

        if is_model:
            if not self.is_saved:
                Lecteur.pygame.mixer.music.stop()
                choix = tkinter.messagebox.askyesnocancel("Attention", "Un modèle est en cours d'utilisation, \nvoulez-vous l'enregistrer ?")
                if choix:
                    self.saveModel()
                elif choix is None:
                    return

        self.destroy()

    # Cette méthode permet de changer la frame affichée dans la fenetre principale
    def switch_frame(self, frame):
        self.saveParametres()
        self.frame.grid_remove()
        self.frame = self.dicoFrame[frame]

        taille = self.dicoTaille[frame]
        self.geometry(taille)
        self.frame.grid(padx=20, pady=15, sticky="ewsn")

        if frame == "Lecteur":
            self.frame.miseAJourRepertoire(self.parametres)
        if frame == "Info":
            is_model = self.dicoFrame["Menu"].is_model
            self.is_saved = False
            self.frame.lanceTrain(self.parametres, is_model)

    def newModel(self):
        if self.dicoFrame["Info"].is_training:  # en cours d'entraînement
            return

        if self.dicoFrame["Menu"].is_model:
            if not self.is_saved:
                choice = tkinter.messagebox.askyesnocancel("Attention", "Un modèle est déjà en cours d'utilisation, voulez-vous l'enregistrer ?")
                if choice is not None:
                    if choice:  # oui
                        self.saveModel()
                else:
                    return
            self.dicoFrame["Menu"].is_model = False  # on a créé un nouveau modèle
            self.dicoFrame["Menu"].genParamsButton["state"] = tkinter.DISABLED
            self.dicoFrame["Menu"].typeGenComboboite["state"] = tkinter.NORMAL
            self.dicoFrame["Menu"].openFolderButton["state"] = tkinter.NORMAL

            if self.dicoFrame["Menu"].paramsAvancesValue == 1:
                self.dicoFrame["Menu"].nbDimCachee["state"] = tkinter.NORMAL
                self.dicoFrame["Menu"].nbLayer["state"] = tkinter.NORMAL

    def saveModel(self):
        if self.dicoFrame["Info"].is_training:  # en cours d'entraînement
            return

        if not self.dicoFrame["Menu"].is_model:
            tkinter.messagebox.showinfo("Attention", "Il n'y a pas de modèle en cours d'utilisation")
        else:
            temp = "Model_" + getDate()
            try:
                nb_epoch = TraitementFichiers.getModelParametres()["TotalEpoch"]  # on récupère le nombre total d'epoch s'il existe
                temp += "_" + str(nb_epoch) + "epoch"  # on l'inscrit dans le nom du modèle
            except KeyError:
                pass

            filename = tkinter.filedialog.asksaveasfilename(initialdir=self.parametres["URL_Dossier"] + os.sep + "Modèles save", defaultextension='.tar', initialfile=temp).replace("/", os.sep)
            if filename != "":
                TraitementFichiers.saveModel(filename)
                self.is_saved = True

    def loadModel(self):
        if self.dicoFrame["Info"].is_training:  # en cours d'entraînement
            return

        choice = True
        if self.dicoFrame["Menu"].is_model:
            if not self.is_saved:
                choice = tkinter.messagebox.askyesnocancel("Attention", "Un modèle est déjà en cours, souhaitez-vous l'enregistrer ?")
                if choice is not None:
                    if choice:
                        self.saveModel()
        if choice is not None:  # l'utilisateur n'a pas choisi 'cancel'
            loadSavePath = self.parametres["URL_Dossier"] + os.sep + "Modèles save"
            if not os.path.exists(loadSavePath):
                loadSavePath = self.parametres["URL_Dossier"]
            filename = tkinter.filedialog.askopenfilename(initialdir=loadSavePath, filetypes=[('tar files', '.tar')]).replace("/", os.sep)

            if filename != '':
                user_parametres = self.getParametres()  # on récupère les paramètres entrés par l'utilisateur
                model_params = TraitementFichiers.loadModel(filename, user_parametres)  # on récupère les paramètres du modèle chargé
                self.dicoFrame["Menu"].varNbLayer.set(model_params["NombreLayer"])  # on set les valeurs de nbLayer et nbDimCachee avec les paramètres du modèle chargé
                self.dicoFrame["Menu"].varDimCach.set(model_params["NombreDimensionCachee"])
                self.dicoFrame["Menu"].typeGenComboboite.set(model_params["TypeGeneration"])
                self.dicoFrame["Menu"].openFolderButton["state"] = tkinter.DISABLED
                self.dicoFrame["Menu"].typeGenComboboite["state"] = tkinter.DISABLED
                self.dicoFrame["Menu"].is_model = True
                self.is_saved = True  # le modèle chargé n'a pas encore été modifié

                if self.dicoFrame["Menu"].paramsAvancesValue == 1:
                    self.dicoFrame["Menu"].nbDimCachee["state"] = tkinter.DISABLED
                    self.dicoFrame["Menu"].nbLayer["state"] = tkinter.DISABLED
                    self.dicoFrame["Menu"].typeGenComboboite["state"] = tkinter.DISABLED
                self.dicoFrame["Menu"].genParamsButton["state"] = tkinter.NORMAL

    def saveParametres(self):
        self.parametres = {"URL_Dossier": self.dicoFrame["Menu"].urlVar.get(),
                           "NombreMorceaux": self.dicoFrame["Menu"].nbMorceaux.get(),
                           "DureeMorceaux": self.dicoFrame["Menu"].dureeMaxMorceau.get(),
                           "TonaliteMorceaux": self.dicoFrame["Menu"].tonaliteMorceau.get(),
                           "VitesseMorceaux": self.dicoFrame["Menu"].bpmMorceau.get(),
                           "TypeGeneration": self.dicoFrame["Menu"].typeGenComboboite.get(),
                           "TauxApprentissage": self.dicoFrame["Menu"].txApprentissage.get(),
                           "NombreEpoch": self.dicoFrame["Menu"].nbEpoch.get(),
                           "NombreDimensionCachee": self.dicoFrame["Menu"].nbDimCachee.get(),
                           "NombreLayer": self.dicoFrame["Menu"].nbLayer.get(),
                           "NombreSequenceBatch": self.dicoFrame["Menu"].nbSeqBatch.get(),
                           "ChoixAffichageDataInfo": self.choisiAffichageVar.get()
                           }

    def getParametres(self):
        self.saveParametres()
        return self.parametres


def credits():
    tkinter.messagebox.showinfo("Crédits", "Créé par:\nAntoine Escriva\nFlorian Bossard\nClément Guérin\nRaphaël Garnier\nClément Bruschini\n\nRepris par:\nYunfei Jia\nRaphaël Garnier")


def about():
    tkinter.messagebox.showinfo("À propos", "Application développée dans le cadre de la matière Conduite et gestion de projet en 2ème année du cycle Ingénieur à Sup Galilée.\nApplication poursuivie en stage du 03/05/2021 au 02/07/21\nVersion 2.0.0, 2021")


def github():
    webbrowser.open("https://github.com/Karatsuban/MusicBox", new=0)


def getDate():
    date = datetime.datetime.now()
    dateG = datetime.date(date.year, date.month, date.day)
    dg = dateG.isoformat()
    heureG = datetime.time(date.hour, date.minute, date.second)
    hg = heureG.strftime('%H-%M-%S')
    temp = "_".join([dg, hg])
    return temp


def geoliste(g):
    # Récupère les infos relatives à l'écran
    r = [i for i in range(0, len(g)) if not g[i].isdigit()]
    return [int(g[0:r[0]]), int(g[r[0]+1:r[1]]), int(g[r[1]+1:r[2]]), int(g[r[2]+1:])]


def centrefenetre(fen):
    # fonctions pour centrer la fenêtre au milieu de l'écran
    fen.update_idletasks()
    l, h, x, y = geoliste(fen.geometry())
    fen.geometry("%dx%d%+d%+d" % (l, h, (fen.winfo_screenwidth()//2-l)//2, (fen.winfo_screenheight()-h)//2))


def start():
    # instancie la classe Application
    app = Application()
    # icon de l'app
    app.iconbitmap("." + os.sep + "source" + os.sep + "view" + os.sep + "icon" + os.sep + "icon.ico")

    # Centrage du futur affichage
    centrefenetre(app)
    # mettre en premier plan au lancement
    app.focus_force()
    # Empecher le redimensionnement
    app.resizable(width=False, height=False)

    # Pour la netteté de la police de caractères sur Windows
    if os.name != "posix":
        windll.shcore.SetProcessDpiAwareness(1)

    # Boucle principale de l'interface
    app.mainloop()
