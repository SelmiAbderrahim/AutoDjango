import os, argparse, json, platform, sys, subprocess, shutil, re, ast
from pathlib import Path
try:
    from termcolor import colored
    from colorama import init
    #init to enable the color feature in the cmd
    init()
except:
    subprocess.run("python -m pip install termcolor", stdout=subprocess.DEVNULL, shell=True)
    subprocess.run("python -m pip install termcolors", stdout=subprocess.DEVNULL, shell=True)
    subprocess.run("python -m pip install colorama", stdout=subprocess.DEVNULL, shell=True)


PROJECT_PATH = Path(__file__).resolve().parent
BASE_PATH = PROJECT_PATH / "base"
MAIN_PATH = PROJECT_PATH / "MAIN"


#To make suret he virtualenv is activated
def is_venv():
    try:
        os.environ["VIRTUAL_ENV"]
    except KeyError:
        return False
    else:
        return True

def pip_install(package):
    from termcolor import colored
    from colorama import init
    #init to enable the color feature in the cmd
    init()
    print(f"\nInstalling {package} ... ")
    try:
        subprocess.run(f"python -m pip install {package}", shell=True, stdout=subprocess.PIPE)
        print(colored("✅ - ", "green") + f"{package} installed.")
    except:
        print(colored("❌ - ", "red") + f"Failed to install {package}!")

#To see whether a Python package/module is installed or not
def  is_installed(package):
    packages = " ".join(pack.lower() for pack in os.popen("python -m pip freeze"))
    if package in packages:
        return True
    return False
  
def get_command_output(command):
    try: 
        return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
    except:
        return None

#Install packages and check for few things that we need
def check_system():
    #Get the operating system version
    os_version = platform.system()
    pip_version = get_command_output("python -m pip --version")[3:10]
    if pip_version is None:
        pip_version = "Unknown"

    if not is_installed("colorama") and not is_installed("termcolors") and not is_installed("termcolor"):  
        pip_install("termcolor")    
        pip_install("colorama")         

    return os_version, pip_version


#This function will install, create, then activate a virtualenv
def install_venv(os_version):
    if not is_installed("virtualenv"):
        pip_install("virtualenv")
    if os_version == "Windows":
        print("\nCreating A New virtualenv ... ")
        os.system("python -m virtualenv MAIN/venv >nul 2>&1")
        print("\nActivating The virtualenv ... ")
        subprocess.call('cmd.exe /k MAIN\\venv\\Scripts\\activate.bat')
    else:
        print("\nCreating A New virtualenv ... \n\n")
        subprocess.run("virtualenv MAIN/env", shell=True, stdout=subprocess.PIPE)
        print("\nActivating The virtualenv ... ")
        os.system('/bin/bash  --rcfile MAIN/env/bin/activate')


#Install Then Create Django project and create new Django app
def create_django_project(project_name, app_name):
    os.chdir("MAIN")
    pip_install("django")
    print(f"\nCreating A New Django Project ... {project_name}")
    subprocess.run(f"django-admin startproject {project_name} .", shell=True, stdout=subprocess.PIPE)
    print(f"\nCreating A New Django App ... {app_name}")
    subprocess.run(f"python manage.py startapp {app_name}", shell=True, stdout=subprocess.PIPE)


