from todocli.odata_system_query import ODataSystemQuery

base_api_url = "https://graph.microsoft.com/v1.0/me/todo"


def _lists():
    return "{}/lists".format(base_api_url)


def _list(todo_task_list_id):
    return "{}/lists/{}".format(base_api_url, todo_task_list_id)


def _tasks(todo_task_list_id):
    return "{}/lists/{}/tasks".format(base_api_url, todo_task_list_id)


def _task(todo_task_list_id, task_id):
    return "{}/lists/{}/tasks/{}".format(base_api_url, todo_task_list_id, task_id)


def new_list():
    return _lists()


def modify_list(todo_task_list_id):
    return _list(todo_task_list_id)


def get_all_lists():
    return _lists()


def get_list_by_name(list_name):
    return (
        _lists() + ODataSystemQuery().filter_startsWith("displayName", list_name).get()
    )


def delete_list(todo_task_list_id):
    return _list(todo_task_list_id)


def new_task(todo_task_list_id):
    return _tasks(todo_task_list_id)


def modify_task(todo_task_list_id, task_id):
    return _task(todo_task_list_id, task_id)


def get_tasks(todo_task_list_id, num_tasks: int, include_completed=False):
    query = ODataSystemQuery()

    if not include_completed:
        query.filter_ne("status", "completed")

    return _tasks(todo_task_list_id) + query.top(num_tasks).get()


def get_task_by_name(todo_task_list_id, task_name: str):
    return (
        _tasks(todo_task_list_id)
        + ODataSystemQuery().filter_eq("title", task_name).get()
    )


def delete_task(todo_task_list_id, task_id):
    return _task(todo_task_list_id, task_id)
