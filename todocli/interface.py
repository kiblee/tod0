from yaspin import yaspin

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
    VerticalAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea

from todocli.graphapi import wrapper, oauth
from todocli.utils import update_checker


class Tod0GUI:
    """
    GUI for tod0 that runs in the terminal.
    """

    # Colors
    COLOR_LIST = "bg:#006699"
    COLOR_TASK = "bg:#006699"

    # Num tasks to display for pagination
    NUM_TASKS_PER_PAGE = 10

    # This flag is used to direct user input to confirmation prompt
    is_waiting_prompt = False

    def __init__(self):
        # Check for updates
        update_checker.check()

        # Check if user is authenticated
        oauth.get_token()

        # Tracking where focus is
        self.list_focus_idx = 0
        self.task_focus_idx = 0
        self.is_focus_on_list = True

        # Global data structures for ui
        self.lists = []
        self.tasks_ui = []
        self.tasks = []

        # UI
        self.DEFAULT_PROMPT_WINDOW = TextArea(
            height=1,
            prompt="",
            style="class:input-field",
            multiline=False,
            wrap_lines=False,
        )

        self.prompt_window = self.DEFAULT_PROMPT_WINDOW
        self.left_window = HSplit([Window()], align=VerticalAlign.TOP, padding=0)
        self.right_window = HSplit([Window()], align=VerticalAlign.TOP, padding=0)

        # Load lists
        self.load_lists()

        # Creating an `Application` instance
        self.application = Application(
            layout=self.create_layout(),
            key_bindings=merge_key_bindings(self.get_key_bindings()),
            mouse_support=False,
            full_screen=False,
        )

        self.application.run()

    def create_layout(self):
        body = VSplit(
            [
                self.left_window,
                Window(width=1, char="|", style="class:line"),
                self.right_window,
            ],
            padding=1,
        )

        root_container = HSplit(
            [
                # The titlebar.
                DynamicContainer(lambda: self.prompt_window),
                Window(
                    height=1,
                    content=FormattedTextControl([("class:title", " tod0 ")]),
                    align=WindowAlign.CENTER,
                ),
                # Horizontal separator.
                Window(height=1, char="-", style="class:line"),
                body,
                Window(height=1, char=".", style="class:line"),
            ]
        )

        return Layout(root_container)

    def load_lists(self):
        """
        Load all lists
        """

        # Reset all folder data structures
        self.list_focus_idx = 0

        # Retrieve folder data
        with yaspin(text="Loading lists") as sp:
            self.lists = wrapper.get_lists()

        # Layout interface
        self.left_window.children = [
            Window(FormattedTextControl(f.display_name), width=50) for f in self.lists
        ]

        # Highlight first folder
        self.left_window.children[self.list_focus_idx].style = Tod0GUI.COLOR_LIST

    def load_tasks(self):
        """
        Load tasks of currently focused folder
        """

        selected_list = self.lists[self.list_focus_idx]

        with yaspin(text="Loading tasks") as sp:
            self.tasks = wrapper.get_tasks(list_id=selected_list.id, num_tasks=100)

        self.tasks_ui.clear()
        for idx, t in enumerate(self.tasks):
            _task_ui = VSplit(
                [
                    Window(FormattedTextControl(t.title), wrap_lines=True, height=2),
                    Window(width=5),
                    Window(
                        FormattedTextControl(
                            f"Created: {t.created_datetime}\nReminder: {t.reminder_datetime}"
                        ),
                        width=30,
                    ),
                ],
            )
            self.tasks_ui.append(_task_ui)

        # Add empty container if task list is empty
        if not self.tasks_ui:
            self.right_window.children = [
                Window(FormattedTextControl("-- No Tasks --"))
            ]
        else:
            self.right_window.children = [
                t for t in self.tasks_ui[0 : Tod0GUI.NUM_TASKS_PER_PAGE]
            ]
            self.task_focus_idx = 0
            self.tasks_ui[self.task_focus_idx].style = Tod0GUI.COLOR_TASK
        self.is_focus_on_list = False

    def reset_prompt_window(self):
        self.prompt_window = self.DEFAULT_PROMPT_WINDOW
        self.application.layout.focus(self.prompt_window)
        Tod0GUI.is_waiting_prompt = False

    """
    Key Bindings
    """

    def get_key_bindings(self):
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
            Tod0GUI.is_waiting_prompt = True

            input_field = TextArea(
                height=1,
                prompt="[UP: j] [DOWN: k] [SELECT: l] [BACK: h] [CREATE: n] [MARK COMPLETE: c] [EXIT HELP: ESC]",
                style="class:output-field",
                multiline=False,
                wrap_lines=False,
            )

            self.prompt_window = input_field
            event.app.layout.focus(input_field)

        @kb.add("j")
        def _(event):
            """
            Move selection down 1
            """
            if self.is_focus_on_list:
                list_window = self.left_window.children
                list_window[self.list_focus_idx].style = ""
                self.list_focus_idx = (self.list_focus_idx + 1) % len(self.lists)
                list_window[self.list_focus_idx].style = Tod0GUI.COLOR_LIST
            else:
                if self.tasks_ui:
                    self.tasks_ui[self.task_focus_idx].style = ""

                    # If we're at end of task list
                    if self.task_focus_idx == len(self.tasks_ui) - 1:
                        # Do nothing
                        pass
                    # If we're at end of paginated page
                    elif (
                        self.task_focus_idx % Tod0GUI.NUM_TASKS_PER_PAGE
                        == Tod0GUI.NUM_TASKS_PER_PAGE - 1
                    ):
                        # Load next paginated page
                        self.task_focus_idx += 1
                        page_tasks = self.tasks_ui[
                            self.task_focus_idx : self.task_focus_idx
                            + Tod0GUI.NUM_TASKS_PER_PAGE
                        ]
                        self.right_window.children = page_tasks
                    # We're in the middle of paginated page
                    else:
                        # Go down one row
                        self.task_focus_idx += 1

                    # Highlight correct task
                    self.tasks_ui[self.task_focus_idx].style = Tod0GUI.COLOR_TASK

        @kb.add("k")
        def _(event):
            """
            Move selection up 1
            """

            if self.is_focus_on_list:
                list_window = self.left_window.children
                list_window[self.list_focus_idx].style = ""
                self.list_focus_idx = (self.list_focus_idx - 1) % len(self.lists)
                list_window[self.list_focus_idx].style = Tod0GUI.COLOR_LIST
            else:
                if self.tasks_ui:
                    self.tasks_ui[self.task_focus_idx].style = ""

                    # If we're at start of task list
                    if self.task_focus_idx == 0:
                        # Do nothing
                        pass
                    # If we're at start of paginated page
                    elif self.task_focus_idx % Tod0GUI.NUM_TASKS_PER_PAGE == 0:
                        # Load previous paginated page
                        page_tasks = self.tasks_ui[
                            self.task_focus_idx
                            - Tod0GUI.NUM_TASKS_PER_PAGE : self.task_focus_idx
                        ]
                        self.task_focus_idx -= 1
                        self.right_window.children = page_tasks
                    # If we're in the middle of paginated page
                    else:
                        # Go up one row
                        self.task_focus_idx -= 1

                    # Highlight correct task
                    self.tasks_ui[self.task_focus_idx].style = Tod0GUI.COLOR_TASK

        @kb.add("l")
        def _(event):
            """
            Select currently focused list
            """
            if self.is_focus_on_list:
                self.load_tasks()

        @kb.add("h")
        def _(event):
            """
            Go back to list scroll mode
            """
            self.right_window.children = [Window()]
            self.is_focus_on_list = True

        @kb.add("c")
        def _(event):
            """
            Mark task as complete
            """

            # Only receive input on task view mode
            if self.is_focus_on_list or (
                not self.is_focus_on_list and not self.tasks_ui
            ):
                return

            Tod0GUI.is_waiting_prompt = True

            input_field = TextArea(
                height=1,
                prompt="Mark task as complete? <y> to confirm. ",
                style="class:input-field",
                multiline=False,
                wrap_lines=False,
            )

            # Confirmation of commands
            def confirm(buff):
                user_input = input_field.text
                if user_input == "y":
                    # Mark task as complete
                    with yaspin(text="Marking as complete") as sp:
                        wrapper.complete_task(
                            list_id=self.lists[self.list_focus_idx].id,
                            task_id=self.tasks[self.task_focus_idx].id,
                        )

                    self.load_tasks()
                    # self.refresh_layout()

                # Return to normal state
                Tod0GUI.is_waiting_prompt = False
                self.reset_prompt_window()

            input_field.accept_handler = confirm

            self.prompt_window = input_field
            event.app.layout.focus(input_field)

        @kb.add("n")
        def _(event):
            """
            Create new task/list
            """
            Tod0GUI.is_waiting_prompt = True

            # Check if we are creating new task or list
            if self.is_focus_on_list:
                # We are creating a new list
                input_field = TextArea(
                    height=1,
                    prompt="New list: ",
                    style="class:input-field",
                    multiline=False,
                    wrap_lines=False,
                )

                # Get new list name
                def get_name(buff):
                    user_input = input_field.text
                    if user_input:
                        # Create new list
                        with yaspin(text="Creating new list") as sp:
                            wrapper.create_list(user_input)
                        # Refresh lists
                        self.load_lists()

                    # Return to normal state
                    self.reset_prompt_window()

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
                    user_input = input_field.text
                    if user_input:
                        # Create new task
                        with yaspin(text="Creating new task") as sp:
                            wrapper.create_task(
                                user_input, list_id=self.lists[self.list_focus_idx].id
                            )
                        # Refresh tasks
                        self.load_tasks()

                    # Return to normal state
                    self.reset_prompt_window()

            input_field.accept_handler = get_name

            self.prompt_window = input_field
            event.app.layout.focus(input_field)

        @kb_escape.add("escape", eager=True)
        def _(event):
            """
            Escape prompt
            """
            # Return to normal state
            self.reset_prompt_window()

        @Condition
        def is_not_waiting_for_confirmation():
            "Enable key bindings when not waiting for confirmation"
            return not Tod0GUI.is_waiting_prompt

        kb = ConditionalKeyBindings(kb, is_not_waiting_for_confirmation)

        return (kb, kb_exit, kb_escape)


def run():
    Tod0GUI()
