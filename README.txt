     ;                                                              ;    
     ;;                                                             ;;
     ;';.                                                           ;';.
     ;  ;;        |||||||||||||||||||||||||||||||||||||||           ;  ;;
     ;   ;;       ||                                   ||           ;   ;;
     ;    ;;      ||  GENERATION ALEATOIRE DE MUSIQUE  ||           ;    ;;
     ;    ;;      ||                                   ||           ;    ;;
     ;   ;'       |||||||||||||||||||||||||||||||||||||||           ;   ;'
     ;  '                                                           ;  ' 
,;;;,;                                                         ,;;;,;
;;;;;;                                                         ;;;;;;
`;;;;'                                                         `;;;;'


V4.0.0


Projet de génération aléatoire musique :

|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||    Authors :                       Clients :                  ||
||        GUERIN CLEMENT                  BODINI OLIVIER         ||
||        GARNIER RAPHAEL                 TOMEH NADI             ||
||        ESCRIVA ANTOINE                                        ||
||        BRUSCHINI CLEMENT           Dates :                    ||
||        BOSSARD FLORIAN                 01/10/21 - 17/04/21    ||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


Stage :

|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||                                    Clients :                  ||
||    Authors :                           BODINI OLIVIER         ||
||        GARNIER RAPHAEL                 TOMEH NADI             ||
||        YUNFEI JIA                      LE ROUX JOSEPH         ||
||                                    Dates :                    ||
||                                        03/05/21 - 02/07/21    ||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

