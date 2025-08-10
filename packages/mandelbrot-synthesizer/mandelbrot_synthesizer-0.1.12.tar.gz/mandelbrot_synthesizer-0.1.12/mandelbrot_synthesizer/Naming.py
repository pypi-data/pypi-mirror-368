from textual.message import Message
from textual.widget import Widget 
from textual.widgets import Input, Static
from textual.containers import Vertical, Horizontal
from textual.events import Key
import re
#this file is a naming widget responsible for saving the names of selected notes
VALID_NAME_REGEX = re.compile(r"^[A-Za-z_-][A-Za-z0-9_-]*$")
class Choose(Widget):
    class Done(Message):
        def __init__(self, name: str):
            super().__init__()
            self.name = name


    def compose(self):
        yield Vertical(
            Static("Choose a name for this note (Max 16 characters)", id="s2"),
            Horizontal(
                Input(id="chose", type="text",max_length=16),
                id="h4",
            ),
            Static("", id="feedback"),
            Static(""),
            Static("Press ESC to exit | Press ENTER to submit"),
            id="v4",
        )

    async def on_ready(self):
        await self.query_one(Input).focus()

    async def on_input_submitted(self, event: Input.Submitted):
        name = event.value
        feedback = self.query_one("#feedback", Static)
        feedback.styles.color = "red"
        if VALID_NAME_REGEX.fullmatch(name):
            self.post_message(self.Done(name))
        else:
            feedback.update(
                "Name must only contain letters, numbers, underscores, or hyphens, and must not begin with a number."
            )

    async def on_key(self, event: Key):
        if event.key == "escape":
            self.post_message(self.Done(self, ""))
