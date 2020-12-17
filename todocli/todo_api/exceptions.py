class ListNotFound(Exception):
    def __init__(self, list_name):
        self.message = "List with name '{}' could not be found".format(list_name)
        super(ListNotFound, self).__init__(self.message)


class TaskNotFoundByName(Exception):
    def __init__(self, task_name, list_name):
        self.message = "Task with name '{}' could not be found in list '{}'".format(
            task_name, list_name
        )
        super(TaskNotFoundByName, self).__init__(self.message)


class TaskNotFoundByIndex(Exception):
    def __init__(self, task_index, list_name):
        self.message = "Task with index '{}' could not be found in list '{}'".format(
            task_index, list_name
        )
        super(TaskNotFoundByIndex, self).__init__(self.message)