#Django post installation
def post_installation(project_name, app_name, media=False):
    print("\nPost Installation:\n")

    #Creating template and static folders
    subprocess.run(f'mkdir {MAIN_PATH / "templates"}', shell=True)
    print("[+]\tCreating templates folder ... \n")
    subprocess.run(f'mkdir {MAIN_PATH / "static"}', shell=True)
    print("[+]\tCreating static folder ... \n")
    if media:
        subprocess.run(f'mkdir {MAIN_PATH / "media"}', shell=True)
        print("[+]\tCreating media folder ... \n")

    #Creating new urls.py file in the app 
    print(f"[+]\tCreating urlsCONFIG for {app_name} ... \n")
    urls_content = open(f'{BASE_PATH / "urls.py"}', "r").read()
    with open(f"{MAIN_PATH}/{app_name}/urls.py", "w") as urls:
        urls.write(urls_content)

    #Creating a simple function to render the home page
    print(f"[+]\tUpdating views.py file in {app_name} ... \n")
    views_content = open(f'{BASE_PATH / "views.py"}', "r").read()
    with open(f"{MAIN_PATH}/{app_name}/views.py", "w") as views:
        views.write(views_content)

    #Updating the settings.py file
    print(f"[+]\tUpdating settings.py file in {project_name} ... \n")
    settings = f"{MAIN_PATH}/{project_name}/settings.py"
    settings_copy = open(settings, "r").read()
    base_settings = open(f'{BASE_PATH / "settings.py"}', "r").read()
    with open(settings, "w") as stng:
        secret_key = [string for string in settings_copy.split() if "django-insecure" in string][0]
        base_settings =  base_settings.replace("DJANGO_SECRET_KEY", secret_key)
        base_settings = base_settings.replace("DJANGO_APP_NAME", f"'{app_name}'")
        base_settings = base_settings.replace("DJANGO_PROJECT_NAME", f"{project_name}")
        if media:
            base_settings = base_settings.replace("#MEDIA_ROOT", "MEDIA_ROOT")
            base_settings = base_settings.replace("#MEDIA_URL", "MEDIA_URL")
        stng.write(base_settings)
    
    #install pillow for media files
    if media:
        pip_install("pillow")
    
    
    #Edit and Update urls.py file of the project folder
    print(f"[+]\tUpdating urls.py file in {project_name} ... \n")
    urls_content = open(f'{BASE_PATH / "project_urls.py"}', "r").read()
    urls_content = urls_content.replace("DJANGO_APP_NAME", app_name)
    if media:
        urls_content = urls_content+"\nurlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)"
    urls = f"{MAIN_PATH}/{project_name}/urls.py"
    with open(urls, "w") as url:
        url.write(urls_content)
    
    
    #Create a home page
    print(f"[+]\tCreating a simple home page ... \n")
    with open(f'{MAIN_PATH / "templates/home.html"}', "w") as f:
        f.write("<h1>Selmi Abderrahim Says Hi ;)</h1>")
    #migrate
    os.chdir("..")
    print(f"\n\n[+]\tMigrating the project ... \n")
    subprocess.run(f'python {MAIN_PATH / "manage.py"} migrate', shell=True)

    
def run_server():
    print(f"\n\n[+]\tRun the server ... \n")
    os.system(f'pip freeze > {MAIN_PATH / "requirements.txt"}')
    subprocess.run(f'python {MAIN_PATH / "manage.py"} runserver', shell=True)


#src="file.extension" --> src="{% static 'file.extension' %}"
def update_static_links(file_to_update, html=True):
    try:
        content_copy = open(file_to_update, "r").read()
    except FileNotFoundError:
        return None
    else:
        static_files_paths = []
        for root, direcectories, files in os.walk(f"{MAIN_PATH}/static"):
            for filename in files:
                path = os.path.join(root, filename)
                static_files_paths.append({
                    "filename":filename,
                    "path":path[path.find("static/")+7:len(path)]
                })
        if html:
            srcs = re.findall('src=[\'"]?([^\'" >]+)', content_copy)
            hrefs = re.findall('href=[\'"]?([^\'" >]+)', content_copy)
            for f in static_files_paths:
                filename = f["filename"]
                path = f["path"]
                try:
                    path_to_replace = [path for path in srcs+hrefs if filename in path][0]
                except:
                    path_to_replace = None
                if path_to_replace and [path for path in srcs+hrefs if ".html" not in path]:
                    content_copy = content_copy.replace(path_to_replace, f"{{% static '{path}' %}}")

        with open(file_to_update, "w") as updated:
            updated.write(content_copy)
            return True


#href="index.html" --> href="{% url 'spacename' %}"
def update_template_urls(urls, file_to_update):
    try:
        content_copy = open(file_to_update, "r").read()
        content_copy = content_copy.replace("./","")
    except FileNotFoundError:
        return None
    else:
        hrefs = re.findall('href=[\'"]?([^\'" >]+)', content_copy)
        for url in urls:
            href = url["file_name"]
            spacename = url["space_name"]
            if [link for link in hrefs if ".html" in link]:
                content_copy = content_copy.replace(href, f"{{% url '{spacename}' %}}")
        
        with open(file_to_update, "w") as updated:
            updated.write(content_copy)
            return True


