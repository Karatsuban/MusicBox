# coding:utf-8

import tkinter
import tkinter.filedialog
from source.view.scripts import Lecteur, Menu, Info
from source.controller import ImportExportParametres
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

        self.dicoTaille = {
            "Lecteur": "525x295",
            "Menu": "525x680",
            "Info": "280x120",
        }
        ########################################################################
        # Parametre par defaut
        ##########################################################################
        self.parametres = {"URL_Dossier": os.getcwd()+os.sep+"data"+os.sep+"midi",
                           "NombreMorceaux": "2",
                           "DureeMorceaux": "30",
                           "TonaliteMorceaux": "A",
                           "VitesseMorceaux": "30",
                           "TypeGeneration": "Rythme et mélodie",
                           "TauxApprentissage": "0.01",
                           "NombreEpoch": "200",
                           "NombreDimensionCachee": "128",
                           "NombreLayer": "1",
                           "NombreSequenceBatch": "16"}

        path = os.listdir(path=os.getcwd() + os.sep + "data")

        if "parametres.csv" in path:  # Si un fichier de configuration existe
            self.parametres = ImportExportParametres.importFromCSV()  # on le charge dans self.parametres
            self.parametres["NombreMorceaux"] = "2"
            self.parametres["DureeMorceaux"] = "30"

        # on crée le dossier Resultat s'il n'existe pas
        os.makedirs(self.parametres["URL_Dossier"]+os.sep+"Resultat", exist_ok=True)

        self.dicoFrame = {
            "Lecteur": Lecteur.Lecteur(self, self.parametres),
            "Menu": Menu.Menu(self, self.parametres),
            "Info": Info.Info(self),
        }

        # frame de base
        self.frame = self.dicoFrame["Lecteur"]

        self.switch_frame("Menu")

    # Cette méthode permet de changer la fame affichée dans la fenetre principale
    def switch_frame(self, frame):
        self.frame.grid_remove()
        self.frame = self.dicoFrame[frame]
        self.parametres = self.dicoFrame["Menu"].getParametres()

        taille = self.dicoTaille[frame]
        self.geometry(taille)
        self.frame.grid(padx=20, pady=15, sticky="ewsn")

        if frame == "Lecteur":
            self.frame.miseAJourRepertoire(self.parametres)
        if frame == "Info":
            is_model = self.dicoFrame["Menu"].is_model
            self.frame.lanceTrain(self.parametres, is_model)


    def popupmsg(self, texte):
        popup = tkinter.Tk()
        centrefenetre(popup)
        popup.title("Erreur")
        popup.config(bg="white")
        label = tkinter.Label(popup, text=texte, bg="white")
        popup.geometry("315x120")
        label.pack(side="top", fill="x", pady=10)
        ok = tkinter.Button(popup, text="Ok", bg="white", command=popup.destroy, width=10)
        ok.pack()


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
