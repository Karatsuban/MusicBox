#coding: utf-8

import tkinter
import tkinter.filedialog
import tkinter.font as tkFont
from tkinter import ttk
from source.view.scripts import Lecteur, Menu
from source.controller import TraitementFichiers, ImportExportParametres
import time
import os

if(os.name != "posix"):
    from ctypes import windll

largeurBout = 15
hauteurBout = 2
margeX = 0
margeY = 0




#######################################################
#Classe mère de l'interface
#######################################################

class Application(tkinter.Tk):
    def __init__(self):
        #Initialisation d'une fenetre TKinter
        tkinter.Tk.__init__(self)
        #Affectation du titre de la fenêtre
        self.title("Génération musique aléatoire")
        #Réglage du fond en blanc
        self.configure(bg='white')


        self.tailleLecteur = "525x300"
        self.tailleMenu = "525x775"

        ########################################################################
        #Parametre par defaut
        ##########################################################################
        self.parametres = {"URL_Dossier": os.getcwd()+os.sep+"data"+os.sep+"midi",
                                "NombreMorceaux": "1",
                                "DureeMorceaux": "60",
                                 "TonaliteMorceaux": "A",
                                 "VitesseMorceaux": "30",
                                "TypeGeneration": "Rythme et mélodie",
                                "TauxApprentissage": "0.01",
                                "NombreEpoch": "200",
                                "NombreDimensionCachee": "512",
                                "NombreLayer": "1",
                                "LongeurSequence": "200",
                                "BatchBool": 'False',
                                "NombreSequenceBatch": "16"}
        
        path = os.listdir(path=os.getcwd() + os.sep + "data")
        if("parametres.csv" in path):
            self.parametres = ImportExportParametres.importFromCSV()


        self.fenetreMenu = Menu.Menu(self, self.parametres)
        self.fenetreLecteur = Lecteur.Lecteur(self, self.parametres)

        self.frame = self.fenetreLecteur


        #Appel de la methode switch_frame qui se situe ci-dessous
        self.switch_frame()



    #Cette méthode permet de supprimer le cadre actuel dans la fenetre principale par frame_class
    def switch_frame(self):
        #on cache la frame actuelle
        self.frame.grid_remove()

        if(self.frame == self.fenetreMenu):
            self.frame = self.fenetreLecteur
            taille = self.tailleLecteur
            self.parametres = self.fenetreMenu.getParametres()
            print(self.parametres)
            self.fenetreLecteur.miseAJourRepertoire(self.parametres)
        else:
            self.frame = self.fenetreMenu
            taille = self.tailleMenu
        
        #Réglage de la taille de la fenêtre
        self.geometry(taille)
        
        #Affectation du cadre à la fenetre

        #Réglage des marges
        self.frame.grid(padx = 20, pady = 15, sticky = "ewsn")


        
####################################################### 

# Récupère les infos relatives à l'écran
def geoliste(g):
    r=[i for i in range(0,len(g)) if not g[i].isdigit()]
    return [int(g[0:r[0]]),int(g[r[0]+1:r[1]]),int(g[r[1]+1:r[2]]),int(g[r[2]+1:])]

# fonctions pour centrer la fenêtre au milieu de l'écran
def centrefenetre(fen):
    fen.update_idletasks()
    l,h,x,y=geoliste(fen.geometry())
    fen.geometry("%dx%d%+d%+d" % (l,h,(fen.winfo_screenwidth()-l)//2,(fen.winfo_screenheight()-h)//2))

##############################################################################################################


def start():
    #instancie la classe Application
    app = Application()
    #Centrage du futur affichage
    centrefenetre(app)
    #Empecher le redimensionnement
    app.resizable(width=False, height=False)
    
    #Pour la netteté de la police de caractères sur Windows
    if(os.name != "posix"):
        windll.shcore.SetProcessDpiAwareness(1)
    

    #Boucle principale de l'interface
    app.mainloop()
