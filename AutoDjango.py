import os, argparse, json, platform, sys, subprocess, shutil, re, ast
from pathlib import Path
try:
    from termcolor import colored
    from colorama import init
    init()
except:
    subprocess.run("python -m pip install termcolor", stdout=subprocess.DEVNULL, shell=True)
    subprocess.run("python -m pip install termcolors", stdout=subprocess.DEVNULL, shell=True)
    subprocess.run("python -m pip install colorama", stdout=subprocess.DEVNULL, shell=True)


PROJECT_PATH = Path(__file__).resolve().parent
BASE_PATH = PROJECT_PATH / "base"
MAIN_PATH = PROJECT_PATH / "MAIN"
UNICORN_BASE_TEMPALTE = """
    { % load unicorn % }
    <html >
    <head >
        { % unicorn_scripts % }
    </head >
    <body >
        { % csrf_token % }
    </body >
    </html >
"""

TAILWIND_BASE_TEMPALTE = """
{% load static tailwind_tags %}
<!DOCTYPE html>
<html lang="en">
	<head>
    <title>Django Tailwind</title>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<meta http-equiv="X-UA-Compatible" content="ie=edge">
		{% tailwind_css %}
	</head>

	<body class="bg-gray-50 font-serif leading-normal tracking-normal">
		<div class="container mx-auto">
			<section class="flex items-center justify-center h-screen">
				<h1 class="text-5xl">Django + Tailwind = ❤️</h1>
			</section>
		</div>
	</body>
</html>

"""

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
    if not os.path.isdir("MAIN"):
        os.mkdir("MAIN")
    if not is_installed("virtualenv"):
        pip_install("virtualenv")
    if os_version == "Windows":
        print("\nCreating A New virtualenv ... ")
        os.system("python -m virtualenv venv >nul 2>&1")
        print("\nActivating The virtualenv ... ")
        subprocess.call('cmd.exe /k venv\\Scripts\\activate.bat')
    else:
        print("\nCreating A New virtualenv ... \n\n")
        subprocess.run("virtualenv env", shell=True, stdout=subprocess.PIPE)
        print("\nActivating The virtualenv ... ")
        os.system('/bin/bash  --rcfile env/bin/activate')


#Install Then Create Django project and create new Django app
def create_django_project(project_name, app_name):
    os.chdir("MAIN")
    pip_install("django")
    print(f"\nCreating A New Django Project ... {project_name}")
    subprocess.run(f"django-admin startproject {project_name} .", shell=True, stdout=subprocess.PIPE)
    print(f"\nCreating A New Django App ... {app_name}")
    subprocess.run(f"python manage.py startapp {app_name}", shell=True, stdout=subprocess.PIPE)

# open a file and return its content in a string variable
def get_file_content(file):
    with open(file, "r") as f:
        content = f.read()
    return content

def update_file_content(file, content):
    with open(file, "w") as f:
        f.write(content)


def add_to_the_bottom_of_the_file(filename, string_to_add):
    with open(filename, "a") as file:
        file.write("\n"+string_to_add)

# Using the regex, we extract the installed_apps list from settings.py
# It returns the list in a string format
def get_installed_apps_list(settings_file_path):
    settings = get_file_content(settings_file_path)
    pattern = r'(?=INSTALLED_APPS = ).+(?=MIDDLEWARE)'
    match = re.search(pattern, settings, re.DOTALL)
    if match:
        return match.group().replace("INSTALLED_APPS = ","")
    else:
        sys.exit(colored("[!] FATAL ","red", attrs=["bold",])+"Couldn't find the INSTALLED_APPS list!")

# Using the regex, we extract the middleware list from settings.py
# It returns the list in a string format
def get_middleware_list(settings_file_path):
    settings = get_file_content(settings_file_path)
    pattern = r'MIDDLEWARE.+(?=ROOT_URLCONF)'
    match = re.search(pattern, settings, re.DOTALL)
    if match:
        return match.group().replace("MIDDLEWARE = ", "")
    else:
        sys.exit(colored("[!] FATAL ", "red", attrs=["bold", ])+"Couldn't find the MIDDLEWARE list!")

# Using the regex, we extract the urlpatterns list from project/urls.py
# It returns the list in a string format
def get_project_urlpatterns_list(urls_file_path):
    urls = get_file_content(urls_file_path)
    pattern = r'urlpatterns = .+]'
    match = re.search(pattern, urls, re.DOTALL)
    if match:
        print("\n\n\n")
        print(match.group().replace("urlpatterns = ", ""))
        return match.group().replace("urlpatterns = ", "")
    else:
        sys.exit(colored("[!] FATAL ", "red", attrs=[
                 "bold", ])+"Couldn't find the MIDDLEWARE list!")



