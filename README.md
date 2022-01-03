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
For the UI client, run `tod0` from anywhere on your terminal.

    j       Move selection down
    k       Move selection up
    l       Select folder and view tasks
    h       Go back to folder
    
    n       Create task/folder
    c       Mark task as complete

    ?       Display help
    
For the CLI client, run `todocli` from anywhere on your terminal.
Usage:

    NAME
        todocli - Command line client for Microsoft ToDo 
        
    SYNOPSIS
        todocli [options] COMMAND ...  
        
        'COMMAND' can be one of the following values:
            ls                  Display all lists  
            
            lst <list_name>     Display all tasks from list
                list_name       Name of the list
                
            new <task> [-r time]
                                Create a new task
                task            Task to create. See 'Specifying a task' for details.
                -r time         Set a reminder. See 'Specifying time' for details.              
            
            newl <list_name>    Create a new list
                list_name       Name of the list
                
            complete <task>     Set task status to completed
                task            Task to complete. See 'Specifying a task' for details.
               
            rm <task>           Remove a task
                task            Task to remove. See 'Specifying a task' for details.
                   
    OPTIONS
        -h, --help
            Display a usage message.
        
        -i, --interactive
            Interactive mode. 
            Don't exit after invoking a command, but ask for follow up commands instead.
        
        -n, --display_linenums
            Display a line number for all lines which are output.
            
    Specifying a task:
        For commands which take 'task' as a parameter, 'task' can be one of the following:
        
        task_name
        list_name/task_name
        task_number
        list_name/task_number
        
        If 'list_name' is omitted, the default task list will be used. 
        'task_number' is the position displayed when specifying option '-n'. 
       
    Specifying time:
        For options which take 'time' as a parameter, 'time' can be one of the following:
        
        {n}h
            Current time + n hours. 
            e.g. 1h, 12h. 
            Max: 99h
            
        morning
            Today at 07:00 AM if current time < 07:00 AM, otherwise tomorrow

        tomorrow
            Tomorrow at 07:00 AM
            
        evening
            Today at 06:00 PM if current time < 06:00 PM, otherwise tomorrow
            
        {hour}:{minute}
            Today at {hour}:{minute} if current time < {hour}:{minute}, otherwise tomorrow 
            e.g. 9:30, 09:30, 17:15
            
        {hour}:{minute} am|pm 
            Today at {hour}:{minute} am|pm  if current time < {hour}:{minute} am|pm, otherwise tomorrow
            e.g. 9:30 am, 12:00 am, 10:15 pm
            
        {day}.{month}. {hour}:{minute}
            The given day at {hour}:{minute}
            e.g. 24.12. 12:00
            e.g. 7.4.   9:15
        
        {day}.{month}.{year}
            The given day at 7:00 am
            e.g. 22.12.2020
            e.g. 01.01.21
    
Features
--------
- View folders and tasks
- Create folders and tasks
- Mark tasks as complete
