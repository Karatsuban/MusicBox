# coding:utf-8

import tkinter
import tkinter.filedialog
from tkinter import messagebox
from source.view.scripts import Lecteur, Menu, Info, GraphDisplay, FormatCreator
from source.controller import TraitementFichiers, ImportExportParametres
import webbrowser
import platform
import datetime
import os

if os.name != "posix":
    from ctypes import windll


class Application(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)  # initialisation d'une fenetre TKinter
        self.title("MusicBox")  # affectation du titre de la fenêtre

        self.configure(bg='white')  # arrière-plan en blanc
        self.option_add("*Font", "Helvetica 13")  # réglage de la police générale
        osName = platform.system()

        self.is_saved = False  # si le modèle a déjà été enregistré ou pas

        # tailles des fenêtres selon les plateformes
        if osName == "Windows":
            self.dicoTaille = {
                "Lecteur": "340x235",
                "Menu": "525x700",
                "Info": "300x120",
                "Graph": "1280x580",
                "Format": "525x450",
            }
        elif osName == "Darwin":
            self.dicoTaille = {
                "Lecteur": "460x205",
                "Menu": "525x700",
                "Info": "300x120",
                "Graph": "1280x580",
                "Format": "525x450",
            }
        else:
            self.dicoTaille = {
                "Lecteur": "350x215",
                "Menu": "600x670",
                "Info": "300x120",
                "Graph": "1280x480",
                "Format": "525x450",
            }

        self.menuBarre = tkinter.Menu(self)  # Barre de Menu

        self.menuFichier = tkinter.Menu(self.menuBarre, tearoff=0)  # Menu pour les modèles
        self.menuFichier.add_command(label="Nouveau", command=self.newModel)  # ajout de boutons dans le menu et leurs commandes associées
        self.menuFichier.add_command(label="Sauvegarder", command=self.saveModel)
        self.menuFichier.add_command(label="Charger", command=self.loadModel)

        self.choixAffichageStatistiques = tkinter.IntVar()
        self.choixAffichageGraphiques = tkinter.IntVar()
        self.menuParam = tkinter.Menu(self.menuBarre, tearoff=0)  # menu pour les paramètres
        self.menuParam.add_checkbutton(label="Affichage Statistiques", variable=self.choixAffichageStatistiques)
        self.menuParam.add_checkbutton(label="Affichage Graphiques loss/acc", variable=self.choixAffichageGraphiques)

        self.menuPropos = tkinter.Menu(self.menuBarre, tearoff=0)  # menu pour les informations sur l'app
        self.menuPropos.add_command(label="À propos", command=about_fen)
        self.menuPropos.add_command(label="Crédits", command=credits_fen)
        self.menuPropos.add_command(label="GitHub", command=github)

        self.menuBarre.add_cascade(label="Modèle", menu=self.menuFichier)  # nommage des boutons sur la barre des menus
        self.menuBarre.add_cascade(label="Paramètres", menu=self.menuParam)
        self.menuBarre.add_cascade(label="À propos", menu=self.menuPropos)

        self.config(menu=self.menuBarre)

        self.dico_formats = {'Melodie': {'NomFormat': 'Melodie', 'NombreElements': '4', 'FracNote': '0', 'FusionPiste': '1', 'EncodeSilences': '0', 'DecoupeMesure': '10',
                                         'ListeTypesElements': ['IIN', 'TN', 'TN', 'PM']},
                             'Rythme': {'NomFormat': 'Rythme', 'NombreElements': '1', 'FracNote': '0', 'FusionPiste': '1', 'EncodeSilences': '1', 'DecoupeMesure': '20',
                                        'ListeTypesElements': ['TN']}
                             }  # formats disponibles par défaut

        format_names = [key for key, _ in self.dico_formats.items()]  # liste des noms de formats disponibles par défaut

        self.parametres = {"URL_Dossier": os.getcwd() + os.sep + "data" + os.sep + "midi",
                           "NombreMorceaux": "2",
                           "DureeMorceaux": "30",
                           "TonaliteMorceaux": "A",
                           "VitesseMorceaux": "30",
                           "TypeGeneration": format_names[0],
                           "TauxApprentissage": "0.01",
                           "NombreEpoch": "200",
                           "NombreDimensionCachee": "128",
                           "NombreLayer": "1",
                           "NombreSequenceBatch": "16",
                           "ChoixAffichageDataInfo": 0
                           }  # parametres par défaut

        if "parametres.csv" in os.listdir(path=os.getcwd() + os.sep + "data"):  # si un fichier de configuration existe
            self.parametres = ImportExportParametres.importFromCSV()  # on le charge dans self.parametres
            self.parametres["NombreMorceaux"] = "2"
            self.parametres["DureeMorceaux"] = "30"

        # on crée le dossier Resultat s'il n'existe pas
        os.makedirs(self.parametres["URL_Dossier"] + os.sep + "Resultat", exist_ok=True)

        self.dicoFrame = {
            "Lecteur": Lecteur.Lecteur(self, self.parametres),
            "Menu": Menu.Menu(self, self.parametres, self.dico_formats),
            "Info": Info.Info(self),
            "Graph": GraphDisplay.GraphDisplay(self),
            "Format": FormatCreator.FormatCreator(self),
        }  # dictionnaire contenant les objets "vue"

        self.frame = self.dicoFrame["Lecteur"]

        self.switch_frame("Menu")
        self.protocol('WM_DELETE_WINDOW', lambda: [self.askWhenClose()])  # fonction à éxécuter lors de la fermeture de la fenêtre

    def switch_frame(self, frame):
        # méthode permettant de changer la frame/vue affichée dans la fenêtre principale
        self.saveParametres()  # on enregistre les paramètres
        self.frame.grid_remove()  # suppression de la frame/vue en affichée
        self.frame = self.dicoFrame[frame]  # affichage de la nouvelle frame/vue

        taille = self.dicoTaille[frame]  # taille de la frame à afficher
        self.geometry(taille)  # appplication de la taille
        self.frame.grid(padx=20, pady=15, sticky="ewsn")

        # fonctions/méthodes à appeler en fonction de la frame à afficher
        if frame == "Menu":
            self.frame.fromApp()
            self.dico_formats = self.dicoFrame["Menu"].dico_formats
        elif frame == "Lecteur":
            self.frame.miseAJourRepertoire(self.parametres)
        elif frame == "Info":
            self.dico_formats = self.dicoFrame["Menu"].dico_formats
            format_nom = self.parametres["TypeGeneration"]
            format_choix = self.dico_formats[format_nom]
            is_model = self.dicoFrame["Menu"].is_model
            self.is_saved = False
            self.frame.lanceTrain(self.parametres, is_model, format_choix)
        elif frame == "Graph":
            self.frame.grid(padx=0, pady=0, ipadx=0, ipady=0)
            self.frame.displayFromApp(self.parametres)
        elif frame == "Format":
            self.frame.fromApp()

    def askWhenClose(self):
        # fonction appelée en cas de fermeture de l'application
        is_model = self.dicoFrame["Menu"].is_model
        is_training = self.dicoFrame["Info"].is_training

        if is_training:  # vérifications si un modèle est en cours d'entraînement
            choix = tkinter.messagebox.askokcancel("Attention", "Entraînement est en cours, voulez-vous l'arrêter?")
            if choix:
                self.dicoFrame["Info"].stopTrain()
            else:
                return

        Lecteur.pygame.mixer.music.stop()
        if is_model:  # vérifications si un modèle est en cours...
            if not self.is_saved:  # ...et n'a pas été enregistré
                choix = tkinter.messagebox.askyesnocancel("Attention", "Un modèle est en cours d'utilisation, \nvoulez-vous l'enregistrer ?")
                if choix:
                    self.saveModel()
                elif choix is None:
                    return

        self.destroy()  # destruction finale de la fenêtre

    def newModel(self):
        # fonction appelée lors de la création d'un nouveau modèle
        if self.dicoFrame["Info"].is_training:  # pas de nouveau modèle si l'un est déjà en cours d'entraînement
            return

        if self.dicoFrame["Menu"].is_model:  # si un modèle est en cours...
            if not self.is_saved:  # ... et n'est pas sauvegardé
                choice = tkinter.messagebox.askyesnocancel("Attention", "Un modèle est déjà en cours d'utilisation, voulez-vous l'enregistrer ?")
                if choice is not None:
                    if choice:  # oui
                        self.saveModel()
                else:
                    return
            # mise à jour de certains widgets et variables
            self.dicoFrame["Menu"].is_model = False  # il n'a pas encore été entraîné
            self.dicoFrame["Menu"].genParamsButton["state"] = tkinter.DISABLED
            self.dicoFrame["Menu"].typeGenComboboite["state"] = "readonly"
            self.dicoFrame["Menu"].openFolderButton["state"] = tkinter.NORMAL

            if self.dicoFrame["Menu"].paramsAvancesValue == 1:  # si les parametres avancés ont été activés
                self.dicoFrame["Menu"].nbDimCachee["state"] = tkinter.NORMAL  # on débloque visuellement des widgets
                self.dicoFrame["Menu"].nbLayer["state"] = tkinter.NORMAL
        return

    def saveModel(self):
        # fonction appelé pour sauvegarder un modèle
        if not self.dicoFrame["Menu"].is_model:  # pas de sauvegarde s'il n'y a pas de modèle en cours
            tkinter.messagebox.showinfo("Attention", "Il n'y a pas de modèle en cours d'utilisation")
            return

        if self.dicoFrame["Info"].is_training:  # pas de sauvegarde de modèle si l'un est déjà en cours d'entraînement
            return

        temp = "Model_" + getDate()  # nom par défaut du modèle
        try:
            nb_epoch = TraitementFichiers.getModelParametres()["TotalEpoch"]  # on récupère le nombre total d'epoch s'il existe
            temp += "_" + str(nb_epoch) + "epoch"  # on l'inscrit dans le nom du modèle
        except KeyError:
            pass

        filename = tkinter.filedialog.asksaveasfilename(initialdir=self.parametres["URL_Dossier"] + os.sep + "Modèles save", defaultextension='.tar', initialfile=temp)
        filename = filename.replace("/", os.sep)

        if filename != "":  # si un nom a été choisi
            TraitementFichiers.saveModel(filename)  # on sauvegarde le modèle
            self.is_saved = True
        return

    def loadModel(self):
        # fonction appelée pour charger un modèle
        if self.dicoFrame["Info"].is_training:  # pas de chargement de modèle si un est en cours d'entraînement
            return

        choice = True
        if self.dicoFrame["Menu"].is_model:  # si un modèle est en cours
            if not self.is_saved:  # si le modèle n'a pas été sauvegardé
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
                model_params = TraitementFichiers.loadModel(filename, user_parametres, self.dico_formats)  # on récupère les paramètres du modèle chargé
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
        return

    def saveParametres(self):
        # enregistre les paramètres récupérés depuis l'interface
        menu = self.dicoFrame["Menu"]
        self.parametres = {"URL_Dossier": menu.urlVar.get(),
                           "NombreMorceaux": menu.nbMorceaux.get(),
                           "DureeMorceaux": menu.dureeMaxMorceau.get(),
                           "TonaliteMorceaux": menu.tonaliteMorceau.get(),
                           "VitesseMorceaux": menu.bpmMorceau.get(),
                           "TypeGeneration": menu.typeGenComboboite.get(),
                           "TauxApprentissage": menu.txApprentissage.get(),
                           "NombreEpoch": menu.nbEpoch.get(),
                           "NombreDimensionCachee": menu.nbDimCachee.get(),
                           "NombreLayer": menu.nbLayer.get(),
                           "NombreSequenceBatch": menu.nbSeqBatch.get(),
                           "ChoixAffichageStatistiques": self.choixAffichageStatistiques.get(),
                           "ChoixAffichageGraphiques": self.choixAffichageGraphiques.get(),
                           }
        return

    def getParametres(self):
        # enregistre les paramètres et les retourne
        self.saveParametres()
        return self.parametres


