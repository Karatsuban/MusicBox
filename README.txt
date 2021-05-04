
     ; 			||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||		     ;	
     ;;			||||||                                                               |||||||		     ;;
     ;';.		||||||   PROJET DE GENERATION ALEATOIRE DE MUSIQUE A PARTIR DE RNN   |||||||		     ;';.
     ;  ;;		||||||                                                               |||||||                 ;  ;;
     ;   ;;		||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||                 ;   ;;
     ;    ;;		||||||    Authors :                       Clients :                  |||||||                 ;    ;;
     ;    ;;		||||||        GUERIN CLEMENT                  BODINI OLIVIER         |||||||                 ;    ;;
     ;   ;'		||||||        GARNIER RAPHAEL                 TOMEH NADI             |||||||                 ;   ;'
     ;  ' 		||||||        ESCRIVA ANTOINE                                        |||||||		     ;  ' 
,;;;,; 			||||||        BRUSCHINI CLEMENT           Version :                  |||||||		,;;;,;
;;;;;;			||||||        BOSSARD FLORIAN                 v1.0 - 12/04/21        |||||||		;;;;;;
`;;;;'			||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||		`;;;;'
			 
 

FRANÇAIS |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
----------------------------------------------------------------------------
INSTALLATION :
	Vous devez vous assurer que Python soit installé sur votre machine
	si ce n'est pas le cas, référez vous à cette page :
		https://www.python.org/downloads/
		
	Lors du lancement de l'application, les packages nécessaires seront téléchargés ou mis à jours.
	L'ensemble de l'application se trouve dans l'archive Generation_aleatoire_musique.zip
-----------------------------------------------------------------------------
EXÉCUTION :
	Dans le dossier principal se trouve le fichier MusicRNNLauncher.py
	Lancer ce fichier via un terminal avec la commande suivante : python MusicRNNLauncher.py
-----------------------------------------------------------------------------
FONCTIONNEMENT :
	Sur la première fenêtre de l'interface vous devez selectionner les paramètres que vous souhaitez utiliser 
		(Si vous ne donnez pas de valeur au champ "Dossier", l'application ne fonctionnera pas idéalement)
		(Les autres paramètres ont tous une valeure par défaut)
	Nous avons donner la possibilité à l'utilisateur de modifier les paramètres du RNN mais faites attention cela pourrait causer des problèmes
	Le bouton Valider permet de lancer l'entrainement du RNN et la génération de musique
		(en version 1.0 on affiche juste chargement à la place de valider pendant tout le temps de travail)
		(l'entrainement du RNN peut être très long en fonction de la taille de la base de données fournit)
	Une fois la génération terminée, une deuxième fenêtre s'ouvre sur laquelle vous pourrez choisir de lire ou enregistrer les morceaux.
-----------------------------------------------------------------------------
NB :
	Explications détaillée de certains points à la fin de la partie en anglais
	Plus d'information dans le dossier Generation_aleatoire_musique/DOCUMENTATION/
-----------------------------------------------------------------------------


ENGLISH  ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
-----------------------------------------------------------------------------
INSTALLATION :
	Be sure that Python is installed on your computer
	if not, follow this page :
		https://www.python.org/downloads/

	All the files needed are in the archive Generation_aleatoire_musique.zip
-----------------------------------------------------------------------------
EXECUTION :
	In the first folder you will find MusicRNNLauncher.py, launch this file 
-----------------------------------------------------------------------------
HOW IT WORKS :
	On the first window you have to select all the parameters you want to use 
		(If you don't give any value to "Dossier", you will not be able to fully work)
		(Other parameters have default values)
	The button Valider start the training of your RNN and the generation of the music
		(on version 1.0 we just display "chargement" while the RNN is working)
		(If your data base is big, the application can take a lot of time to run)
	Once the generation is complete, another window open, you can chose to either listen or save the musics
-----------------------------------------------------------------------------
DATABASE FORMAT :
	You should use your own database to train the RNN, your database need to be 
		- one folder
		- several midi files in this folder
	please not that if there is another folder in the first one it will not be explored
-----------------------------------------------------------------------------
AMELIORATION :
	v1.0 (04/12/21) : 
		the interface work
		the RNN can be trained for rythms and simple melody
		music created can be saved
	v1.5 (futur ideas) :
		modification of the RNN possible via Advanced Parametre Window
		default RNN optimisation
	v2.0 (futur ideas) :
		the RNN can be trained for polyphonic melody
	v3.0 (futur ideas) :
		graphical représentation of the database
-----------------------------------------------------------------------------
NB :
	For more detailled informmation please refer to the documents in the folder 
		Generation_aleatoire_musique/DOCUMENTATION/

