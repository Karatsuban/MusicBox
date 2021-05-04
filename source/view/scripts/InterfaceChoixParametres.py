#coding: utf-8

import tkinter
import tkinter.filedialog
import tkinter.font as tkFont
from tkinter import ttk
from source.view.scripts import InterfaceLecteur
from source.controller import TraitementFichiers, ImportExportParametres
import time
import os

if(os.name != "posix"):
    from ctypes import windll

largeurBout = 15
hauteurBout = 2
margeX = 0
margeY = 0
tailleMenu = "525x775"

#######################################################
#Classe mère de l'interface
#######################################################

class Musique(tkinter.Tk):
    def __init__(self):
        #Initialisation d'une fenetre TKinter
        tkinter.Tk.__init__(self)
        self.frame = None
        #Affectation du titre de la fenêtre
        self.title("Génération musique aléatoire")
        #Réglage de la taille de la fenêtre
        self.geometry(tailleMenu)
        #Réglage du fond en blanc
        self.configure(bg='white')
        #Appel de la methode switch_frame qui se situe ci-dessous
        self.switch_frame(Menu)
        
    #Cette méthode permet de supprimer le cadre actuel dans la fenetre principale par frame_class
    def switch_frame(self, frame_class):
        #On instancie un nouveau cadre
        newFrame = frame_class(self)
        #Si il y a déjà un cadre on le supprime
        if(self.frame is not None):
            self.frame.grid_remove()
        #Affectation du cadre à la fenetre
        self.frame = newFrame
        #Réglage des marges
        self.frame.grid(padx = 20, pady = 15, sticky = "ewsn")
        
#######################################################
#Classe du menu de l'interface
#######################################################

