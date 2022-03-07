#!/usr/bin/env python
from asyncio import tasks
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import (
    KeyBindings,
    ConditionalKeyBindings,
    merge_key_bindings,
)
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import (
    HSplit,
    VSplit,
    Window,
    WindowAlign,
    DynamicContainer,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea

import todocli.graphapi.todo_api as todo_api

# Colors
COLOR_FOLDER = "bg:#006699"
COLOR_TASK = "bg:#006699"

global_focus_index_folder = 0
global_focus_index_task = 0
global_focus_on_folder = True

# This flag is used to direct user input to confirmation prompt
global_waiting_confirmation = False

# Global data structures for ui
global_folder2id = {}
global_folders = []
global_task2id = {}
global_tasks_ui = []
global_tasks = []


def load_folders():
    """
    Load all folders
    """
    global left_window
    global global_focus_index_folder
    global global_folder2id
    global global_folders

    # Reset all folder data structures
    global_focus_index_folder = 0
    global_folder2id.clear()
    global_folders.clear()

    # Retrieve folder data
    lists = todo_api.query_lists()
    for idx, _list in enumerate(lists):
        global_folder2id[idx] = _list.id
        global_folders.append(_list.display_name)

    # Layout interface
    left_window.children = [
        Window(FormattedTextControl(f), height=1, width=50) for f in global_folders
    ]

    # Highlight first folder
    left_window.children[0].style = COLOR_FOLDER


left_window = HSplit([Window()])

# Get folders to load on screen
load_folders()

right_window = HSplit([Window()])
body = VSplit(
    [
        left_window,
        Window(width=1, char="|", style="class:line"),
        right_window,
    ]
)


def get_titlebar_text():
    return [("class:title", " tod0 ")]


prompt_window = Window(
    height=1, content=FormattedTextControl(""), align=WindowAlign.LEFT
)

root_container = HSplit(
    [
        # The titlebar.
        Window(
            height=1,
            content=FormattedTextControl(get_titlebar_text),
            align=WindowAlign.CENTER,
        ),
        # Horizontal separator.
        Window(height=1, char="-", style="class:line"),
        # The 'body', like defined above.
        body,
        Window(height=1, char=".", style="class:line"),
        DynamicContainer(lambda: prompt_window),
    ]
)


# Key bindings
kb = KeyBindings()
kb_exit = KeyBindings()
kb_escape = KeyBindings()


@kb_exit.add("c-c", eager=True)
@kb_exit.add("c-q", eager=True)
def _(event):
    """
    Pressing Ctrl-Q or Ctrl-C will exit the user interface.
    """
    event.app.exit()


@kb.add("?")
def _(event):
    """
    Pressing Shift-? will display help toolbar.
    """
    global global_waiting_confirmation
    global prompt_window

    global_waiting_confirmation = True

    input_field = TextArea(
        height=1,
        prompt="[UP: j] [DOWN: k] [SELECT: l] [BACK: h] [CREATE: n] [MARK COMPLETE: c] [EXIT HELP: ESC]",
        style="class:output-field",
        multiline=False,
        wrap_lines=False,
    )

    prompt_window = input_field
    event.app.layout.focus(input_field)


@kb.add("j")
def _(event):
    """
    Move selection down 1
    """

    if global_focus_on_folder:
        global global_focus_index_folder
        folder_window = left_window.children
        folder_window[global_focus_index_folder].style = ""
        global_focus_index_folder = (global_focus_index_folder + 1) % len(
            global_folders
        )
        folder_window[global_focus_index_folder].style = COLOR_FOLDER
    else:
        global global_focus_index_task
        if global_tasks_ui:
            global_tasks_ui[global_focus_index_task].style = ""
            global_focus_index_task = (global_focus_index_task + 1) % len(
                global_tasks_ui
            )
            global_tasks_ui[global_focus_index_task].style = COLOR_TASK


@kb.add("k")
def _(event):
    """
    Move selection up 1
    """

    if global_focus_on_folder:
        global global_focus_index_folder
        folder_window = left_window.children
        folder_window[global_focus_index_folder].style = ""
        global_focus_index_folder = (global_focus_index_folder - 1) % len(
            global_folders
        )
        folder_window[global_focus_index_folder].style = COLOR_FOLDER
    else:
        global global_focus_index_task
        if global_tasks_ui:
            global_tasks_ui[global_focus_index_task].style = ""
            global_focus_index_task = (global_focus_index_task - 1) % len(
                global_tasks_ui
            )
            global_tasks_ui[global_focus_index_task].style = COLOR_TASK


@kb.add("l")
def _(event):
    """
    Select currently focused folder
    """
    if global_focus_on_folder:
        load_tasks()


@kb.add("h")
def _(event):
    """
    Go back to folder scroll mode
    """
    global global_focus_index_task
    global global_focus_on_folder
    global right_window

    if global_tasks_ui:
        global_tasks_ui[global_focus_index_task].style = ""
    right_window.children = [Window()]
    global_focus_on_folder = True


@kb.add("c")
def _(event):
    """
    Mark task as complete
    """

    # Only receive input on task view mode
    if global_focus_on_folder or (not global_focus_on_folder and not global_tasks_ui):
        return

    global global_waiting_confirmation
    global prompt_window
    global global_tasks

    global_waiting_confirmation = True

    input_field = TextArea(
        height=1,
        prompt="Mark task as complete? <y> to confirm. ",
        style="class:input-field",
        multiline=False,
        wrap_lines=False,
    )

    # Confirmation of commands
    def confirm(buff):
        global global_waiting_confirmation
        global prompt_window
        user_input = input_field.text
        if user_input == "y":
            # Mark task as complete
            todo_api.complete_task(
                global_folders[global_focus_index_folder],
                global_tasks[global_focus_index_task].title,
            )
            load_tasks()

        # Return to normal state
        global_waiting_confirmation = False
        prompt_window = Window()

    input_field.accept_handler = confirm

    prompt_window = input_field
    event.app.layout.focus(input_field)


@kb.add("n")
def _(event):
    """
    Create new task/folder
    """
    global global_waiting_confirmation
    global prompt_window

    global_waiting_confirmation = True

    # Check if we are creating new task or folder
    if global_focus_on_folder:
        # We are creating a new folder
        input_field = TextArea(
            height=1,
            prompt="New folder: ",
            style="class:input-field",
            multiline=False,
            wrap_lines=False,
        )

        # Get new folder name
        def get_name(buff):
            global global_waiting_confirmation
            global prompt_window
            global left_window

            user_input = input_field.text
            if user_input:
                # Create new folder
                todo_api.create_list(user_input)
                # Refresh folders
                load_folders()

            # Return to normal state
            global_waiting_confirmation = False
            prompt_window = Window()

    else:
        # We are creating a new task
        input_field = TextArea(
            height=1,
            prompt="New task: ",
            style="class:input-field",
            multiline=False,
            wrap_lines=False,
        )

        # Get new task name
        def get_name(buff):
            global global_waiting_confirmation
            global prompt_window
            user_input = input_field.text

            if user_input:
                # Create new task
                todo_api.create_task(
                    user_input, global_folders[global_focus_index_folder]
                )
                # Refresh tasks
                load_tasks()

            # Return to normal state
            global_waiting_confirmation = False
            prompt_window = Window()

    input_field.accept_handler = get_name

    prompt_window = input_field
    event.app.layout.focus(input_field)


@kb_escape.add("escape", eager=True)
def _(event):
    """
    Escape prompt
    """
    global global_waiting_confirmation
    global prompt_window

    # Return to normal state
    global_waiting_confirmation = False
    prompt_window = Window()


@Condition
def is_not_waiting_for_confirmation():
    "Enable key bindings when not waiting for confirmation"
    return not global_waiting_confirmation


kb = ConditionalKeyBindings(kb, is_not_waiting_for_confirmation)


def load_tasks():
    """
    Load tasks of currently focused folder
    """

    global global_focus_on_folder
    global global_focus_index_task
    global global_tasks_ui
    global global_task2id
    global global_tasks

    folder_name = global_folders[global_focus_index_folder]
    global_tasks = todo_api.query_tasks(folder_name, num_tasks=100)

    global_tasks_ui = []
    for idx, t in enumerate(global_tasks):
        id_ = t.id
        title = t.title
        global_tasks_ui.append(Window(FormattedTextControl(title), height=1))
        global_task2id[idx] = id_

    # Add empty container if task list is empty
    if not global_tasks_ui:
        right_window.children = [Window(FormattedTextControl("-- No Tasks --"))]
    else:
        right_window.children = global_tasks_ui
        global_focus_index_task = 0
        global_tasks_ui[global_focus_index_task].style = COLOR_TASK
    global_focus_on_folder = False


# Creating an `Application` instance
# ----------------------------------
application = Application(
    layout=Layout(root_container),
    key_bindings=merge_key_bindings([kb, kb_exit, kb_escape]),
    mouse_support=False,
    full_screen=False,
)


# Run the application
# -------------------
def run():
    application.run()


if __name__ == "__main__":
    run()
