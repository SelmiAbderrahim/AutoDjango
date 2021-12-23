# AutoDjango

A Simple Python Script To Automate The Creation Of Virtual Environment And Django Project.

## Features

- Create virtual environment
- Install Django packages
- Convert HTML template into Django application

## Note: 
 This works when you want to create a new Django project, it won't work if you're willing to update your old Django project.
### Requirements:

- Python 

### Installation:

```
$ git clone https://github.com/SelmiAbderrahim/AutoDjango.git

```
### Usage:


- To create a virtual environment and activate it:

```
$ python AutoDjango.py --venv

```

- To install only Django:

```
$ python AutoDjango.py --django --project PROJECTNAME --app APPNAME

```

- To install only Django plus the usual configuration (static, templates and pther settings):

```
$ python AutoDjango.py --django --project PROJECTNAME --app APPNAME --config-media-static-templates 

```

- To enable and configure media files:

```
$ python AutoDjango.py --django --project PROJECTNAME --app APPNAME --config-media-static-templates --media 

```


- To install a django package:

```
$ python AutoDjango.py --django --project PROJECTNAME --app APPNAME --config-media-static-templates --media  --install-package django-unicorn django-cors-headers djangorestframework

```

😞  For now, it supports only three packages