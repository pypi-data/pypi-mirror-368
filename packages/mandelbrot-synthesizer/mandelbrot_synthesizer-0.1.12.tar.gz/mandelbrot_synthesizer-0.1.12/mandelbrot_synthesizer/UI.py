from textual.app import App
from textual.widgets import Button, Static
from textual.containers import Vertical, Horizontal
from .MandelbrotWindow import Mandelbrot
from .MelodyMakerWindow import Melody
from .Naming import Choose
class Main(App):
    CSS_PATH = "Styling.tcss"

    def compose(self):
        yield Vertical(
            Static("Mandelbrot Synthesizer", id="header"),
            Horizontal(
                Vertical(
                    Button("🌌", classes="sidebar", id="uni"),
                    Button("🎹", classes="sidebar", id="key"),
                    id="sidecontainer"
                ),
                Mandelbrot(id="mandelbrot"),
                id="maincontainer",
            )
        )

    async def on_button_pressed(self, event: Button.Pressed):
        cntnr = self.query_one("#maincontainer")
        if(event.button.id == "uni" and not self.query("#mandelbrot")):
            await cntnr.mount(Mandelbrot(id="mandelbrot"))
            melody = self.query_one("#melody")
            await melody.remove()
        if (event.button.id == "key" and not self.query("#melody")):
            await cntnr.mount(Melody(id="melody"))
            mandelbrot = self.query_one("#mandelbrot")
            await mandelbrot.remove()
            