#Convert HTML template into Django app
def html2django(zipfile, static_folder, templates_folder):
    os_version = platform.system()
    from zipfile import ZipFile, BadZipFile
    from termcolor import colored
    from colorama import init
    #init to enable the color feature in the cmd
    init()
    subprocess.run("python -m pip install --upgrade pip", stdout=subprocess.DEVNULL if os_version=="Windows" else subprocess.PIPE, shell=True if os_version in ["Linux", "Darwin"] else False)
    images = []
    #Extract the zip file and organize files depending on their extensions
    try:
        with ZipFile(zipfile,"r") as zip:
            zip_file_name = zipfile.replace(".zip","")

            #Create Django App
            create_django_project("project", zip_file_name)
            post_installation("project", zip_file_name, media=True)
            #Extracting
            print(f"Extracting:\t{zip_file_name}")
            zip.extractall()
            all_file_names = []
            paths = []
            templates = []
            print(colored("\nMigrating your files to the Django project ... ", "green"))
            for root, direcectories, files in os.walk(zip_file_name):
                for filename in files:
                    path = os.path.join(root, filename)
                    paths.append(path)
                    all_file_names.append(filename)
                    if ".html" in filename:
                        templates.append({
                            "file_name":filename,
                            "space_name":filename.replace('.html','').replace('-','_'),
                            "view_name":filename.replace('.html','').replace('-','_')+"_view",
                        })
            with open("templates.json", "w") as template_json:
                template_json.write(json.dumps(templates))
            
            try:
                shutil.copytree(zip_file_name+"/"+static_folder, f"{MAIN_PATH}/static")
            except FileExistsError:
                shutil.rmtree(f"{MAIN_PATH}/static")
                shutil.copytree(zip_file_name+"/"+static_folder, f"{MAIN_PATH}/static")
            try:
                shutil.copytree(zip_file_name+"/"+templates_folder, f"{MAIN_PATH}/templates")
            except FileExistsError:
                shutil.rmtree(f"{MAIN_PATH}/templates")
                shutil.copytree(zip_file_name+"/"+templates_folder, f"{MAIN_PATH}/templates")

    except BadZipFile:
        sys.exit(colored("Error: Zip File Is Not Valid!", "red"))

    except FileNotFoundError:
        sys.exit(colored("File Not Found Error: Enter A Valid File Name!", "red"))
    
    #Create Views For Each Template
    views_and_urls = []
    views_file_path = os.path.join(f"{MAIN_PATH}/{zip_file_name}/", "views.py")
    urls_file_path = os.path.join(f"{MAIN_PATH}/{zip_file_name}/", "urls.py")
    templates_json = json.load(open("templates.json", "r"))

    with open(views_file_path, "a") as views:
        for template in templates_json:
            namespace = template["space_name"]
            filename = template["file_name"]
            viewname = template["view_name"]
            content = f"\ndef {viewname}(request):\n    return render(request, \"{filename}\", {{}})\n"
            views.write(content)



    with open(urls_file_path, "w") as urls:
        content = "from django.urls import path\nfrom .views import *\nurlpatterns = [\n"
        urls.write(content)

    with open(urls_file_path, "a") as urls:
        content = "from django.urls import path\nfrom .views import *\nurlpatterns = [\n"

        for template in templates_json:
            namespace = template["space_name"]
            filename = template["file_name"]
            viewname = template["view_name"]
            if "home" in template:
                content = f"    path(\"\", home, name=\"home\"),\n"
            else:
                content = f"    path(\"{namespace}\", {viewname}, name=\"{namespace}\"),\n"
            urls.write(content)
            views_and_url = {"template":template, "namespace":namespace}
            views_and_urls.append(views_and_url)
    with open(urls_file_path, "a") as urls:
        urls.write("]")



    #Update html files to fit Django
    templates = json.load(open("templates.json", "r"))
    for template in templates:
        file_to_update = f"{MAIN_PATH}/templates/{template['file_name']}"
        if update_static_links(file_to_update, html=True) is None:
            print(f"[STATIC] Couldn't find {file_to_update} in templates. "+colored("X", "red", attrs=["bold",]))
        else:
            print(f"[STATIC] {file_to_update} updated. "+colored("✓", "green", attrs=["bold",]))
        if update_template_urls(templates, file_to_update) is None:
            print(f"[TEMPLATE] Couldn't find {file_to_update} in templates. "+colored("X", "red", attrs=["bold",]))
        else:
            print(f"[TEMPLATE] {file_to_update} updated. "+colored("✓", "green", attrs=["bold",]))

def append_string_format_list(string_list, element, string_to_remove=""):
    python_list = ast.literal_eval(string_list.replace(" ","").replace("\n","").replace(string_to_remove, ""))
    if element not in python_list:
        python_list.append(element)
        string_list = json.dumps(python_list)
        return string_to_remove+string_list.replace("[","[\n").replace(",",",\n").replace("]","]\n")
    return None

def add_to_the_bottom_of_the_file(filename, string_to_add):
    with open(filename, "a") as file:
        file.write("\n"+string_to_add)

def update_settings_installed_app(app_name_to_add, project_name):
    settings_file = MAIN_PATH / f"{project_name}/settings.py"
    with open(settings_file, "r") as settings:
        content = settings.read()
        pattern = r'INSTALLED_APPS.+(?=MIDDLEWARE)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            old_installed_apps_string = match.group().strip("\n")
            new_installed_apps_string = append_string_format_list(old_installed_apps_string, app_name_to_add, string_to_remove="INSTALLED_APPS=")
        else:
            print(colored("ERROR: ", "red")+" Couldn't find INSTALLED_APPS!")
    if new_installed_apps_string:
        with open(settings_file, "w") as settings:
            content = content.replace(old_installed_apps_string, new_installed_apps_string)
            settings.write(content)
        