def credits_fen():
    # affiche une fenêtre avec quelques crédits
    tkinter.messagebox.showinfo("Crédits", "Créé par:\nAntoine Escriva\nFlorian Bossard\nClément Guérin\n"
                                           "Raphaël Garnier\nClément Bruschini\n\nRepris par:\nYunfei Jia\nRaphaël Garnier")
    return


def about_fen():
    # affiche une fenêtre avec quelques informations
    tkinter.messagebox.showinfo("À propos",
                                "Application développée dans le cadre de la matière Conduite et Gestion de Projet en 2ème année du cycle Ingénieur à Sup Galilée.\n"
                                "Application poursuivie en stage du 03/05/2021 au 02/07/21\nVersion 3.0.0, 2021")
    return


def github():
    # ouvre le navigateur sur le lien
    webbrowser.open("https://github.com/Karatsuban/MusicBox", new=0)
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


def centrefenetre(fen):
    # fonctions pour centrer la fenêtre au milieu à gauche de l'écran
    fen.update_idletasks()
    g = fen.geometry()
    r = [i for i in range(0, len(g)) if not g[i].isdigit()]
    l, h, x, y = [int(g[0:r[0]]), int(g[r[0] + 1:r[1]]), int(g[r[1] + 1:r[2]]), int(g[r[2] + 1:])]
    fen.geometry("%dx%d%+d%+d" % (l, h, (fen.winfo_screenwidth() // 2 - l) // 2, (fen.winfo_screenheight() - h) // 2))
    return


def start():
    # instancie la classe Application
    app = Application()
    app.iconbitmap("." + os.sep + "source" + os.sep + "view" + os.sep + "icon" + os.sep + "icon.ico")  # chargement de l'icône de l'app

    centrefenetre(app)  # placement de la fenêtre
    app.focus_force()  # mettre en premier plan au lancement
    app.resizable(width=False, height=False)  # empêchee le redimensionnement

    if os.name != "posix":  # netteté de la police de caractères
        windll.shcore.SetProcessDpiAwareness(1)

    app.mainloop()  # Boucle principale de l'interface
    return
