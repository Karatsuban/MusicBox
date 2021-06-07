import os
import pkg_resources

def installRequiredPackages():

    required ={'pygame','pillow','numpy','py-midicsv','torch','matplotlib'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if len(missing) > 0:
        print ("One or more packages are missing")
        if("pip" in installed):
            print("pip is installed")
            print ("Installation of missing packages in progress...")
            for pkg in missing:
                print("This package is currently being installed : ", pkg)
                cmd = 'python -m pip install ' + pkg
                os.system(cmd)
        else:
            print("pip not found, please install pip (see : https://pip.pypa.io/en/stable/installing/)")
    else:
        print("All packages are already installed and up to date")
