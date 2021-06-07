# coding:utf-8

from source.controller import TraitementFichiers, ImportExportParametres
import datetime
import os
import queue


class LineClient:

    def __init__(self):
        self.parametres = None
        self.parametres_infos = None
        self.is_model = False  # aucun modèle n'a été créé ou chargé

        self.initParams()  # on initialise les parametres

    def initParams(self):
        self.parametres = {"URL_Dossier": os.getcwd() + os.sep + "data" + os.sep + "midi",
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

        self.parametres_infos = {"URL_Dossier": ["URL"],
                                 "NombreMorceaux": ["INT", 1, 200],
                                 "DureeMorceaux": ["INT", 5, 1000],
                                 "TonaliteMorceaux": ["LIST", ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]],
                                 "VitesseMorceaux": ["INT", 1, 360],
                                 "TypeGeneration": ["LIST", ["Rythme et mélodie", "Rythme seulement"]],
                                 "TauxApprentissage": ["FLOAT", 0, 1],
                                 "NombreEpoch": ["INT", 1, 1000000],
                                 "NombreDimensionCachee": ["INT", 16, 2048],
                                 "NombreLayer": ["INT", 1, 5],
                                 "NombreSequenceBatch": ["INT", 1, 512]}

    def menuPrincipal(self):
        fin = False
        while not fin:
            valide = False
            choice = ""
            while not valide:
                print("-- Menu principal --")
                print("1 - Menu modele")
                print("2 - Menu parametres")
                print("3 - Entrainer")
                print("4 - Generer morceaux")
                print("5 - Credits")
                print("6 - Quitter")
                choice = input()
                if choice in "123456" and len(choice) == 1 and choice != "":
                    valide = True
            choice = int(choice)
            if choice == 1:
                self.menuModel()
            elif choice == 2:
                self.menuParams()
            elif choice == 3:
                self.charging()
            elif choice == 4:
                self.genererNewMorceau()
            elif choice == 5:
                credits()
            elif choice == 6:
                fin = True
        return

    def menuModel(self):
        fin = False
        while not fin:
            valide = False
            choice = ""
            while not valide:
                print("-- Menu modele --")
                print("1 - Charger modele")
                print("2 - Sauvegarder modele")
                print("3 - Nouveau modele")
                print("4 - Retour")
                choice = input()
                if choice in "1234" and len(choice) == 1 and choice != "":
                    valide = True
            choice = int(choice)
            if choice == 1:
                self.loadModel()
            elif choice == 2:
                self.saveModel()
            elif choice == 3:
                self.newModel()
            elif choice == 4:
                fin = True
        return

    def menuParams(self):
        fin = False
        while not fin:
            valide = False
            choice = ""
            while not valide:
                print("-- Menu parametres --")
                print("1 - Afficher parametres")
                print("2 - Modifier parametres")
                print("3 - Retour")
                choice = input()
                if choice in "123" and len(choice) == 1 and choice != "":
                    valide = True
            choice = int(choice)
            if choice == 1:
                self.displayParams()
            elif choice == 2:
                self.modifyParams()
            elif choice == 3:
                fin = True
        return

    def modifyParams(self):
        print("Dans modifyParams")
        print("Pour chaque parametre, entrez une valeur ou Entree pour passer a la suivante")
        for ind, val in self.parametres.items():
            valide = False
            while not valide:
                print(ind, val, end="  ")
                value = input()
                if value != "":
                    infos = self.parametres_infos[ind]  # on récupère les infos dans le dico associé
                    if infos[0] == "INT":
                        value = int(float(value))
                        if infos[1] <= value <= infos[2]:
                            valide = True
                        else:
                            print("Erreur : la valeur entree doit etre un entier entre {} et {}".format(infos[1], infos[2]))
                    elif infos[0] == "FLOAT":
                        value = float(value)
                        if infos[1] <= value <= infos[2]:
                            valide = True
                        else:
                            print("Erreur : la valeur entree doit etre un flottant entre {} et {}".format(infos[1], infos[2]))
                    elif infos[0] == "LIST":
                        if value in infos[1]:
                            valide = True
                        else:
                            print("Erreur : le parametre attendu doit etre un des suivants {}".format(infos[1]))
                    if valide:
                        self.parametres[ind] = value
                else:
                    valide = True
        return

    def displayParams(self):
        for ind, val in self.parametres.items():
            print(ind, " : ", val)
        print()
        return

    def charging(self):
        print("Dans charging")
        queue_1 = queue.Queue()
        queue_fin = queue.Queue()
        TraitementFichiers.train(self.parametres, self.is_model, queue_1, queue_fin)
        self.is_model = True
        return

    def newModel(self):
        temp = getDate()
        if self.is_model:
            choice = askyesnocancelSave()
            if choice is not "CANCEL":
                if choice == "YES":
                    savePath = askSavePath()
                    TraitementFichiers.saveModel(savePath)
                self.is_model = False
                self.initParams()  # on re-initialise les parametres
        return

    def saveModel(self):
        print("Dans saveModel")
        temp = "Model " + getDate()
        if not self.is_model:
            print("Il n'y a pas de modele en cours d'utilisation !")
        else:
            savePath = askSavePath()
            if savePath != "":
                if ".tar" not in savePath:
                    savePath += ".tar"
                TraitementFichiers.saveModel(savePath)
                print("Modele enregistré")
        return

    def loadModel(self):
        temp = "Model " + getDate()
        print("Dans loadModel")
        choice = ""
        if self.is_model:  # si un modèle est déjà en cours
            print("Nom conseille : ", temp)
            choice = askyesnocancelSave()  # on récupère ce que choisit l'utilisateur
            if choice == "YES":
                savePath = askSavePath()
                if ".tar" not in savePath:
                    savePath += ".tar"
                TraitementFichiers.saveModel(savePath)

        if choice is not "CANCEL":
            loadPath = askLoadPath()
            user_parametres = self.getParametres()
            TraitementFichiers.loadModel(loadPath, user_parametres)
            self.is_model = True
            print("Chargement du modele effectue")
        return

    def Browser(self):
        valide = False
        path = ""
        while not valide:
            path = input("Entrez le nouveau chemin : ")
            if path == "":
                print("Chemin non modifie")
                path = self.parametres["URL_Dossier"]
            if not self.verifMidi(path):
                print("Erreur : Il n'y a pas de fichiers MIDI dans le repertoire choisi !")
            else:
                valide = True
        return path

    def genererNewMorceau(self):
        if self.is_model:
            TraitementFichiers.genereNew(self.parametres)
            print("Les fichiers ont ete generes !")
        else:
            print("Aucun modele n'est en cours d'utilisation !")
        return

    def exportParametres(self):
        ImportExportParametres.exportInCSV(self.parametres)

    def getParametres(self):
        return self.parametres


