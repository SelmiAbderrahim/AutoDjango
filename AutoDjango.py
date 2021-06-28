import os
import argparse
import platform
import sys
import subprocess
import shutil

def check_system():
    #Get the operating system version
    os_version = platform.system()
    if os_version.lower() in "windows":
        #Install termcolor and colorama to display colored text in the terminal and cmd
        pip_version = subprocess.check_output("pip --version").decode('UTF-8')[3:10]
        try:
            subprocess.run("pip install termcolor", stdout=subprocess.DEVNULL)
            print("[+] termcolor installed.")
            subprocess.run("pip install colorama", stdout=subprocess.DEVNULL)
            print("[+] colorama installed.")
        except:
            subprocess.run("sudo apt-get install python3-pip", stdout=subprocess.DEVNULL)
            print("[+] Pip installed.")
            sys.exit("Run the script again!")
    elif os_version.lower() in "darwin":
        #Install termcolor and colorama to display colored text in the terminal and cmd
        pip_version = subprocess.run("pip --version", shell=True, capture_output=True).stdout.decode("utf-8")[3:10]
        try:
            subprocess.run("pip install termcolor", shell=True, stdout=subprocess.PIPE)
            print("[+] termcolor installed.")
            subprocess.run("pip install colorama", shell=True, stdout=subprocess.PIPE)
            print("[+] colorama installed.")
        except:
            subprocess.run("sudo easy_install pip", shell=True, stdout=subprocess.PIPE)
            print("[+] Pip installed.")
            sys.exit("Run the script again!")
    elif os_version.lower() in "linux":
        #Install termcolor and colorama to display colored text in the terminal and cmd
        pip_version = subprocess.run("pip --version", shell=True, capture_output=True).stdout.decode("utf-8")[3:10]
        try:
            subprocess.run("pip install termcolor", shell=True, stdout=subprocess.PIPE)
            print("[+] termcolor installed.")
            subprocess.run("pip install colorama", shell=True, stdout=subprocess.PIPE)
            print("[+] colorama installed.")
        except:
            subprocess.run("sudo apt-get install python3-pip", shell=True, stdout=subprocess.PIPE)
            print("[+] Pip installed.")
            sys.exit("Run the script again!")
    return os_version, pip_version

#This function will install virtualenv, then create a new venv, and activate it
def install_venv(os_version):
    print("Installing virtualenv ... ")
    if os_version == "Windows":
        os.system("python -m pip install virtualenv >nul 2>&1")
        print("\n[+] virtualenv installed.")
        print("\nCreating A New virtualenv ... ")
        os.system("python -m virtualenv MAIN/venv >nul 2>&1")
        print("\nActivating The virtualenv ... ")
        subprocess.call('cmd.exe /k MAIN\\venv\\Scripts\\activate.bat')

    else:
        subprocess.run("pip install virtualenv", shell=True, stdout=subprocess.PIPE)
        print("\n[+] virtualenv installed.")
        print("\nCreating A New virtualenv ... ")
        subprocess.run("virtualenv MAIN/env", shell=True, stdout=subprocess.PIPE)
        print("\nActivating The virtualenv ... ")
        os.system('/bin/bash  --rcfile MAIN/env/bin/activate')
    
#Install Then Create Django project and create new Django app
def create_django_project(project_name, app_name):
    os.chdir("MAIN")
    print("\nInstalling Django ... ")
    subprocess.run("pip install django", shell=True, stdout=subprocess.PIPE)
    print(f"\nCreating A New Django Project ... {project_name}")
    subprocess.run(f"django-admin startproject {project_name} .", shell=True, stdout=subprocess.PIPE)
    print(f"\nCreating A New Django App ... {app_name}")
    subprocess.run(f"python manage.py startapp {app_name}", shell=True, stdout=subprocess.PIPE)

