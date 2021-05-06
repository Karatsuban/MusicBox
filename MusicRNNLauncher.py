# !/usr/bin/python3
#coding: utf-8
from source.view.scripts import Application
import Install

if __name__ == "__main__":
	Install.installRequiredPackages()
	Application.start()