class Menu(tkinter.Frame):
        
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)
        

        #Réglage de la taille de la fenêtre
        self.master.geometry(tailleMenu)
        
        #Réglage police du titre et du texte
        self.titre = tkFont.Font(family='Helvetica', size=20)
        self.texte = tkFont.Font(family='Helvetica', size=13)
        #Réglage police combobox
        master.option_add("*Font", "Helvetica 13")
        #Réglage arrière plan
        self.configure(bg='white')
        
        
        #---------Label------------#
        #Création et placement du titre du cadre
        self.titre1 = tkinter.Label(self, text="Configuration", bg='white', font = self.titre).grid(row=0,column=0)

        #Création de la Zone d'affichage du chemin
        self.entry_text = tkinter.StringVar()
        self.entry_text.set(os.getcwd()+os.sep+"data"+os.sep+"midi")

        

        #Barre de Menu
        self.menubarre = tkinter.Menu(self.master)
        
        self.menuPropos = tkinter.Menu(self.menubarre, tearoff=0)
        self.menuPropos.add_command(label="À propos",command = self.about)
        self.menuPropos.add_command(label="Crédits", command = self.credits)
        self.menubarre.add_cascade(label="À propos", menu = self.menuPropos)
        
        self.master.config(menu = self.menubarre)

        
        #Traitement affichage chemin
        self.affichageChemin = tkinter.StringVar()
        self.affichageChemin.set(self.entry_text.get())
        
        #Placement de la zone et affectation d'un texte dans cette zone d'affichage
        self.usr_input = tkinter.Entry(self, state='readonly', text=self.affichageChemin, width =25)
        self.usr_input .grid(row=1,column=1, sticky="EW")
        
        #Création et placement du Bouton ouvrir dossier
        self.UF = tkinter.Button(self, text="Sélection Dossier", bg = "white", font = self.texte,bd=1,command = lambda:[self.Browser()])
        self.UF.grid(row = 1, column = 0, sticky="W")
        
        #Création et placement du label Nombre de morceaux
        tkinter.Label(self, text="Nombre de morceaux",height = hauteurBout, font = self.texte, bg='white').grid(row = 2, column =0, sticky="W")
        #Création et placement d'une spinbox pour choisir le nombre de morceaux
        self.nbMorceaux = tkinter.Spinbox(self, from_=1, to=20, width=10)
        self.nbMorceaux.grid(row = 2, column =1, sticky="W")
        tkinter.Label(self, text="(1-20)", bg="white").grid(row=2, column=1, sticky="e")
        
        #Création et placement du label Durée de morceaux
        tkinter.Label(self, text="Durée de morceaux",height = hauteurBout,  font = self.texte, bg='white').grid(row = 3, column =0, sticky="W")
        
        #Tonalité de morceaux
        tkinter.Label(self, text="Tonalité de morceaux",height = hauteurBout,  font = self.texte, bg='white').grid(row = 4, column =0, sticky="W")
        #Bouton Tonalite du morceau
        self.tonaliteMorceau = tkinter.Spinbox(self, values = ("A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"), width=10)
        self.tonaliteMorceau.grid(row = 4, column =1, sticky="W")
        
        #bpm des morceaux
        tkinter.Label(self, text="Vitesse des morceaux",height = hauteurBout,  font = self.texte, bg='white').grid(row = 5, column =0, sticky="W")
        #Bouton bpm des morceau
        self.bpmMorceau = tkinter.Spinbox(self, from_=30,to=240, width=10)
        self.bpmMorceau.grid(row = 5, column =1, sticky="W")
        tkinter.Label(self, text="(30-240)", bg="white").grid(row=5, column=1, sticky="e")
        
        #Choix de génération
        tkinter.Label(self, text="Type de génération", width = 15, height = hauteurBout, font = self.texte, bg='white').grid(row = 6, column =0, sticky="W")
                
        #Création du spinbox de durée du morceau
        self.dureeMorceau = tkinter.Spinbox(self, from_=60,to=340, width=10)
        #Placement de la spinbox
        self.dureeMorceau.grid(row = 3, column =1, sticky="W")
        tkinter.Label(self, text="(60-340)", bg="white").grid(row=3, column=1, sticky="e")
        
        #Création et placement du Bouton valider
        self.textBoutonValider = tkinter.StringVar()
        self.textBoutonValider.set("Valider")
        self.Valider = tkinter.Button(self, textvariable=self.textBoutonValider, width = 20, bg="white", font = self.texte, bd=1, command=lambda :[self.charging(master)])
        self.Valider.grid(row=16,column = 1,sticky="E")

        #Création et placement du Bouton Lecteur
        self.textBoutonLecteur = tkinter.StringVar()
        self.textBoutonLecteur.set("Accès direct au lecteur")
        self.Lecteur = tkinter.Button(self, textvariable=self.textBoutonLecteur, bg = "white", font = self.texte, bd = 1, command=lambda :[self.acces_lecteur(master)])
        self.Lecteur.grid(row=16,column =0, sticky="EW")
        
        
        #Création de la combobox de Choix de generation    
        self.comboboite = tkinter.ttk.Combobox(self, values = ["Rythme seulement","Rythme et mélodie"],state="readonly")
        #Réglage de l'item actuel sur 0
        self.comboboite.current(0)
        #Placement
        self.comboboite.grid(row=6, column=1, sticky="W")

        #---------Label------------#
        #Création et placement du titre2
        self.titre2 = tkinter.Label(self, text="Choix avancés", bg='white', font = self.titre).grid(row=7,column=0,sticky="W")
        self.warning = tkinter.Label(self, text="Non recommandé", bg='white', font = self.texte).grid(row=8,column=0,sticky="W")


        #Création et placement du label Taux apprentissage
        varTxApp = tkinter.StringVar(self)
        varTxApp.set("0.01")
        tkinter.Label(self, text="Taux apprentissage",height = hauteurBout, font = self.texte, bg='white').grid(row = 9, column =0, sticky="W")
        #Création et placement d'une spinbox pour choisir le taux d'apprentissage
        self.txApprentissage = tkinter.Spinbox(self, from_=0, to=1, width=10, format='%4.3f', increment=0.001, textvariable=varTxApp, state=tkinter.DISABLED)
        self.txApprentissage.grid(row = 9, column =1, sticky="W")
        tkinter.Label(self, text="(0-1)", bg="white").grid(row=9, column=1, sticky="e")

        #Création et placement du label Nombre d'epoch
        varEpoch = tkinter.StringVar(self)
        varEpoch.set("200")
        tkinter.Label(self, text="Nombre d'Epoch",height = hauteurBout, font = self.texte, bg='white').grid(row = 10, column =0, sticky="W")
        #Création et placement d'une spinbox pour choisir le nombre d'epoch
        self.nbEpoch = tkinter.Spinbox(self, from_=1, to=7000, width=10, textvariable=varEpoch, state=tkinter.DISABLED)
        self.nbEpoch.grid(row = 10, column =1, sticky="W")
        tkinter.Label(self, text="(1-7000)", bg="white").grid(row=10, column=1, sticky="e")

        #Création et placement du label Nombre de dimension cachée
        varDimCach = tkinter.StringVar(self)
        varDimCach.set("512")
        tkinter.Label(self, text="Dimension cachée",height = hauteurBout, font = self.texte, bg='white').grid(row = 11, column =0, sticky="W")
        #Création et placement d'une spinbox pour choisir le nombre de dimension cachée
        self.nbDimCachee = tkinter.Spinbox(self, from_=16, to=2048, width=10, textvariable=varDimCach, state=tkinter.DISABLED)
        self.nbDimCachee.grid(row = 11, column =1, sticky="W")
        tkinter.Label(self, text="(2"+chr(0x2074)+"-2"+chr(0x00B9)+chr(0x00B9)+")", bg="white").grid(row=11, column=1, sticky="e")

        #Création et placement du label Nombre de layer
        varNbLayer = tkinter.StringVar(self)
        varNbLayer.set("1")
        tkinter.Label(self, text="Nombre de layer",height = hauteurBout, font = self.texte, bg='white').grid(row = 12, column =0, sticky="W")
        #Création et placement d'une spinbox pour choisir le nombre de layer
        self.nbLayer = tkinter.Spinbox(self, from_=1, to=5, width=10, textvariable=varNbLayer, state=tkinter.DISABLED)
        self.nbLayer.grid(row = 12, column =1, sticky="W")
        tkinter.Label(self, text="(1-5)", bg="white").grid(row=12, column=1, sticky="e")

        #Création et placement du label Longueur de sequence
        varLgSeq = tkinter.StringVar(self)
        varLgSeq.set("200")
        tkinter.Label(self, text="Longueur séquence",height = hauteurBout, font = self.texte, bg='white').grid(row = 13, column =0, sticky="W")
        #Création et placement d'une spinbox pour choisir la Longueur de sequence
        self.lgSeq = tkinter.Spinbox(self, from_=1, to=2000, width=10, textvariable=varLgSeq, state=tkinter.DISABLED)
        self.lgSeq.grid(row = 13, column =1, sticky="W")
        tkinter.Label(self, text="(1-2000)", bg="white").grid(row=13, column=1, sticky="e")

        #utilisation batch
        tkinter.Label(self, text="Utiliser batch",height = hauteurBout,  font = self.texte, bg='white').grid(row = 14, column =0, sticky="W")
        #Bouton utilisation du batch
        self.boolBatch = tkinter.ttk.Combobox(self, values = ["True","False"],state=tkinter.DISABLED)
        #Réglage de l'item actuel sur 0
        self.boolBatch.current(0)
        self.boolBatch.grid(row = 14, column =1, sticky="W")

        #Création et placement du label Nombre de sequence par batch
        varSeqBa = tkinter.StringVar(self)
        varSeqBa.set("16")
        tkinter.Label(self, text="Séquence/batch",height = hauteurBout, font = self.texte, bg='white').grid(row = 15, column =0, sticky="W")
        #Création et placement d'une spinbox pour choisir le nombre de seq du batch
        self.nbSeqBatch = tkinter.Spinbox(self, from_=1, to=512, width=10, textvariable=varSeqBa, state=tkinter.DISABLED)
        self.nbSeqBatch.grid(row = 15, column =1, sticky="W")
        tkinter.Label(self, text="(2"+chr(0x2070)+"-2"+chr(0x2079)+")", bg="white").grid(row=15, column=1, sticky="e")
        
        #button to enable choix avancés
        self.varButton = 0
        self.buttonA = tkinter.Button(self, text="Activer les paramètres avancés", width = 30, bg="white", command=lambda:[self.changeInterface()])
        self.buttonA.grid(row=8,column=1,sticky="W")


    def changeInterface(self):
        if (self.varButton == 0):
          self.varButton = 1
          self.buttonA.config(text="Désactiver les paramètres avancés")
          #enable everyone
          self.txApprentissage["state"]=tkinter.NORMAL
          self.nbEpoch["state"]=tkinter.NORMAL
          self.nbDimCachee["state"]=tkinter.NORMAL
          self.nbLayer["state"]=tkinter.NORMAL
          self.lgSeq["state"]=tkinter.NORMAL
          self.boolBatch["state"]="readonly"
          self.nbSeqBatch["state"]=tkinter.NORMAL
        elif (self.varButton == 1):
          self.varButton = 0
          self.buttonA.config(text="Activer les paramètres avancés")
          #disable everyone
          self.txApprentissage["state"]=tkinter.DISABLED
          self.nbEpoch["state"]=tkinter.DISABLED
          self.nbDimCachee["state"]=tkinter.DISABLED
          self.nbLayer["state"]=tkinter.DISABLED
          self.lgSeq["state"]=tkinter.DISABLED
          self.boolBatch["state"]=tkinter.DISABLED
          self.nbSeqBatch["state"]=tkinter.DISABLED




    def traitementAffichage(self, chemin, taille):
        if len(chemin) > taille:
            cheminCoupe = chemin[-(len(chemin)-taille):]
            return cheminCoupe
        else:
            return chemin
    
    def valide(self):
        valide = True
        if(int(self.nbMorceaux.get())>20 or int(self.nbMorceaux.get())<1):
            valide = False
        if(int(self.dureeMorceau.get())<60 or int(self.dureeMorceau.get())>340) :
            valide = False
        if(int(self.bpmMorceau.get()) <30 or int(self.bpmMorceau.get())>240) :
            valide=False
        if(not valide):
            self.popupmsg()
        return valide

    def popupmsg(self):
        popup = tkinter.Tk()
        centrefenetre(popup)
        popup.title("Erreur")
        popup.config(bg="white")
        label = tkinter.Label(popup, text="Attention : Le nombre de morceaux, ou \nla durée, ou les bpm est incorrect", bg="white")
        popup.geometry("315x120")
        label.pack(side="top", fill="x", pady=10)
        ok = tkinter.Button(popup, text="Ok", bg="white", command = popup.destroy, width=10)
        ok.pack()

    def charging(self, master):
        if(self.valide()):
            self.textBoutonValider.set("En chargement...")
            self.export()
            TraitementFichiers.main()
            self.textBoutonValider.set("Valider")
            master.switch_frame(InterfaceLecteur.Lecteur)
        return

    def acces_lecteur(self, master):
        master.switch_frame(InterfaceLecteur.Lecteur)
        

    def export(self):
    
        self.parametres =     {"URL_Dossier": self.entry_text.get(),
                        "NombreMorceaux": self.nbMorceaux.get(),
                        "DureeMorceaux": self.dureeMorceau.get(),
                         "TonaliteMorceaux": self.tonaliteMorceau.get(),
                         "VitesseMorceaux": self.bpmMorceau.get(),
                        "TypeGeneration":self.comboboite.get(),
                        "TauxApprentissage": self.txApprentissage.get(),
                        "NombreEpoch": self.nbEpoch.get(),
                        "NombreDimensionCachee": self.nbDimCachee.get(),
                        "NombreLayer": self.nbLayer.get(),
                        "LongeurSequence": self.lgSeq.get(),
                        "BatchBool": self.boolBatch.get(),
                        "NombreSequenceBatch": self.nbSeqBatch.get()}
        ImportExportParametres.exportInCSV(self.parametres)
        return
    
        
    #Méthode pour l'explorateur de fichier
    def Browser(self):
        filename = tkinter.filedialog.askdirectory().replace("/", os.sep)
        print("Selected Filename is "+filename)
        self.affichageChemin.set(self.traitementAffichage(filename,20))
        self.entry_text.set(filename)


    def credits(self):
        pageCredit = tkinter.Tk()
        pageCredit.geometry("200x155")
        pageCredit.resizable(False, False)
        pageCredit.config(bg='white')
        pageCredit.title("Credits")
        centrefenetre(pageCredit)
        texte = "Créé par:\nAntoine Escriva\nFlorian Bossard\nClément Guérin\nRaphaël Garnier\nClément Bruschini"
        tkinter.Message(pageCredit, text=texte, bg="white", relief = tkinter.RAISED, anchor = 'w', width =200).pack(fill = tkinter.X)
        tkinter.Button(pageCredit,text="Ok", width=10,bg="white",command= pageCredit.destroy).pack(fill = tkinter.X)
    
    def about(self):
        pageAbout = tkinter.Tk()
        pageAbout.geometry("450x100")
        pageAbout.resizable(False, False)
        pageAbout.config(bg='white')
        pageAbout.title("À propos")
        centrefenetre(pageAbout)
        text = "Application développée dans le cadre de la matière Conduite et gestion de projet en 2ème année du cycle Ingénieur à Sup Galilée.\nVersion 1.0, 2021"
        tkinter.Message(pageAbout, text=text, bg="white", relief = tkinter.RAISED, width=450).pack(fill = tkinter.X)
        tkinter.Button(pageAbout,text="Ok", bg="white",command= pageAbout.destroy, width=10).pack(fill = tkinter.X)
        
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
    #instancie la classe Musique
    app = Musique()
    #Centrage du futur affichage
    centrefenetre(app)
    #Empecher le redimensionnement
    app.resizable(width=False, height=False)
    
    #Pour la netteté de la police de caractères sur Windows
    if(os.name != "posix"):
        windll.shcore.SetProcessDpiAwareness(1)
    

    #Boucle principale de l'interface
    app.mainloop()