#Django post installation
def post_installation(project_name, app_name):
    print("\nPost Installation:\n")
    #Creating a template and static folders
    subprocess.run("mkdir templates", shell=True)
    print("[+]\tCreating templates folder ... \n")
    subprocess.run("mkdir static", shell=True)
    print("[+]\tCreating static folder ... \n")
    subprocess.run("mkdir media", shell=True)
    print("[+]\tCreating media folder ... \n")
    #Creating new urls.py file in the app 
    print(f"[+]\tCreating urlsCONFIG for {app_name} ... \n")
    urls_content = "from django.urls import path\nfrom .views import home\nurlpatterns = [\n    path(\"\", home, name=\"home\"),\n]"
    with open(f"{app_name}/urls.py", "w") as urls:
        urls.write(urls_content)
    #Creating a simple function to render the home page
    print(f"[+]\tUpdating views.py file in {app_name} ... \n")
    views_content = "\nfrom django.shortcuts import render\ndef home(request):\n    return render(request, \"home.html\", {})"
    with open(f"{app_name}/views.py", "w") as views:
        views.write(views_content)
    #Updating the settings.py file
    print(f"[+]\tUpdating settings.py file in {project_name} ... \n")
    settings = f"{project_name}/settings.py"
    temp = open("temp", "w")
    with open(settings, "r") as stng:
        #Add the app we just installed
        for line in stng:
            if 'django.contrib.staticfiles' in line:
                line = f"    'django.contrib.staticfiles',\n    '{app_name}',\n"  
            # config templates 
            if "'DIRS': []" in line:
                line = "        'DIRS': [BASE_DIR /\"templates\"],\n" 
            #Config static 
            static_content = "STATIC_URL = '/static/'\n#STATIC_ROOT = BASE_DIR / 'static'\nSTATICFILES_DIRS = [BASE_DIR / 'static']\nMEDIA_ROOT  = BASE_DIR / 'media'\nMEDIA_URL = '/media/'"
            if "STATIC_URL = '/static/'" in line:
                line = static_content
            temp.write(line)
        temp.close()
        shutil.move("temp", settings)
    #install pillow for media files
    print(f"[+]\tInstalling Pillow ... \n")
    subprocess.run("pip install pillow", shell=True, stdout=subprocess.PIPE)
    #Edit and Update urls.py file of the project folder
    print(f"[+]\tUpdating urls.py file in {project_name} ... \n")
    urls_content = f"\nfrom django.conf import settings\nfrom django.conf.urls.static import static\nfrom django.contrib import admin\nfrom django.urls import path, include\nurlpatterns = [\n    path('admin/', admin.site.urls),\n    path('', include(\"{app_name}.urls\")),\n] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)"
    urls = f"{project_name}/urls.py"
    with open(urls, "w") as url:
        url.write(urls_content)
    #Create a home page
    print(f"[+]\tCreating a simple home page ... \n")
    with open(f"templates/home.html", "w") as f:
        f.write("<h1>Selmi Abderrahim Says Hi ;)")
    #migrate
    os.chdir("..")
    print(f"\n\n[+]\tMigrating the project ... \n")
    subprocess.run("python MAIN/manage.py migrate", shell=True)
    #Edit and Update urls.py file of the project folder
    print(f"\n\n[+]\tRun the server ... \n")
    subprocess.run("python MAIN/manage.py runserver", shell=True)
    
    
    

def main():
    parser = argparse.ArgumentParser(description="A Simple Script That Automates Creating Virtual Environment And Creating Django Project.")
    parser.add_argument("--venv", nargs="?", const=True, required=False, help="To create a Python virtual environment.")
    parser.add_argument("--post_installation", nargs="?", const=True, required=False, help="To config and launch the Django project.")
    parser.add_argument("--django", nargs="?", const=True, required=False, help="To create a Django project.")
    parser.add_argument("--project", type=str, required=False, help="The name of the Django project.")
    parser.add_argument("--app", type=str, required=False, help="The name of the Django app.")


    args = parser.parse_args()
    if args.venv:
        os_version, pip_version = check_system()
        from termcolor import colored
        from colorama import init
        #init to enable the color feature in the cmd
        init()
        #Print the system informations
        python_version = platform.python_version()
        print("\n")
        print(colored(f"Operating System:\t{os_version}", "blue"))
        print(colored(f"Python Version:\t{python_version[:10]}", "blue"))
        print(colored(f"Pip Version:\t{pip_version}", "blue"))
        print("\n")

        install_venv(os_version)

    
    if args.django:
        create_django_project(args.project, args.app)
        if args.post_installation:
            post_installation(args.project, args.app)


if __name__ == "__main__":
    main()
