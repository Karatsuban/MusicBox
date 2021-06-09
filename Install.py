import os
import platform
import pkg_resources
try:
    import tkinter
except ModuleNotFoundError:
    print("OUPS! tkinter n'est pas là.")

###################################### Commun ################################################
osName = platform.system()
sepLigne = "-----------------------------"

required = {'pygame', 'pillow', 'numpy', 'py-midicsv', 'torch', 'matplotlib'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed



def installByOS(type):
    miss = len(missing)
    if osName == "Windows":
        if miss > 0:
            askInstall(type)
        print("All packages are already installed and up to date")

    elif osName == "Darwin":
        if miss > 0:
            askInstall(type, "python3")
        print("All packages are already installed and up to date")

    elif osName == "Linux":
        askInstall(type, "python3")
        print("All packages are already installed and up to date")

def askInstall(type, lang="python"):
    commande = ""
    for cmd in missing:
        commande += "- " + lang + "-m pip install {}\n".format(cmd)
    msg = "Il vous manque les modules suivante pour pouvoir lancer MusicBox: \n\n{}\n{}\n Voici les commande qu'on va executer si vous l'acceptez.\n\n{}".format(missing, sepLigne, commande)

    if osName == "Linux":
        linuxNeed = {"freepats", "timidity", "python3-tk", "python3-pip"}
        commandeLinux = ""
        for cmd in linuxNeed:
            commandeLinux += "- sudo apt-get install {}\n".format(cmd)
        msgLinux = "Il vous manque les modules suivante pour pouvoir lancer MusicBox: \n\n{}\n{}\n Voici les commande qu'on va executer si vous l'acceptez.\n\n{}\n{}\n Il faut installer manuellement les modules suivant si vous ne les avez pas encore:\n\n{} ".format(missing, sepLigne, commande, sepLigne, commandeLinux)

    if type == "Interface":
        if osName == "Linux":
            fenAsk = tkinter.Tk()
            fenAsk.title('Installation Modules')
            fenAsk.geometry('600x400')
            info = tkinter.Label(fenAsk, text=msgLinux)
            info.grid(padx=20, row=2, column=0, columnspan=3)

        elif osName == "Darwin":
            fenAsk = tkinter.Tk()
            fenAsk.title('Installation Modules')
            fenAsk.geometry('450x400')
            info = tkinter.Label(fenAsk, text=msg)
            info.grid(padx=20, row=2, column=0, columnspan=3)

        elif osName == "Windows":
            fenAsk = tkinter.Tk()
            fenAsk.title('Installation Modules')
            fenAsk.geometry('420x400')
            info = tkinter.Label(fenAsk, text=msg)
            info.grid(padx=20, row=2, column=0, columnspan=3)

        buttonA = tkinter.Button(fenAsk, text='Accepter')
        buttonA.config(bd=0, bg='green', command=lambda: [install(lang), fenAsk.destroy()])
        buttonA.grid(row=15, column=0, sticky="e")

        buttonR = tkinter.Button(fenAsk, text='Refuser')
        buttonR.config(bd=0, bg='red', command=lambda: [fenAsk.destroy()])
        buttonR.grid(row=15, column=2, sticky="w")

        tkinter.Label(fenAsk, text=" ").grid(row=0)
        tkinter.Label(fenAsk, text=" ").grid(row=14)

        fenAsk.mainloop()

    else:
        if osName == "Linux":
            print(msgLinux)
            print("-----------------------------")
            print("Attention, vous devez install manuellement les module avec commande sudo")
            print("-----------------------------")
            print("1. Accepter\n2. Refuser\n")

        else:
            print(msg)
            print("-----------------------------")
            print("1. Accepter\n2. Refuser\n")

        choix = "0"
        while choix != "1" and choix != "2":
            choix = input("votre choix: ")
        if choix == "1":
            install(lang)
        else:
            print("Vous avez refuser")


def install(lang="python"):
    if ("pip" in installed):
        print("pip is installed")
        print("Installation of missing packages in progress...")
        for pkg in missing:
            print("This package is currently being installed : ", pkg)

            cmd = lang + ' -m pip install ' + pkg
            os.system(cmd)
    else:
        if osName == "Darwin" or osName == "Linux":
            print("pip not found, please install pip: \n- sudo apt-get install python3-pip")
        else:
            print("pip not found, please install pip (see : https://pip.pypa.io/en/stable/installing/)")