# Convert and update lists in files (.html, .py)
# Note: list is a list of type string "[1,2,3]"
def update_list_in_file(file, list, value="", append=False, delete=False, position=False):
    content = get_file_content(file)
    python_list = ast.literal_eval(list)
    if append and value not in python_list:
        if not position:
            python_list.append(value)
        else:
            python_list.insert(position, value)
    if delete and value in python_list:
        python_list.remove(value)
    string_list = json.dumps(python_list)
    content = content.replace(list, string_list.replace(
        ",", ",\n\t").replace("]", "\n]\n\n").replace("[", "[\n\t"))
    update_file_content(file, content)


def update_settings_installed_app(app_name_to_add, project_name):
    settings_file = MAIN_PATH / f"{project_name}/settings.py"
    installed_apps_list = get_installed_apps_list(settings_file)
    update_list_in_file(settings_file, installed_apps_list,value=app_name_to_add, append=True)


def update_settings_middleware(middleware_to_add, position, project_name):
    settings_file = MAIN_PATH / f"{project_name}/settings.py"
    middleware_list = get_middleware_list(settings_file)
    update_list_in_file(settings_file, middleware_list, value=middleware_to_add, append=True, position=position)


def update_project_urlpatterns(path_to_add, project_name):
    urls_file = MAIN_PATH / f"{project_name}/urls.py"
    urls_file_content = get_file_content(urls_file)
    static_path = "urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)"
    if static_path in urls_file_content:
        urls_file_content = urls_file_content.replace(static_path, '')
        update_file_content(urls_file, urls_file_content)
        urls_file_content = get_file_content(urls_file)
        add_to_the_bottom_of_the_file(urls_file, path_to_add)
        add_to_the_bottom_of_the_file(urls_file, static_path)
    else:
        add_to_the_bottom_of_the_file(path_to_add)



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
    urls_content = "from django.urls import path\nfrom .views import home\n\nurlpatterns = [\n    path(\"\", home, name=\"home\"),\n]"
    app_urls_file = f"{MAIN_PATH}/{app_name}/urls.py"
    update_file_content(app_urls_file, urls_content)

    #Creating a simple function to render the home page
    print(f"[+]\tUpdating views.py file in {app_name} ... \n")
    views_content = "from django.shortcuts import render\ndef home(request):\n    return render(request, \"home.html\", {})"
    app_views_file = f"{MAIN_PATH}/{app_name}/views.py"
    update_file_content(app_views_file, views_content)

    #Updating the settings.py file
    print(f"[+]\tUpdating settings.py file in {project_name} ... \n")
    settings = f"{MAIN_PATH}/{project_name}/settings.py"
    settings_content = get_file_content(settings)
    installed_apps_list = get_installed_apps_list(settings)
    update_list_in_file(settings, installed_apps_list, value=app_name, append=True)
    settings_content = settings_content.replace("'DIRS': [],", "'DIRS': [BASE_DIR / \"templates\"],")
    settings_content = settings_content.replace(
        "STATIC_URL = 'static/'", "STATIC_URL='/static/'\nif not DEBUG:\n    STATIC_ROOT=BASE_DIR / 'static'\nelse:\n    STATICFILES_DIRS=[BASE_DIR / 'static']")
    update_file_content(settings, settings_content)
    update_settings_installed_app(app_name, project_name)

    #install pillow for media files
    if media:
        pip_install("pillow")
    
    
    #Edit and Update urls.py file of the project folder
    print(f"[+]\tUpdating urls.py file in {project_name} ... \n")
    urls_content = "from django.conf import settings\nfrom django.conf.urls.static import static\nfrom django.contrib import admin\nfrom django.urls import path, include\nfrom django.views.generic.base import TemplateView\n\nurlpatterns = [\n    path('admin/', admin.site.urls), \n    path('', include(\"DJANGO_APP_NAME.urls\")), \n\t]"
    urls_content = urls_content.replace("DJANGO_APP_NAME", app_name)
    if media:
        urls_content = urls_content+"\nurlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)"
    urls_project_file = f"{MAIN_PATH}/{project_name}/urls.py"
    update_file_content(urls_project_file, urls_content)
    
    
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