----------------------------------------------------------------------------
LANCEMENT :
	L'application peut se lancer de deux manières différentes :
	-avec l'interface graphique
	-en ligne de commande

	Vous devez vous assurer que Python soit installé sur votre machine
	si ce n'est pas le cas, référez vous à cette page :
		https://www.python.org/downloads/

	Interface :
	Dans le dossier principal se trouve le fichier MusicBox.py
	Lancer ce fichier via un terminal avec la commande suivante : python MusicBox.py (l'appel à python peut varier selon votre OS)
	La vérification de la présence des packages nécessaires sera effectuée à chaque lancement

	Ligne de commande :
	Dans le dossier principal se trouve le fichier MusicBoxLine.py
	Lancer ce fichier via un terminal avec la commande suivante : python MusicBoxLine.py (l'appel à python peut varier selon votre OS)

-----------------------------------------------------------------------------
FONCTIONNEMENT INTERFACE:
	Menu :
	Sur la fenêtre "Menu" de l'interface, vous devez selectionner les paramètres que vous souhaitez utiliser pour l'entraînement du modèle et la génération
	Tous les paramètres ont des valeurs par défaut que vous pouvez modifier en changeant la valeur sur l'interface.
	Une fois que vous êtes satisfait des parmaètres, cliquez sur le bouton "Entraîner" qui vous emmènera sur la fenêtre "Info"
	Cliquer sur "Accès direct au lecteur" basculera sur l'interface "Lecteur"
	Cliquer sur "Accès graphiques" basculera sur l'interface "Graphe"
	CLiquer sur "Générer morceaux" basculera sur "Lecteur" après avoir généré de nouveaux morceaux

	Info :
	Cette fenêtre affiche le nombre d'epoch restant sur le nombre total et une estimation du temps restant.
	Si l'entraînement prend trop de temps, vous pouvez cliquer sur "Arrêt entraînement"
	(Note : dans le cas où le temps d'entraînement sur une epoch est très long, l'entraînement mettra du temps à s'arrêter)
	(Note : la conversion d'un grand nombre de fichiers avant l'entraînement peut mettre beaucoup de temps. Dans ce cas, l'appui sur le bouton n'aura un effet que lorsque l'entraînement commencera)
	Lorsque l'entraînement est fini, si vous avez sélectionné l'option de création de graphes, la fenêtre basculera sur l'interface "Graphe"

	Graphe :
	Cette fenêtre permet d'afficher les graphiques de Loss par élément d'une note et d'accuracy globale lors de l'entraînement du modèle
	Vous pouvez naviguer entre les différents graphiques en sélectionnant un nom dans la liste déroulante.
	Lorsque vous cliquez sur "Retour", l'interface revient sur "Menu"

	Lecteur :
	Cette fenêtre vous permet d'écouter les fichiers générés par l'application.
	Les quatre boutons vous permettent de mettre en pause, de lire un morceau, de lire le suivant et le précédent.
	Alternativement, vous pouvez sélectionner un morceau dans la liste qui sera joué automatiquement
	Le bouton "Accéder au dossier" permet d'ouvrir une fenêtre de l'explorateur sur le dossier où sont stockés les morceaux
	Le bouton "Supprimer les fichiers" permet de supprimer tous les fichiers générés après confirmation.
	Le bouton "Retour" bascule sur l'interface "Menu".

	Format :
	Cette fenêtre vous permet de créer un format dans lequel les données midi vont être convertis avant d'être utilisées pour l'entraînement du modèle.
	Le nombre d'éléments correspond au nombre de valeurs qu'une note encodée devra posséder.
	Pour chaque élément, vous devez choisir son type parmi la liste.
	Attention : vous ne devez pas mettre deux éléments de même type ! Cela pourrait conduire à des résultats imprévus, voire des erreurs
	Fusion des pistes : toutes les pistes de chaque fichier Midi seront fusionnées en une seule piste
	Note entière : lors de l'entraînement, la note est considérée comme un bloc et non comme un ensemble d'éléments.
	Vous pouvez choisir de découper toutes les X mesures pour augmenter le nombre de séquences tout en diminuant leur taille. Par défaut, il n'y a pas de découpage et la conversion dans ce format produira une seule séquence
	Le bouton "Enregistrer" n'est cliquable que lorsque toutes les données nécessaires ont été rentrées et basculera sur "Menu" après avoir sauvegardé votre format.
	Le bouton "Annuler" n'enregistre pas le format et bascule l'interface sur "Menu"


FONCTIONNEMENT LIGNE DE COMMANDE :

	Depuis un terminal, vous pouvez lancer MusicBoxLine.py avec les paramètres ci-dessus, dans n'importe quel ordre :

	Nom parametre           Type            Valeurs
	-----------------------------------------------------------------------------
	URL_Dossier             String          Le dossier doit contenir des fichiers .mid
	NombreMorceaux          Int             Valeur dans [1, 200]
	DureeMorceaux           Int             Valeur dans [5, 1000]
	TypeGeneration          String          Valeur dans ['Melodie', 'Rythme', ...]
	TauxApprentissage       Float           Valeur dans ]0:1[
	NombreEpoch             Int             Valeur dans [1, 1000000]
	NombreDimensionCachee   Int             Valeur dans [2^4:2^11], multiple de 2 de preference.
	NombreLayer             Int             Valeur dans [1, 5]
	NombreSequenceBatch     Int             Valeur dans [1:2^9], multiple de 2 de preference
	SavePath                String          Chemin absolu valide de sauvegarde du modele
	LoadPath                String          Chemin absolu valide de chargment du modele
	generate                                Pour generer des morceaux dans le dossier Résultat après entrainement
	graph                                   Pour generer des graphiques bases sur les donnees d'entrainement
	stat                                    Pour afficher des statistiques sur les donnees d'entrainement
	params                                  Pour afficher les parametres
	help                                    Pour afficher cette aide
	update                                  Pour verifier l'installation des packages
	credits                                 Pour afficher les credits de l'application	

	Note : les paramètres sans type ne prennent pas de valeur
	Note : la syntaxe est la suivante : $ python MusicBoxLine.py parametre1=valeur1 parametre2
	Note : l'affichage de l'aide arrête l'application après l'affichage

-----------------------------------------------------------------------------
NB :
	Plus d'information dans le dossier Generation_aleatoire_musique/DOCUMENTATION/
-----------------------------------------------------------------------------