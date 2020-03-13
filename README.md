tod0
====

A Terminal Client for Microsoft To-Do.

[![CircleCI](https://circleci.com/gh/kiblee/tod0.svg?style=svg&circle-token=7c223e0b25b7428107e841926315e74478cacb55)](https://circleci.com/gh/kiblee/tod0)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

#### Microsoft To Do Command Line Interface

`tod0` lets you use [Microsoft To Do](https://todo.microsoft.com/) from the command line. 

<p align="center"><img src="/demo-min.gif?raw=true"/></p>

Installation
------------

***Remember to [register for an API key](https://github.com/kiblee/tod0/tree/master/GET_KEY.md) before using `tod0`***

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
Run `tod0` from anywhere on your terminal.

    j       Move selection down
    k       Move selection up
    l       Select folder and view tasks
    h       Go back to folder
    
    n       Create task/folder
    c       Mark task as complete
 

Features
--------
- View folders and tasks
- Create folders and tasks
- Mark tasks as complete
