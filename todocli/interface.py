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


# Get list of folders
folder2id = {}
folders = []
task2id = {}
tasks = []


folder_data = auth.list_and_update_folders()
for idx, f in enumerate(folder_data):
    folder2id[idx] = f["id"]
    folders.append(Window(FormattedTextControl(f["name"]), height=1, width=50))

folders[0].style = color_folder

left_window = HSplit(folders)

right_window = HSplit([Window()])

body = VSplit(
    [
        left_window,
        # A vertical line in the middle. We explicitly specify the width, to make
        # sure that the layout engine will not try to divide the whole width by
        # three for all these windows.
        Window(width=1, char="|", style="class:line"),
        # Display the Result buffer on the right.
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
        folders[focus_index_folder].style = ""
        focus_index_folder = (focus_index_folder + 1) % len(folders)
        folders[focus_index_folder].style = color_folder
    else:
        global focus_index_task
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
        folders[focus_index_folder].style = ""
        focus_index_folder = (focus_index_folder - 1) % len(folders)
        folders[focus_index_folder].style = color_folder
    else:
        global focus_index_task
        tasks[focus_index_task].style = ""
        focus_index_task = (focus_index_task - 1) % len(tasks)
        tasks[focus_index_task].style = color_task


@kb.add("l")
def _(event):
    """
    Select currently focused folder
    """
    load_tasks()


@kb.add("h")
def _(event):
    """
    Go back to folder scroll mode
    """
    global focus_index_task
    global focus_folder
    tasks[focus_index_task].style = ""
    focus_folder = True


@kb.add("c")
def _(event):
    """
    Mark task as complete
    """
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

    input_field = TextArea(
        height=1,
        prompt="New task: ",
        style="class:input-field",
        multiline=False,
        wrap_lines=False,
    )

    # Confirmation of commands
    def confirm(buff):
        global waiting_for_confirmation
        global prompt_window
        user_input = input_field.text
        if user_input:
            # Create new taske
            auth.create_task(user_input, folder2id[focus_index_folder])
            # Refresh tasks
            load_tasks()

        # Return to normal state
        waiting_for_confirmation = False
        prompt_window = Window()

    input_field.accept_handler = confirm

    prompt_window = input_field
    event.app.layout.focus(input_field)


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
    key_bindings=merge_key_bindings([kb, kb_exit]),
    mouse_support=False,
    full_screen=False,
)


# Run the application
# -------------------
def run():
    application.run()


if __name__ == "__main__":
    run()