# Verifier si fichiers .mid existe dans le dossier choisi.
def verifMIDI(path):
    files = os.listdir(path)
    print(files)
    for k in range(len(files)):
        files[k] = os.path.splitext(files[k])[1]
    print(files)
    extention = '.mid'
    if extention in files:
        return True
    else:
        return False


def askyesnocancelSave():
    valide = False
    choice = ""
    while not valide:
        print("Un modele est déjà en cours d'utilisation, voulez-vous le sauvegarder ? ")
        print("1 - Oui")
        print("2 - Non")
        print("3 - Annuler")
        choice = input()
        if choice in "123" and len(choice) == 1 and choice != "":
            valide = True
        choice = int(choice)
    if choice == 1:
        return "YES"
    elif choice == 2:
        return "NO"
    else:
        return "CANCEL"


def askSavePath():
    choice = input("Entrez le chemin complet où sera sauvegarde le modele : ")
    return choice


def askLoadPath():
    choice = input("Entrez le chemin complet d'où sera charge le modele : ")
    return choice


def getDate():
    date = datetime.datetime.now()
    dateG = datetime.date(date.year, date.month, date.day)
    dg = dateG.isoformat()
    heureG = datetime.time(date.hour, date.minute, date.second)
    hg = heureG.strftime('%H-%M-%S')
    temp = "_".join([dg, hg])
    return temp


def credits():
    print("Application créée par:\nAntoine Escriva\nFlorian Bossard\nClément Guérin\nRaphaël Garnier\nClément Bruschini\n\nRepris par:\nYunfei Jia\nRaphaël Garnier")
    print("Application développée dans le cadre de la matière Conduite et gestion de projet en 2ème année du cycle Ingénieur à Sup Galilée.\nApplication poursuivie en stage du 03/05/2021 au 02/07/21\nVersion 1.5, 2021")
    print("https://github.com/Karatsuban/MusicBox\n")


def start():
    client = LineClient()
    print("Client lancé")
    client.menuPrincipal()
