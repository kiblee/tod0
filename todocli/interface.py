#!/usr/bin/env python
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
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
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea

from todocli import auth

# Colors
color_folder = "bg:#006699"
color_task = "bg:#006699"

focus_index_folder = 0
focus_index_task = 0
focus_folder = True

# Confirmation stuff
waiting_for_confirmation = False


@Condition
def is_not_waiting_for_confirmation():
    "Enable key bindings when not waiting for confirmation"
    return not waiting_for_confirmation


# Global data structures to hold info
folder2id = {}
folders = []
task2id = {}
tasks = []


def load_folders():
    """
    Load all folders
    """
    global left_window
    global focus_index_folder
    global folder2id
    global folders

    # Reset all folder data structures
    focus_index_folder = 0
    folder2id.clear()
    folders.clear()

    # Retrieve folder data
    folder_data = auth.list_and_update_folders()
    for idx, f in enumerate(folder_data):
        folder2id[idx] = f["id"]
        folders.append(f["name"])

    # Layout interface
    left_window.children = [
        Window(FormattedTextControl(f), height=1, width=50) for f in folders
    ]

    # Highlight first folder
    left_window.children[0].style = color_folder


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


@kb.add("j")
def _(event):
    """
    Move selection down 1
    """

    if focus_folder:
        global focus_index_folder
        folder_window = left_window.children
        folder_window[focus_index_folder].style = ""
        focus_index_folder = (focus_index_folder + 1) % len(folders)
        folder_window[focus_index_folder].style = color_folder
    else:
        global focus_index_task
        if tasks:
            tasks[focus_index_task].style = ""
            focus_index_task = (focus_index_task + 1) % len(tasks)
            tasks[focus_index_task].style = color_task


@kb.add("k")
def _(event):
    """
    Move selection up 1
    """

    if focus_folder:
        global focus_index_folder
        folder_window = left_window.children
        folder_window[focus_index_folder].style = ""
        focus_index_folder = (focus_index_folder - 1) % len(folders)
        folder_window[focus_index_folder].style = color_folder
    else:
        global focus_index_task
        if tasks:
            tasks[focus_index_task].style = ""
            focus_index_task = (focus_index_task - 1) % len(tasks)
            tasks[focus_index_task].style = color_task


@kb.add("l")
def _(event):
    """
    Select currently focused folder
    """
    if focus_folder:
        load_tasks()


@kb.add("h")
def _(event):
    """
    Go back to folder scroll mode
    """
    global focus_index_task
    global focus_folder
    global right_window

    if tasks:
        tasks[focus_index_task].style = ""
    right_window.children = [Window()]
    focus_folder = True


@kb.add("c")
def _(event):
    """
    Mark task as complete
    """

    # Only receive input on task view mode
    if focus_folder or (not focus_folder and not tasks):
        return

    global waiting_for_confirmation
    global prompt_window

    waiting_for_confirmation = True

    input_field = TextArea(
        height=1,
        prompt="Mark task as complete? <y> to confirm. ",
        style="class:input-field",
        multiline=False,
        wrap_lines=False,
    )

    # Confirmation of commands
    def confirm(buff):
        global waiting_for_confirmation
        global prompt_window
        user_input = input_field.text
        if user_input == "y":
            # Mark task as complete
            auth.complete_task(task2id[focus_index_task])
            load_tasks()

        # Return to normal state
        waiting_for_confirmation = False
        prompt_window = Window()

    input_field.accept_handler = confirm

    prompt_window = input_field
    event.app.layout.focus(input_field)


@kb.add("n")
def _(event):
    """
    Create new task/folder
    """
    global waiting_for_confirmation
    global prompt_window

    waiting_for_confirmation = True

    # Check if we are creating new task or folder
    if focus_folder:
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
            global waiting_for_confirmation
            global prompt_window
            global left_window

            user_input = input_field.text
            if user_input:
                # Create new folder
                auth.create_folder(user_input)
                # Refresh folders
                load_folders()

            # Return to normal state
            waiting_for_confirmation = False
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
            global waiting_for_confirmation
            global prompt_window
            user_input = input_field.text
            if user_input:
                # Create new task
                auth.create_task(user_input, folder2id[focus_index_folder])
                # Refresh tasks
                load_tasks()

            # Return to normal state
            waiting_for_confirmation = False
            prompt_window = Window()

    input_field.accept_handler = get_name

    prompt_window = input_field
    event.app.layout.focus(input_field)


@kb_escape.add("escape", eager=True)
def _(event):
    """
    Escape prompt
    """
    global waiting_for_confirmation
    global prompt_window

    # Return to normal state
    waiting_for_confirmation = False
    prompt_window = Window()


kb = ConditionalKeyBindings(kb, is_not_waiting_for_confirmation)


def load_tasks():
    """
    Load tasks of currently focused folder
    """

    global focus_folder
    global focus_index_task
    global tasks
    global task2id

    task_data = auth.list_tasks(all_=False, folder=folder2id[focus_index_folder])

    tasks = []
    for idx, t in enumerate(task_data):
        id_ = t["id"]
        subject = t["subject"]
        status = t["status"]
        folder_id = t["parentFolderId"]
        tasks.append(Window(FormattedTextControl(subject), height=1))
        task2id[idx] = id_

    # Add empty container if task list is empty
    if not tasks:
        right_window.children = [Window(FormattedTextControl("-- No Tasks --"))]
    else:
        right_window.children = tasks
        focus_index_task = 0
        tasks[focus_index_task].style = color_task
    focus_folder = False


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
