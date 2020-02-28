#!/usr/bin/env python
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout

from todocli import auth

# Colors
color_folder = "bg:#006699"

focus_index_folder = 0
focus_index_task = 0
focus_folder = True


# Get list of folders
folder2id = {}
folders = []
tasks = []

folder_data = auth.list_and_update_folders()
for idx, f in enumerate(folder_data):
    folder2id[f["name"]] = f["id"]
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
    return [
        ("class:title", " tod0 "),
    ]


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
    ]
)


# Key bindings
kb = KeyBindings()


@kb.add("c-c", eager=True)
@kb.add("c-q", eager=True)
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
        tasks[focus_index_task].style = color_folder


@kb.add("k")
def _(event):
    """
    Move folder selection up 1
    """
    global focus_index_folder
    folders[focus_index_folder].style = ""
    focus_index_folder = (focus_index_folder - 1) % len(folders)
    # event.app.layout.focus(task_categories[focus_index_folder])
    folders[focus_index_folder].style = color_folder


@kb.add("c-m")
@kb.add("l")
def _(event):
    """
    Select currently focused folder
    """

    global focus_folder
    global tasks

    task_data = auth.list_tasks(
        all_=False, folder=folder2id[folders[focus_index_folder].content.text]
    )

    # results = {}
    tasks = []
    for idx, t in enumerate(task_data):
        id_ = t["id"]
        subject = t["subject"]
        status = t["status"]
        folder_id = t["parentFolderId"]
        tasks.append(Window(FormattedTextControl(subject), height=1))

    # Add empty container if task list is empty
    if not tasks:
        right_window.children = [Window(FormattedTextControl("-- No Tasks --"))]
    else:
        right_window.children = tasks
        # tasks[0].style="bg:#aabbcc"

    # focus_folder = False

    # results[str(idx)] = t


# Creating an `Application` instance
# ----------------------------------
application = Application(
    layout=Layout(root_container),
    key_bindings=kb,
    mouse_support=False,
    full_screen=False,
)


# Run the application
# -------------------
def run():
    application.run()


if __name__ == "__main__":
    run()
