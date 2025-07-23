from datetime import datetime, timezone
from todocli.utils.datetime_util import parse_datetime
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
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.widgets import TextArea

from todocli.graphapi import wrapper, oauth
from todocli.utils import update_checker

DATETIME_FORMAT = "%Y-%m-%d %H:%M"


class TaskUI(VSplit):
    def __init__(self, task):
        self.task = task
        self.title = FormattedTextControl("", focusable=True)
        self.marked = False

        reminder_text = [
            ("", f"Created: {task.created_datetime.strftime(DATETIME_FORMAT)}"),
        ]

        reminder = task.reminder_datetime or task.due_datetime
        if reminder:
            color = (
                "#ff0000" if reminder and reminder < datetime.now(timezone.utc) else ""
            )
            reminder_text.extend(
                [
                    ("", f"\nReminder: "),
                    (color, reminder.strftime(DATETIME_FORMAT)),
                ]
            )

        super().__init__(
            [
                Window(self.title, wrap_lines=True, height=2),
                Window(width=5),
                Window(
                    FormattedTextControl(reminder_text),
                    width=30,
                ),
            ],
        )

        self.mark(False)

    def mark(self, value=None):
        if value is not None:
            self.marked = value
        else:
            self.marked = not self.marked
        self.title.text = f"{'*' if self.marked else ' '}{self.task.title}"


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
        self.right_window = ScrollablePane(
            HSplit([Window()], align=VerticalAlign.TOP, padding=0)
        )

        # Load lists
        self.load_lists()

        # Creating an `Application` instance
        self.application = Application(
            layout=self.create_layout(),
            key_bindings=merge_key_bindings(self.get_key_bindings()),
            mouse_support=False,
            full_screen=True,
        )

        try:
            # try disbling paste recognition
            self.application.input.console_input_reader.recognize_paste = False
        except AttributeError:
            pass

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
            self.tasks.sort(
                key=lambda x: x.reminder_datetime
                or x.due_datetime
                or x.created_datetime
            )

        self.tasks_ui.clear()
        for idx, t in enumerate(self.tasks):
            self.tasks_ui.append(TaskUI(t))

        # Add empty container if task list is empty
        if not self.tasks_ui:
            self.right_window.content.children = [
                Window(FormattedTextControl("-- No Tasks --"))
            ]
        else:
            if self.task_focus_idx >= len(self.tasks_ui):
                self.task_focus_idx = len(self.tasks_ui) - 1
            self.right_window.content.children = self.tasks_ui
            self.tasks_ui[self.task_focus_idx].style = Tod0GUI.COLOR_TASK
        self.is_focus_on_list = False

    def reset_prompt_window(self):
        self.prompt_window = self.DEFAULT_PROMPT_WINDOW
        self.application.layout.focus(self.prompt_window)
        Tod0GUI.is_waiting_prompt = False

    def prompt(self, *messages, callback=None):
        messages_list = [*messages]

        if not callable(callback):
            raise ValueError("callback must be a function")

        result = []

        def loop():
            if not messages_list:
                callback(*result)
                return

            Tod0GUI.is_waiting_prompt = True

            input_field = TextArea(
                height=1,
                prompt=messages_list.pop(0),
                style="class:input-field",
                multiline=False,
                wrap_lines=False,
            )

            def handler(_):
                self.reset_prompt_window()
                result.append(input_field.text)
                loop()

            input_field.accept_handler = handler

            self.prompt_window = input_field
            self.application.layout.focus(input_field)

        loop()

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

        def move_selection(direction):
            if self.is_focus_on_list:
                list_window = self.left_window.children
                list_window[self.list_focus_idx].style = ""
                next_idx = self.list_focus_idx + direction
                next_idx = next_idx % len(self.lists)  # loop through list
                self.list_focus_idx = next_idx
                list_window[self.list_focus_idx].style = Tod0GUI.COLOR_LIST
            else:
                if self.tasks_ui:
                    self.tasks_ui[self.task_focus_idx].style = ""
                    next_idx = self.task_focus_idx + direction
                    next_idx = min(
                        next_idx, len(self.tasks_ui) - 1
                    )  # Don't go out of bounds
                    next_idx = max(next_idx, 0)  # Don't go below 0
                    self.task_focus_idx = next_idx
                    # Highlight correct task
                    self.tasks_ui[self.task_focus_idx].style = Tod0GUI.COLOR_TASK
                    self.application.layout.focus(
                        self.tasks_ui[self.task_focus_idx].children[0].content
                    )

        @kb.add("j")
        def _(event):
            """
            Move selection down 1
            """
            move_selection(1)

        @kb.add("k")
        def _(event):
            """
            Move selection up 1
            """
            move_selection(-1)

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
            self.right_window.content.children = [Window()]
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
                        # find marked tasks
                        marked_tasks = [t for t in self.tasks_ui if t.marked]
                        if not marked_tasks:
                            wrapper.complete_task(
                                list_id=self.lists[self.list_focus_idx].id,
                                task_id=self.tasks[self.task_focus_idx].id,
                            )
                        else:
                            wrapper.complete_tasks(
                                list_id=self.lists[self.list_focus_idx].id,
                                task_ids=[task_ui.task.id for task_ui in marked_tasks],
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
            # Check if we are creating new task or list
            if self.is_focus_on_list:
                # We are creating a new list
                def get_name(user_input):
                    if user_input:
                        # Create new list
                        with yaspin(text="Creating new list") as sp:
                            wrapper.create_list(user_input)
                        # Refresh lists
                        self.load_lists()

                self.prompt("New list: ", callback=get_name)

            else:
                # We are creating a new task

                def create_task(name, reminder):
                    if not name:
                        return

                    # Create new task
                    with yaspin(text="Creating new task") as sp:
                        wrapper.create_task(
                            task_name=name,
                            list_id=self.lists[self.list_focus_idx].id,
                            reminder_datetime=(
                                None if not reminder else parse_datetime(reminder)
                            ),
                        )
                    # Refresh tasks
                    self.load_tasks()

                self.prompt("New task: ", "Reminder (optional): ", callback=create_task)

        @kb.add("t")
        def _(event):
            """
            Toggle marker
            """
            # Only receive input on task view mode
            if self.is_focus_on_list or (
                not self.is_focus_on_list and not self.tasks_ui
            ):
                return

            # Toggle marker of currently focused task
            self.tasks_ui[self.task_focus_idx].mark()
            # self.application.layout.focus(self.tasks_ui[self.task_focus_idx].children[0].content)

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
