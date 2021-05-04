# !/usr/bin/python3
#coding: utf-8
from source.view.scripts import InterfaceChoixParametres, InterfaceLecteur
import Install

if __name__ == "__main__":
	Install.installRequiredPackages()
	InterfaceChoixParametres.start()