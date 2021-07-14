# coding:utf-8

from source.controller import TraitementFichiers, ImportExportParametres
import os
import queue
import Install


class OneLineClient:

    def __init__(self, args):
        self.args = args
        self.is_model = False
        self.parametres = None
        self.parametres_infos = None
        self.list_param = None
        self.user_param = None
        self.dico_formats = {'Melodie': {'NomFormat': 'Melodie', 'NombreElements': '4', 'FracNote': '0', 'FusionPiste': '1', 'EncodeSilences': '0', 'DecoupeMesure': '10',
                                         'ListeTypesElements': "['IIN', 'TN', 'TN', 'PM']"},
                             'Rythme': {'NomFormat': 'Rythme', 'NombreElements': '1', 'FracNote': '0', 'FusionPiste': '1', 'EncodeSilences': '1', 'DecoupeMesure': '20',
                                        'ListeTypesElements': "['TN']"}
                             }  # formats disponibles par défaut
        self.format_liste = None  # nom des formats
        self.update_formats()  # mise à jour des formats existants depuis le fichier de sauvegarde des formats

        self.initParams()  # on initialise les parametres

        if self.parse_param():  # si les paramètres sont corrects
            self.launch()  # on appelle la fonction
        return

    def initParams(self):
        # initialise les paramètres avec les valeurs par défaut
        self.parametres = {
            "URL_Dossier": os.getcwd() + os.sep + "data" + os.sep + "midi",
            "NombreMorceaux": "2",
            "DureeMorceaux": "30",
            "TonaliteMorceaux": "A",
            "VitesseMorceaux": "30",
            "TypeGeneration": self.format_liste[0],
            "TauxApprentissage": "0.01",
            "NombreEpoch": "200",
            "NombreDimensionCachee": "128",
            "NombreLayer": "1",
            "NombreSequenceBatch": "16",
            "ChoixAffichageDataInfo": 0
        }  # dictionnaire des paramètres, créé par défaut

        self.parametres_infos = {
            "URL_Dossier": ["DIR_PATH"],
            "NombreMorceaux": ["INT", 1, 200],
            "DureeMorceaux": ["INT", 5, 1000],
            "TonaliteMorceaux": ["LIST", ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]],
            "VitesseMorceaux": ["INT", 1, 360],
            "TypeGeneration": ["LIST", self.format_liste],
            "TauxApprentissage": ["FLOAT", 0, 1],
            "NombreEpoch": ["INT", 1, 1000000],
            "NombreDimensionCachee": ["INT", 16, 2048],
            "NombreLayer": ["INT", 1, 5],
            "NombreSequenceBatch": ["INT", 1, 512],
            "ChoixAffichageDataInfo": ["INT", 0, 1],
            "SavePath": ["STRING"],
            "LoadPath": ["FILE_PATH"],
            "generate": ["BOOL"],
            "help": ["BOOL"],
            "graph": ["BOOL"],
            "stat": ["BOOL"],
            "params": ["BOOL"],
            "update": ["BOOL"]
        }  # dictionnaire des types, limites/valeurs possibles par paramètre

        self.user_param = {
            "Save": False,
            "SavePath": "",
            "Load": False,
            "LoadPath": "",
            "generate": False,
            "help": False,
            "graph": False,
            "stat": False,
            "params": False,
            "update": False,
        }  # paramètres de sauvegarde, chargement, generation de morceaux, graphes et/ou statistiques, statistiques, parametres, aide et mise à jour
        return

    def parse_param(self):
        # parcourt les parametres entres par l'utilisateur et enregistre les valeurs dans les bons parametres
        for param in ["help", "stat", "graph", "generate", "params", "update"]:
            if param in self.args:
                self.args[self.args.index(param)] = param+"=True"  # les paramètres qui ne prennent pas de valeurs sont mis à True

        param_input = [a.split("=") for a in self.args]  # séparation des arguments et de leur valeurs

        for nom_val in param_input:  # pour chaque couple nom_param et val_param
            if len(nom_val) != 2:  # si on a pas de couple, on ne va pas plus loin
                print("Erreur : parametre {} incomprehensible".format(nom_val))
                return False
            nom, value = nom_val
            if nom in self.parametres.keys():  # si le paramètre existe bien
                valide, value = self.verif_one_param(nom, value)  # on vérifie sa validité et on récupère la valeur au bon type
                if valide:  # si le parametre est valide
                    self.parametres[nom] = value  # on l'enregistre
                else:
                    return False  # sinon, on arrête tout
            elif nom in self.user_param.keys():  # le parametre existe
                valide, value = self.verif_one_param(nom, value)
                if valide:
                    self.user_param[nom] = value
                else:
                    return False  # paramètre non valide
            else:
                print("Parametre {} inconnu".format(nom_val))  # parametre non existant

        self.user_param["Save"] = self.user_param["SavePath"] != ""  # si le chemin n'est pas vide, on va sauvegarder le modèle
        self.user_param["Load"] = self.user_param["LoadPath"] != ""  # idem pour le chargement

        self.parametres["ChoixAffichageStatistiques"] = int(self.user_param["stat"])  # on intègre le choix de l'utilisateur pour les graphes et les stats
        self.parametres["ChoixAffichageGraphiques"] = int(self.user_param["graph"])

        return True

    def verif_one_param(self, name, value):
        # vérifie que la valeur associée au paramètre de nom "name" est valide
        valide = False
        param_type = self.parametres_infos[name][0]
        infos = self.parametres_infos[name][1:]  # on récupère les infos dans le dico associé

        if param_type == "INT":
            value = eval(value)
            if infos[0] <= value <= infos[1]:
                valide = True
            else:
                print("Erreur parametre {} : la valeur doit etre un entier entre {} et {}".format(name, infos[0], infos[1]))

        elif param_type == "FLOAT":
            value = eval(value)
            if infos[0] <= value <= infos[1]:
                valide = True
            else:
                print("Erreur parametre {} : la valeur doit etre un flottant entre {} et {}".format(name, infos[0], infos[1]))

        elif param_type == "LIST":
            if value in infos[0]:
                valide = True
            else:
                print("Erreur parametre {} : la valeur doit etre une des suivantes {}".format(name, infos[0]))

        elif param_type == "DIR_PATH":
            if os.path.isdir(value):  # si le chemin existe bien et décrit bien un dossier
                valide = True
            else:
                print("Erreur parametre {} : le dossier \"{}\" n'existe pas".format(name, value))

        elif param_type == "FILE_PATH":
            if os.path.isfile(value):
                valide = True
            else:
                print("Erreur parametre {} : le fichier \"{}\" n'existe pas".format(name, value))

        elif param_type == "BOOL":
            if value in ["True", "False"]:
                valide = True
            value = eval(value)

        elif param_type == "STRING":
            valide = True

        return valide, value  # on renvoie la validité et la valeur dans le bon type

    def displayParams(self):
        # affiche les tous les paramètres de génération et du modèle
        print("\nPARAMETRES UTILISES")
        print("-------------------------------------------------")
        for ind, val in self.parametres.items():
            print(ind, " : ", val)
        print("-------------------------------------------------\n")
        return

    def lance_train(self):
        # appelle la fonction de lancement de l'entraînement
        queue_1 = queue.Queue()
        queue_fin = queue.Queue()
        type_gen = self.parametres["TypeGeneration"]
        format_infos = self.dico_formats[type_gen]
        TraitementFichiers.train(self.parametres, self.is_model, queue_1, queue_fin, format_infos)
        print()
        return

    def saveModel(self):
        # permet de sauvegarder le modèle
        modelSavePath = self.user_param["SavePath"]
        if ".tar" not in modelSavePath:
            modelSavePath += ".tar"
        TraitementFichiers.saveModel(modelSavePath)
        print("Modele enregistré sous : {}".format(modelSavePath))
        return

    def loadModel(self):
        # permet de charger un modèle
        load_parametres = self.getParametres()
        modelLoadPath = self.user_param["LoadPath"]
        if ".tar" not in modelLoadPath:
            modelLoadPath += ".tar"
        TraitementFichiers.loadModel(modelLoadPath, load_parametres, self.dico_formats)
        print("Chargement du modèle effectue\n")
        self.is_model = True
        return

    def genererMorceau(self):
        # permet de générer des morceaux
        TraitementFichiers.genereMorceaux(self.parametres)
        print("Les fichiers midi ont ete generes !\n")
        return

    def getParametres(self):
        # renvoie les paramètres
        return self.parametres

    def launch(self):
        # effectue toutes les actions demandées par l'utilisateur
        if self.user_param["update"]:
            print("HERE")
            Install.installByOS("LineClient")  # vérifie l'installation

        if self.user_param["help"]:
            self.display_help()  # affiche l'aide
            return

        if self.user_param["params"]:
            self.displayParams()  # affiche les parametres

        if self.user_param["Load"]:
            self.loadModel()  # charge un modèle

        self.lance_train()  # lance l'entraînement

        if self.user_param["Save"]:
            self.saveModel()  # sauvegarde le modèle

        if self.user_param["generate"]:
            self.genererMorceau()  # génère des morceaux
        return

    def update_formats(self):
        # met à jour la liste et les informations sur les formats en lisant le fichier de sauvegarde des formats
        new_formats = ImportExportParametres.importFormat()  # récupération des formats
        if new_formats is not None:  # si d'autres formats que ceux de base ont été chargés
            for a in new_formats:
                self.dico_formats[a] = new_formats[a]  # on ajoute les nouveaux formats
        self.format_liste = [key for key, _ in self.dico_formats.items()]  # on récupère les noms des nouveaux formats
        return

    def display_help(self):
        # affiche l'aide
        print("\nAIDE\n"
              "Nom parametre\t\tType\t\tValeurs\n"
              "-----------------------------------------------------------\n"
              "URL_Dossier\t\tString\t\tLe dossier doit contenir des fichiers .mid\n"
              "NombreMorceaux\t\tInt\t\tValeur dans [1, 200]\n"
              "DureeMorceaux\t\tInt\t\tValeur dans [5, 1000] \n"
              "TypeGeneration\t\tString\t\tValeur dans", self.format_liste, "\n"
              "TauxApprentissage\tFloat\t\tValeur dans ]0:1[ \n"
              "NombreEpoch\t\tInt\t\tValeur dans [1, 1000000]\n"
              "NombreDimensionCachee\tInt\t\tValeur dans [2^4:2^11], multiple de 2 de preference.\n"
              "NombreLayer\t\tInt\t\tValeur dans [1, 5]\n"
              "NombreSequenceBatch\tInt\t\tValeur dans [1:2^9], multiple de 2 de preference\n"
              "SavePath\t\tString\t\tChemin absolu valide de sauvegarde du modele\n"
              "LoadPath\t\tString\t\tChemin absolu valide de chargment du modele\n"
              "generate\t\t\t\tPour generer des morceaux dans le dossier Résultat après entrainement\n"
              "graph\t\t\t\t\tPour generer des graphiques bases sur les donnees d'entrainement\n"
              "stat\t\t\t\t\tPour afficher des statistiques sur les donnees d'entrainement\n"
              "params\t\t\t\t\tPour afficher les parametres\n"
              "help\t\t\t\t\tPour afficher cette aide\n"
              "update\t\t\t\t\tPour verifier l'installation des packages"
              "-----------------------------------------------------------\n")
        return


def verifMIDI(path):
    # Vérification de la présence de fichiers .mid dans le dossier
    files = [file for file in os.listdir(path) if ".mid" in file]  # liste des fichiers .mid dans le dossier choisi
    return len(files) != 0  # True si la liste n'est pas vide


def start(args):
    # instancie le client
    print("Client lancé")
    OneLineClient(args)
    return
