import asyncio
from os import access
import sys

from todocli.utils.datetime_util import parse_datetime

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings

from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import (
    HSplit,
    VSplit,
    Window,
    WindowAlign,
    VerticalAlign,
)
from prompt_toolkit.layout.controls import (
    FormattedTextControl,
    BufferControl,
    DummyControl,
)
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style

from todocli.graphapi import wrapper, oauth
from todocli.utils import update_checker


class Tod0GUI:
    """
    GUI for tod0 that runs in the terminal.
    """

    # Colors
    STYLE_ACTIVATED = "bg:#006699"

    def __init__(self):
        # Check for updates
        update_checker.check()

        # Check if user is authenticated
        oauth.get_token()

        # Tracking where focus is
        self.list_focus_idx = 0
        self.task_focus_idx = 0

        # Global data structures for ui
        self.lists = []
        self.tasks = []

        # Initialize windows
        self.left_window = HSplit(
            [Window()],
            align=VerticalAlign.TOP,
            padding=0,
            key_bindings=self.get_left_kb(),
        )
        self.right_window = HSplit(
            [Window()],
            align=VerticalAlign.TOP,
            padding=0,
            key_bindings=self.get_right_kb(),
        )
        self.status_bar = Window(height=1, style="class:line")

        # Style sheet
        style = Style(
            [
                ("activated", self.STYLE_ACTIVATED),
            ]
        )

        # Creating an `Application` instance
        self.application = Application(
            layout=self.create_layout(),
            key_bindings=self.get_global_kb(),
            mouse_support=False,
            full_screen=True,
            style=style,
        )

        # disable paste on win32
        if sys.platform == "win32":
            self.application.input.console_input_reader.recognize_paste = False

    async def run(self):
        async def init():
            await self.load_lists()
            self.application.invalidate()

        await asyncio.gather(self.application.run_async(), init())

    def create_layout(self):
        body = VSplit(
            [
                self.left_window,
                Window(width=1, char="|", style="class:line"),
                ScrollablePane(self.right_window, keep_cursor_visible=True),
            ],
            padding=1,
        )

        root_container = HSplit(
            [
                self.status_bar,
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

    async def spinner(self, message, callback):
        self.status_bar.content = FormattedTextControl()
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        task = asyncio.create_task(asyncio.to_thread(callback))
        i = 0
        while not task.done():
            self.status_bar.content.text = f"{chars[i]} {message}"
            self.application.invalidate()
            i = (i + 1) % len(chars)
            await asyncio.wait([task], timeout=0.05)
        self.status_bar.content = DummyControl()
        return task.result()

    async def load_lists(self):
        """
        Load all lists
        """

        # Retrieve folder data
        self.lists = await self.spinner("Loading lists", lambda: wrapper.get_lists())

        # Layout interface
        self.left_window.children = [
            Window(FormattedTextControl(f.display_name), width=50) for f in self.lists
        ]

        if self.list_focus_idx >= len(self.lists):
            self.list_focus_idx = len(self.lists) - 1

        # Highlight first folder
        self.left_window.children[self.list_focus_idx].style = "class:activated"
        self.application.layout.focus(self.left_window.children[self.list_focus_idx])

    async def load_tasks(self):
        """
        Load tasks of currently focused folder
        """

        selected_list = self.lists[self.list_focus_idx]

        self.tasks = await self.spinner(
            "Loading tasks",
            lambda: wrapper.get_tasks(list_id=selected_list.id, num_tasks=100),
        )
        self.tasks.sort(
            key=lambda x: x.reminder_datetime or x.due_datetime or x.created_datetime
        )

        if not self.tasks:
            self.right_window.children = [
                Window(FormattedTextControl("-- No Tasks --"))
            ]
            self.application.layout.focus(self.right_window.children[0])
            return

        def create_task_ui(task):
            return VSplit(
                [
                    Window(FormattedTextControl(task.title), wrap_lines=True, height=2),
                    Window(width=5),
                    Window(
                        FormattedTextControl(f"Reminder: {task.reminder_datetime}"),
                        width=30,
                    ),
                ],
            )

        self.right_window.children = [create_task_ui(t) for t in self.tasks]

        if self.task_focus_idx >= len(self.tasks):
            self.task_focus_idx = len(self.tasks) - 1

        self.right_window.children[self.task_focus_idx].style = "class:activated"
        self.application.layout.focus(
            self.right_window.children[self.task_focus_idx].children[0]
        )

    def reset_prompt_window(self):
        self.status_bar.content = DummyControl()
        self.application.layout.focus_last()

    async def prompt_async(self, message):
        last_focused = self.application.layout.current_window
        try:
            return await self._prompt_async(message)
        finally:
            # FIXME: what if the window is removed?
            self.application.layout.focus(last_focused)

    def _prompt_async(self, message):
        f = asyncio.Future()
        self.prompt(message, callback=f.set_result, callback_err=f.set_exception)
        return f

    def prompt(self, *messages, callback=None, callback_err=None):
        messages_list = [*messages]

        if not callable(callback):
            raise ValueError("callback must be a function")

        result = []

        def loop():
            if not messages_list:
                callback(*result)
                return

            def handler(_):
                result.append(buffer.text)
                self.reset_prompt_window()
                loop()

            buffer = Buffer(multiline=False, accept_handler=handler)

            kb = KeyBindings()

            @kb.add("escape", eager=True)
            def _(event):
                self.reset_prompt_window()
                if callable(callback_err):
                    callback_err(TypeError("User cancelled input"))

            control = BufferControl(
                buffer=buffer,
                key_bindings=kb,
                input_processors=[
                    BeforeInput(messages_list.pop(0), style="class:text-area.prompt")
                ],
            )

            self.status_bar.content = control
            self.application.layout.focus(buffer)
            self.application.invalidate()

        loop()

    """
    Key Bindings
    """

    def get_global_kb(self):
        kb = KeyBindings()

        @kb.add("c-c", eager=True)
        @kb.add("c-q", eager=True)
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
            self.status_bar.content = FormattedTextControl(
                "[UP: j] [DOWN: k] [SELECT: l] [BACK: h] [CREATE: n] [MARK COMPLETE: c] [EXIT HELP: ESC]"
            )

        return kb

    def get_left_kb(self):
        kb = KeyBindings()

        @kb.add("n")
        async def _(event):
            """
            Create new list
            """
            try:
                name = await self.prompt_async("New list: ")
            except TypeError:
                return
            await self.spinner("Creating new list", lambda: wrapper.create_list(name))
            await self.load_lists()

        @kb.add("d")
        async def _(event):
            """
            Delete currently focused list
            """
            list_title = self.lists[self.list_focus_idx].display_name
            try:
                confirmation = await self.prompt_async(
                    f"Delete list {list_title!r}? <y> to confirm. "
                )
            except TypeError:
                return
            if confirmation != "y":
                return
            await self.spinner(
                "Deleting list",
                lambda: wrapper.delete_list(self.lists[self.list_focus_idx].id),
            )
            await self.load_lists()

        def move_cursor(offset):
            list_window = self.left_window.children
            if not list_window:
                return
            list_window[self.list_focus_idx].style = ""
            self.list_focus_idx = (
                self.list_focus_idx + offset + len(list_window)
            ) % len(self.lists)
            list_window[self.list_focus_idx].style = "class:activated"
            self.application.layout.focus(list_window[self.list_focus_idx])

        @kb.add("j")
        def _(event):
            """
            Move selection down 1
            """
            move_cursor(1)

        @kb.add("k")
        def _(event):
            """
            Move selection up 1
            """
            move_cursor(-1)

        @kb.add("l")
        async def _(event):
            """
            Load tasks of currently focused folder
            """
            await self.load_tasks()

        return kb

    def get_right_kb(self):
        kb = KeyBindings()

        @kb.add("n")
        async def _(event):
            """
            Create new task
            """
            try:
                name = await self.prompt_async("New task: ")
            except TypeError:
                return
            if not name:
                return

            reminder = None
            try:
                reminder = await self.prompt_async("Reminder (optional): ")
            except TypeError:
                pass

            def create_task():
                wrapper.create_task(
                    task_name=name,
                    list_id=self.lists[self.list_focus_idx].id,
                    reminder_datetime=(
                        None if not reminder else parse_datetime(reminder)
                    ),
                )

            await self.spinner("Creating new task", create_task)
            await self.load_tasks()

        @kb.add("h")
        def _(event):
            """
            Go back to list scroll mode
            """
            self.right_window.children = []
            self.application.layout.focus(
                self.left_window.children[self.list_focus_idx]
            )

        def move_cursor(offset):
            if not self.tasks:
                return
            self.right_window.children[self.task_focus_idx].style = ""
            self.task_focus_idx = (
                self.task_focus_idx + offset + len(self.tasks)
            ) % len(self.tasks)
            self.right_window.children[self.task_focus_idx].style = "class:activated"
            self.application.layout.focus(
                self.right_window.children[self.task_focus_idx].children[0]
            )

        @kb.add("j")
        def _(event):
            """
            Move selection down 1
            """
            move_cursor(1)

        @kb.add("k")
        def _(event):
            """
            Move selection up 1
            """
            move_cursor(-1)

        @kb.add("c")
        def _(event):
            """
            Mark task as complete
            """
            if not self.tasks:
                return

            async def _():
                try:
                    confirmation = await self.prompt_async(
                        "Mark task as complete? <y> to confirm. "
                    )
                except TypeError:
                    return
                if confirmation != "y":
                    return

                def complete_task():
                    wrapper.complete_task(
                        list_id=self.lists[self.list_focus_idx].id,
                        task_id=self.tasks[self.task_focus_idx].id,
                    )

                await self.spinner("Marking task as complete", complete_task)
                await self.load_tasks()

            asyncio.create_task(_())

        @kb.add("d")
        def _(event):
            """
            Delete currently focused task
            """
            if not self.tasks:
                return

            async def _():
                task_title = self.tasks[self.task_focus_idx].title
                try:
                    confirmation = await self.prompt_async(
                        f"Delete task {task_title!r}? <y> to confirm. "
                    )
                except TypeError:
                    return
                if confirmation != "y":
                    return

                def delete_task():
                    wrapper.delete_task(
                        list_id=self.lists[self.list_focus_idx].id,
                        task_id=self.tasks[self.task_focus_idx].id,
                    )

                await self.spinner("Deleting task", delete_task)
                await self.load_tasks()

            asyncio.create_task(_())

        return kb


def run():
    gui = Tod0GUI()
    asyncio.run(gui.run())
