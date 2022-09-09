#!/usr/bin/env python

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
    HorizontalAlign,
    VerticalAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea

import todocli.graphapi.wrapper as wrapper
from todocli.utils import update_checker

# Colors
COLOR_FOLDER = "bg:#006699"
COLOR_TASK = "bg:#006699"

global_focus_index_folder = 0
global_focus_index_task = 0
global_is_focus_on_folder = True

# This flag is used to direct user input to confirmation prompt
global_waiting_confirmation = False

# Global data structures for ui
global_lists = []
global_tasks_ui = []
global_tasks = []


def load_folders():
    """
    Load all folders
    """
    global left_window
    global global_focus_index_folder
    global global_lists

    # Reset all folder data structures
    global_focus_index_folder = 0

    # Retrieve folder data
    global_lists = wrapper.get_lists()

    # Layout interface
    left_window.children = [
        Window(FormattedTextControl(f.display_name), width=50) for f in global_lists
    ]

    # Highlight first folder
    left_window.children[0].style = COLOR_FOLDER


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

    if global_is_focus_on_folder:
        global global_focus_index_folder
        folder_window = left_window.children
        folder_window[global_focus_index_folder].style = ""
        global_focus_index_folder = (global_focus_index_folder + 1) % len(global_lists)
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

    if global_is_focus_on_folder:
        global global_focus_index_folder
        folder_window = left_window.children
        folder_window[global_focus_index_folder].style = ""
        global_focus_index_folder = (global_focus_index_folder - 1) % len(global_lists)
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
    if global_is_focus_on_folder:
        load_tasks()


@kb.add("h")
def _(event):
    """
    Go back to folder scroll mode
    """
    global global_focus_index_task
    global global_is_focus_on_folder
    global right_window

    if global_tasks_ui:
        global_tasks_ui[global_focus_index_task].style = ""
    right_window.children = [Window()]
    global_is_focus_on_folder = True


@kb.add("c")
def _(event):
    """
    Mark task as complete
    """

    # Only receive input on task view mode
    if global_is_focus_on_folder or (
        not global_is_focus_on_folder and not global_tasks_ui
    ):
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
            wrapper.complete_task(
                list_id=global_lists[global_focus_index_folder].id,
                task_id=global_tasks[global_focus_index_task].id,
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
    if global_is_focus_on_folder:
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
                wrapper.create_list(user_input)
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
                wrapper.create_task(
                    user_input, list_id=global_lists[global_focus_index_folder].id
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

    global global_is_focus_on_folder
    global global_focus_index_task
    global global_tasks_ui
    global global_tasks

    selected_list = global_lists[global_focus_index_folder]
    global_tasks = wrapper.get_tasks(list_id=selected_list.id, num_tasks=100)

    global_tasks_ui = []
    for idx, t in enumerate(global_tasks):
        # global_tasks_ui.append(Window(FormattedTextControl(t.title), height=1))
        _task_ui = VSplit(
            [
                Window(FormattedTextControl(t.title), wrap_lines=True, height=3),
                Window(width=5),
                Window(
                    FormattedTextControl(
                        f"Created: {t.created_datetime}\nReminder: {t.reminder_datetime}"
                    ),
                    width=30,
                ),
            ],
        )
        global_tasks_ui.append(_task_ui)

    # Add empty container if task list is empty
    if not global_tasks_ui:
        right_window.children = [Window(FormattedTextControl("-- No Tasks --"))]
    else:
        right_window.children = global_tasks_ui
        global_focus_index_task = 0
        global_tasks_ui[global_focus_index_task].style = COLOR_TASK
    global_is_focus_on_folder = False


left_window = HSplit([Window()])

# Get folders to load on screen
load_folders()

right_window = HSplit([Window()], align=VerticalAlign.TOP, padding=1)
body = VSplit(
    [
        left_window,
        Window(width=1, char="|", style="class:line"),
        right_window,
    ],
    padding=1,
    # align=HorizontalAlign.JUSTIFY,
)

prompt_window = Window(
    height=1, content=FormattedTextControl(""), align=WindowAlign.LEFT
)

root_container = HSplit(
    [
        # The titlebar.
        Window(
            height=1,
            content=FormattedTextControl([("class:title", " tod0 ")]),
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
    update_checker()
    run()
