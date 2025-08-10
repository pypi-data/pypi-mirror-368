from textual.app import App 
from textual.widget import Widget 
from textual.widgets import Static, Button
from textual.containers import Horizontal, Vertical, VerticalScroll, HorizontalScroll
from pathlib import Path
from textual import events
from textual.events import MouseDown
import pygame
import asyncio
pygame.mixer.init()


from .config import LIBRARY_DIR as Lib
#This file contains the melody maker window it has a playback bar at the top and a library bar on the side and a bar widget for the music sequencer and a static bar at the bottom for controls

class Soundb(Button):
    async def on_mouse_down(self, event: MouseDown) -> None:
        if event.button == 1:
            if "b1" in self.classes:
                self.remove_class("b1")
                self.add_class("b2")
            elif "b2" in self.classes:
                self.remove_class("b2")
                self.add_class("b1")
class Deleteb(Button):
    async def on_mouse_down(self, event: MouseDown) -> None:
        cntr = self.app.query_one("#v2")
        if event.button == 3:
            self.remove()
            (Lib / f"{self.label}.wav").unlink()
            await (cntr.query_one(f"#{self.label}")).remove()
            
        if event.button == 1 and not(cntr.query(f"#{self.label}")):
            await cntr.mount(Bar(self.label,classes="barr",id=str(self.label)))
            
          
class Melody(Widget):
    def compose(self):
        combined = []
        for file in Lib.iterdir():
            if file.is_file() and file.suffix.lower() == '.wav':
                bt = Deleteb(file.stem)
                combined.append(bt)
                combined.extend([])
        yield Horizontal(
                Vertical(
                    Static("Library", classes="label1"),
                    VerticalScroll(*combined,id="bar1"),
                    id="v1",
                ),
                Vertical(
                    Horizontal(
                        Button("▶️",id="play"),
                        id="h1",
                    ),
                    VerticalScroll(
                        id="v2"
                    ),
                    Static("Left Click to add sound - Right Click to delete sound - Ctrl + Scroll to scroll horizonally - Scroll to scroll vertically",classes= "s6"),  
                ),
        )
    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "play":
            bars = self.query("#v2 .barr") 
            step = 0
            for bar in bars:
                buttons = list(bar.query(Soundb))
                for i, btn in enumerate(buttons):
                    if "b2" in btn.classes:
                        step = max(step, i) 
            for stp in range(step + 1):
                for bar in bars:
                    buttons = list(bar.query(Soundb))
                    if stp < len(buttons):
                        btn = buttons[stp]
                        if "b2" in btn.classes:
                            sound_path = Lib / f"{bar.index}.wav"
                            if sound_path.exists():
                                pygame.mixer.Sound(str(sound_path)).play()
                await asyncio.sleep(0.5)
class Bar(Widget):
    def __init__(self, index: str, **kwargs):
        super().__init__(**kwargs)
        self.index = index
    def compose(self):
        combined = [] 
        combined.append(Static(self.index, classes="s1"))
        combined.extend([ 
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),
        Soundb("", classes="b1"),])
        yield HorizontalScroll(*combined, classes="h5")

