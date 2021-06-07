# !/usr/bin/python3
# coding: utf-8
import Install
Install.installRequiredPackages()
from source.view.scripts import LineClient
LineClient.start()
