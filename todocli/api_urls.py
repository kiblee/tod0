base_api_url = "https://graph.microsoft.com/v1.0/me/todo"

def newTask(todoTaskListId):
    return "{}/lists/{}/tasks".format(base_api_url, todoTaskListId)


def newList():
    return "{}/lists".format(base_api_url)


def queryLists():
    return newList()


def modifyList(todoTaskListId):
    return "{}/lists/{}".format(base_api_url, todoTaskListId)

def modifyTask(todoTaskListId, taskId):
    return "{}/lists/{}/tasks/{}".format(base_api_url, todoTaskListId, taskId)


def queryTasksFromList(todoTaskListId, num_tasks: int):
    return newTask(todoTaskListId) + "?$filter=status ne 'completed'&$top={}".format(num_tasks)

def modifyTask(todoTaskListId, taskId):
    return "{}/lists/{}/tasks/{}".format(base_api_url, todoTaskListId, taskId)
