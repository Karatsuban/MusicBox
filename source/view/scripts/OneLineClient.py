import sys
from source.controller import TraitementFichiers
import os
import queue


class LineClient:

    def __init__(self):
        self.is_model = False
        self.parametres = None
        self.parametres_infos = None
        self.list_param = None
        self.initParams()  # on initialise les parametres
        self.get_user_param()  # on recupere les parametre rentree

    def initParams(self):
        self.parametres = {
            "URL_Dossier": os.getcwd() + os.sep + "data" + os.sep + "midi",
            "NombreMorceaux": "2",
            "DureeMorceaux": "30",
            "TonaliteMorceaux": "A",
            "VitesseMorceaux": "30",
            "TypeGeneration": "Melodie",
            "TauxApprentissage": "0.01",
            "NombreEpoch": "200",
            "NombreDimensionCachee": "128",
            "NombreLayer": "1",
            "NombreSequenceBatch": "16",
            "ChoixAffichageDataInfo": 0
        }

        self.parametres_infos = {
            "URL_Dossier": ["URL"],
            "NombreMorceaux": ["INT", 1, 200],
            "DureeMorceaux": ["INT", 5, 1000],
            "TonaliteMorceaux": ["LIST", ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]],
            "VitesseMorceaux": ["INT", 1, 360],
            "TypeGeneration": ["LIST", ["Melodie", "Rythme", "Melodie_ttt", "Melodie_saut"]],
            "TauxApprentissage": ["FLOAT", 0, 1],
            "NombreEpoch": ["INT", 1, 1000000],
            "NombreDimensionCachee": ["INT", 16, 2048],
            "NombreLayer": ["INT", 1, 5],
            "NombreSequenceBatch": ["INT", 1, 512],
            "ChoixAffichageDataInfo": ["INT", 0, 1],
            "Save": ["2PARAM"],
            "Load": ["2PARAM"],
            "AffParam": ["INT", 0, 1],
            "Create": ["INT", 0, 1],
            "Man": ["INT", 0, 1],
        }

        self.user_param = {
            "Save": "0, nom",
            "Load": "0, nom",
            "AffParam": "0",
            "Create": "0",
            "Man": "0",
        }

    def get_user_param(self):
        param_input = sys.argv[1:len(sys.argv)]  # on ne prends pas le 1er arg, car c'est le nom du script
        for i in range(len(param_input)):
            for j in range(len(param_input[i])):
                if param_input[i][j] == "=":
                    self.user_param[param_input[i][:j]] = param_input[i][j + 1:]
        for k,v in self.user_param.items():
            if k in self.parametres:
                self.parametres[k] = self.user_param[k]

    def verif_param(self):
        for ind, val in self.user_param.items():
            valide = False
            while not valide:
                infos = self.parametres_infos[ind]  # on récupère les infos dans le dico associé
                if infos[0] == "INT":
                    val = int(float(val))
                    if infos[1] <= val <= infos[2]:
                        valide = True
                    else:
                        print("Erreur : la valeur entree doit etre un entier entre {} et {}".format(infos[1], infos[2]))
                        return
                elif infos[0] == "FLOAT":
                    val = float(val)
                    if infos[1] <= val <= infos[2]:
                        valide = True
                    else:
                        print("Erreur : la valeur entree doit etre un flottant entre {} et {}".format(infos[1], infos[2]))
                        return
                elif infos[0] == "LIST":
                    if val in infos[1]:
                        valide = True
                    else:
                        print("Erreur : le parametre attendu doit etre un des suivants {}".format(infos[1]))
                        return
                elif infos[0] == "URL":
                    if os.path.isdir(val):  # si le chemin existe bel et bien
                        if verifMIDI(val):
                            valide = True
                        else:
                            print("Erreur : Il n'y a pas de fichiers MIDI dans le repertoire choisi !")
                            return
                    else:
                        print("Erreur : le chemin n'existe pas")
                        return

                elif infos[0] == "2PARAM":
                    val = val.split(",")
                    if val[0] == "0" or val[0] == "1":
                        if 0 < len(val[1]) <= 50:
                            valide = True
                        else:
                            print("Erreur, nom est trop court ou trop long")
                            return
                    else:
                        print("Erreur, le premier parametre pour Save ou Load doit etre 1 ou 0")
                        return
        return valide

    def displayParams(self):
        for ind, val in self.parametres.items():
            print(ind, " : ", val)
        print()
        print("=================================== sep line ===================================")
        return

    def charging(self):
        queue_1 = queue.Queue()
        queue_fin = queue.Queue()
        TraitementFichiers.train(self.parametres, self.is_model, queue_1, queue_fin)
        print("=================================== sep line ===================================")
        return

    def saveModel(self, nom):
        if ".tar" in nom:
            savePath = self.parametres["URL_Dossier"] + os.sep + "Modèles save" + os.sep + nom
        else:
            savePath = self.parametres["URL_Dossier"] + os.sep + "Modèles save" + os.sep + nom + ".tar"
        TraitementFichiers.saveModel(savePath)
        print("Modele enregistré sous: ", savePath)
        print("=================================== sep line ===================================")
        return

    def loadModel(self, nom):
        try:
            loadPath = self.parametres["URL_Dossier"] + os.sep + "Modèles save"
            load_parametres = self.getParametres()

            if ".tar" in nom:
                loadFile = loadPath + os.sep + nom
            else:
                loadFile = loadPath + os.sep + nom + ".tar"

            TraitementFichiers.loadModel(loadFile, load_parametres)
            print("Chargement du modèle éfféctué")
            self.is_model = True
        except IOError:
            print("Load failed, Vous n'avez pas rentré de chemin ou chemin est incorrect!")

        print("=================================== sep line ===================================")
        return

    def genererMorceau(self):
        TraitementFichiers.genereMorceaux(self.parametres)
        print("Les fichiers midi ont été générer !")
        print("=================================== sep line ===================================")
        return

    def getParametres(self):
        return self.parametres

    def manuel(self):
        tuto = ("\n\nSi vous ne rentrez pas certains paramètres, ils vont être par défaut.\n"
                "-----------------------------------------------------------\n"
                "Les paramettres possible : \n"               
                "URL_Dossier  /--URL doit contenir des fichiers .mid--\n" 
                "NombreMorceaux  /--ne soit pas trop grand plz--\n"
                "DureeMorceaux  /--comme l'info du précédent ψ(._. )>--\n"
                "TypeGeneration /--Rythme ou Melodie--\n"
                "TauxApprentissage  /--Attention lr entre ]0:1[ --\n"
                "NombreEpoch  /--Si trop = trop de temps, à vous de voir, pour l'instant le max est 1000000! pas mal nn?(*/ω＼*)\n"
                "NombreDimensionCachee  /--Entre [2^4:2^11]--\n"
                "NombreLayer  /--Entre 1-5--\n"
                "NombreSequenceBatch  /--Entre [1:2^9]--\n"
                "ChoixAffichageDataInfo  /--1 pour afficher les detaills sur la base, 0 pour vous avez compris (￣y▽￣)╭ Ohohoho.....\n"
                "Save  /--1 pour Save après entrainement. Exemple: Save=1, nom du modele--\n"
                "Load  /--1 pour load le modele que vous avez saved avant, dès le début. Exemple: load=1, nom du modele--\n"
                "AffParam  /--1 pour afficher les paramettre avant l'entrainement--\n"
                "Create  /--1 pour générer des morceaux dans le dossier Résultat du URL après entrainement--\n"
                "-----------------------------------------------------------\n"
                "L'ordre de fonctionnement: \n "
                "Load? -> Print Param? -> Entrainement -> Save? -> Create? -> Fin\n"
                "-----------------------------------------------------------")

        print(tuto)

    def trainning(self):
        load = self.user_param["Load"].replace(" ", "").split(",")
        save = self.user_param["Save"].replace(" ", "").split(",")
        Valide = self.verif_param()
        if Valide:
            if int(self.user_param["Man"]):
                self.manuel()
                return
            if int(load[0]):
                self.loadModel(load[1])
            if int(self.user_param["AffParam"]):
                self.displayParams()
            self.charging()
            if int(save[0]):
                self.saveModel(save[1])
            if int(self.user_param["Create"]):
                self.genererMorceau()
        return


# Verifier si fichiers .mid existe dans le dossier choisi.
def verifMIDI(path):
    files = os.listdir(path)
    for k in range(len(files)):
        files[k] = os.path.splitext(files[k])[1]
    extention = '.mid'
    return extention in files


def start():
    client = LineClient()
    print("Client lancé")
    client.trainning()