def install_and_config_package(app_name, project_name, package_list):
    config_urls_file = MAIN_PATH / f"{project_name}/urls.py"
    settings_file = MAIN_PATH / f"{project_name}/settings.py"
    if "djangorestframework" in package_list:
        pip_install("djangorestframework")
        update_settings_installed_app("rest_framework", project_name)
        update_project_urlpatterns("urlpatterns.append(path('api-auth/', include('rest_framework.urls')))", project_name)
    if "django-cors-headers" in package_list:
        pip_install("django-cors-headers")
        update_settings_installed_app("corsheaders", project_name)
        update_settings_middleware("corsheaders.middleware.CorsMiddleware", 2, project_name)
        add_to_the_bottom_of_the_file(settings_file, "CORS_ALLOWED_ORIGINS = [\n\"http://localhost:8080\",\n\"http://127.0.0.1:9000\",\n]")
        add_to_the_bottom_of_the_file(settings_file, "CORS_ALLOW_CREDENTIALS: True")
    if "django-unicorn" in package_list:
        pip_install("django-unicorn")
        update_settings_installed_app("django_unicorn", project_name)
        update_project_urlpatterns(
            "urlpatterns.append(path(\"unicorn/\", include(\"django_unicorn.urls\")))", project_name)
        with open(f"{MAIN_PATH}/templates/unicorn-base_tempalte.html", "w") as uni_base_file:
            uni_base_file.write(UNICORN_BASE_TEMPALTE)

    if "tailwind" in package_list:
        pip_install("django-tailwind") 
        update_settings_installed_app('tailwind', project_name)
        subprocess.run(f"python {MAIN_PATH}/manage.py tailwind init", shell=True)
        shutil.move("theme", MAIN_PATH)
        update_settings_installed_app('theme', project_name)
        add_to_the_bottom_of_the_file(f"{MAIN_PATH}/{project_name}/settings.py", "TAILWIND_APP_NAME = 'theme'")
        internal_ips = "INTERNAL_IPS = ['127.0.0.1',]"
        add_to_the_bottom_of_the_file(f"{MAIN_PATH}/{project_name}/settings.py", internal_ips)
        add_to_the_bottom_of_the_file(f"{MAIN_PATH}/{project_name}/settings.py","import platform\nif platform.system() == 'Windows':\n    NPM_BIN_PATH = r'C:\\Program Files\\nodejs\\npm.cmd'")
        subprocess.run(f"python {MAIN_PATH}/manage.py tailwind install", shell=True)
        update_settings_installed_app('django_browser_reload', project_name)
        update_settings_middleware("django_browser_reload.middleware.BrowserReloadMiddleware", False, project_name)
        update_project_urlpatterns("urlpatterns.append(path('__reload__/', include('django_browser_reload.urls')))", project_name)
        with open(f"{MAIN_PATH}/templates/tailwind-base_tempalte.html", "w") as uni_base_file:
            uni_base_file.write(TAILWIND_BASE_TEMPALTE)


def main():
    parser = argparse.ArgumentParser(description="A Simple Script That Automates Creating Virtual Environment And Creating Django Project with some extra features.")
    parser.add_argument("--venv", nargs="?", const=True, required=False, help="To create a python3 virtual environment.")
    parser.add_argument("--config-media-static-templates", nargs="?", const=True, required=False, help="To config 'templates', 'static', 'media' before launching the Django project.")
    parser.add_argument("--post-installation", nargs="?", const=True, required=False, help="To config 'templates', 'static', 'media' before launching the Django project. [same as --config-media-static-templates]")
    parser.add_argument("--install-package", nargs="+", default='all', choices=("djangorestframework",
                        "django-cors-headers", "django-unicorn","tailwind",), help="Install one or more Django packages.")
    parser.add_argument("--django", nargs="?", const=True, required=False, help="To initiate a new Django project.")
    parser.add_argument("--media", nargs="?", const=True, required=False, help="To handle media files in Django.")
    parser.add_argument("--html2django", nargs="?", const=True, required=False, help="Convert any HTML template (project) into Django app.")
    parser.add_argument("--project", type=str, required=False, help="The name of the Django project ['project_name'/settings.py] .")
    parser.add_argument("--templates", type=str, required=False, default="templates", help="The name of the fodler where you saved the HTML files [for django2html].")
    parser.add_argument("--static", type=str, required=False, default="assets",
                        help="The name of the fodler where you saved the STATICL files [for django2html].")
    parser.add_argument("--app", type=str, required=False, help="The name of the Django app.")


    args = parser.parse_args()

    if not os.path.isdir("MAIN"):
        os.mkdir("MAIN")

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
            if args.config_media_static_templates or args.post_installation:
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