def update_settings_middleware(middleware, before_middleware, project_name):
    settings_file = MAIN_PATH / f"{project_name}/settings.py"
    with open(settings_file, "r") as settings:
        content = settings.read()
        pattern = r'MIDDLEWARE.+(?=ROOT_URLCONF)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            old_installed_apps_string = match.group().strip("\n")
            python_list = ast.literal_eval(old_installed_apps_string.replace(" ","").replace("\n","").replace("MIDDLEWARE=", ""))
            if middleware not in python_list:
                python_list.insert(python_list.index(before_middleware), middleware)
                new_installed_apps_string = "MIDDLEWARE = "+json.dumps(python_list)
        else:
            print(colored("ERROR: ", "red")+" Couldn't find INSTALLED_APPS!")
    if new_installed_apps_string:
        with open(settings_file, "w") as settings:
            content = content.replace(old_installed_apps_string, new_installed_apps_string.replace("[","[\n").replace(",",",\n").replace("]","]\n"))
            settings.write(content)

def install_and_config_package(app_name, project_name, package_list):
    config_urls_file = MAIN_PATH / f"{project_name}/urls.py"
    settings_file = MAIN_PATH / f"{project_name}/settings.py"
    if "djangorestframework" in package_list:
        pip_install("djangorestframework")
        update_settings_installed_app("rest_framework", project_name)
        add_to_the_bottom_of_the_file(config_urls_file, "urlpatterns.append(path('api-auth/', include('rest_framework.urls')))")
    if "django-cors-headers" in package_list:
        pip_install("django-cors-headers")
        update_settings_installed_app("corsheaders", project_name)
        update_settings_middleware("corsheaders.middleware.CorsMiddleware", "django.middleware.common.CommonMiddleware", project_name)
        add_to_the_bottom_of_the_file(settings_file, "CORS_ALLOWED_ORIGINS = [\n\"http://localhost:8080\",\n\"http://127.0.0.1:9000\",\n]")
        add_to_the_bottom_of_the_file(settings_file, "CORS_ALLOW_CREDENTIALS: True")
    if "django-unicorn" in package_list:
        pip_install("django-unicorn")
        update_settings_installed_app("django_unicorn", project_name)



def main():
    parser = argparse.ArgumentParser(description="A Simple Script That Automates Creating Virtual Environment And Creating Django Project with some extra features.")
    parser.add_argument("--venv", nargs="?", const=True, required=False, help="To create a python3 virtual environment.")
    parser.add_argument("--config-media-static-templates", nargs="?", const=True, required=False, help="To config 'templates', 'static', 'media' before launching the Django project.")
    parser.add_argument("--install-package", nargs="+", default='all', choices=("djangorestframework",
                        "django-cors-headers", "django-unicorn",), help="Install one or more Django packages.")
    parser.add_argument("--django", nargs="?", const=True, required=False, help="To initiate a new Django project.")
    parser.add_argument("--media", nargs="?", const=True, required=False, help="To handle media files in Django.")
    parser.add_argument("--html2django", nargs="?", const=True, required=False, help="Convert any HTML template (project) into Django app.")
    parser.add_argument("--project", type=str, required=False, help="The name of the Django project ['project_name'/settings.py] .")
    parser.add_argument("--templates", type=str, required=False, default="templates", help="The name of the fodler where you saved the HTML files [for django2html].")
    parser.add_argument("--static", type=str, required=False, default="assets",
                        help="The name of the fodler where you saved the STATICL files [for django2html].")
    parser.add_argument("--app", type=str, required=False, help="The name of the Django app.")


    args = parser.parse_args()
    if args.venv:
        os_version, pip_version = check_system()
        #Print the system informations
        python_version = platform.python_version()
        print("\n")
        print(colored(f"Operating System:\t{os_version}", "blue"))
        print(colored(f"python3 Version:\t{python_version[:10]}", "blue"))
        print(colored(f"Pip Version:\t{pip_version}", "blue"))
        print("\n")

        install_venv(os_version)

    if args.django:
        if not is_venv:
            print(colored("[!] ", "red", attrs=["bold",])+"Please make sure to activate the virtualenv.")
        else:
            create_django_project(args.project, args.app)
            if args.config_media_static_templates:
                post_installation(args.project, args.app, media=args.media)
            if args.install_package:
                install_and_config_package(args.app, args.project, args.install_package)
  
            run_server()


    if args.html2django:
        if not is_venv:
            print(colored("[!] ", "red", attrs=["bold",])+"Please make sure to activate the virtualenv.")
        else:
            zipfile = input("\nEnter The Path Of The Zip File:\t")
            html2django(zipfile, args.static, args.templates)
            run_server()

    

if __name__ == "__main__":
    main()
