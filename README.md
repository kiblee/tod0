tod0
====

A CLI for Microsoft To Do

[![CircleCI](https://circleci.com/gh/kiblee/tod0.svg?style=svg&circle-token=7c223e0b25b7428107e841926315e74478cacb55)](https://circleci.com/gh/kiblee/tod0)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

#### Microsoft To Do Command Line Interface

`tod0` lets you use [Microsoft To Do](https://todo.microsoft.com/) from the command line. 
You can view, add, edit, and delete your tasks without leaving your terminal. 


Installation
------------

### Install from PyPI

```sh
pip install tod0
```

### Install from source

```sh
git clone https://github.com/kiblee/tod0.git
cd tod0
python setup.py install
```


Commands
--------
`tod0` is envoked with the command `tod` for easier and quicker access.

`tod` supports the following commands:

    complete     mark task as completed
    create       create a task
    delete       delete a task
    list         list tasks or folders
    
 
Run with `--help`/`-h` for detailed usage.


Getting your own API key
------------------------

You need to get your own Microsoft API key to use `tod0`. 
  1. Sign in to the [Azure portal](https://portal.azure.com/) using a Microsoft account.
  2. In the left-hand navigation pane, select the `Azure Active Directory` service, and then select `App registrations > New registration`.
  3. When the Register an application page appears, enter your application's registration information:
     - Name: `tod0`
     - Supported account types: `Accounts in any organizational directory and personal Microsoft accounts`
     - Platform configuration: `Client Application`
  4. Click `Register` when finished.
  5. You will be redirected to the app's authentication page. Under `Platform configurations` click `Add a platform`. 
  6. Select `Web` and enter `https://localhost/login/authorized` for the `Redirect URI` and click `Configure`.
  
  7. Next, in the left-hand navigation pane, select `Certificates & secrets`.
  6. Click `New client secret` and create a secret key. You may use any description. Click `Add`. Make sure to copy the secret key somewhere before leaving the page as you will not be able to view it again.
  7. In the left-hand navigation pane, select `Overview`. Copy the `application (client) id` and the `secret key` from the previous step to `~/.config/tod0/keys.yml`. 
  
