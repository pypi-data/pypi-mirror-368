from textual.app import App
from textual.widgets import Button, Label, Static
from textual.widget import Widget
from textual.containers import Vertical, VerticalScroll, Horizontal, Container
from textual_canvas import Canvas
from textual.color import Color
from textual import events
from textual.binding import Binding
from typing import Iterator
import pygame
import time
import math
import os
import wave
from pathlib import Path
from .Naming import Choose
from .config import LIBRARY_DIR
#This file contains the fractal display window responsible for displaying various fractals. it also contains a sidebar on the left for fractal selection and a bar at the bottom for controls
BLUE_BROWN = [
    Color(66, 30, 15),
    Color(25, 7, 26),
    Color(9, 1, 47),
    Color(4, 4, 73),
    Color(0, 7, 100),
    Color(12, 44, 138),
    Color(24, 82, 177),
    Color(57, 125, 209),
    Color(134, 181, 229),
    Color(211, 236, 248),
    Color(241, 233, 191),
    Color(248, 201, 95),
    Color(255, 170, 0),
    Color(204, 128, 0),
    Color(153, 87, 0),
    Color(106, 52, 3),
]

pygame.mixer.init(frequency=44100, size=-16, channels=1)

def generate_tone(frequency: float, duration: float = 0.2, volume: float = 0.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    for i in range(n_samples):
        value = int(volume * 32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        buf += value.to_bytes(2, byteorder='little', signed=True)
    sound = pygame.mixer.Sound(buffer=bytes(buf))
    return sound, bytes(buf)

def mandelbrot(x: float, y: float, max_iter: int) -> int:
    c = complex(x, y)
    z = 0j
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return 0

def burning_ship(x: float, y: float, max_iter: int) -> int:
    c = complex(x, y)
    z = 0j
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = complex(abs(z.real), abs(z.imag))
        z = z*z + c
    return 0

def phoenix(x: float, y: float, max_iter: int) -> int:
    c = complex(x, y)
    z = 0j
    p = 0j
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z, p = z*z + c + 0.56667 * p, z
    return 0

def tricorn(x: float, y: float, max_iter: int) -> int:
    c = complex(x, y)
    z = 0j
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = (z.conjugate())**2 + c
    return 0

def julia(x: float, y: float, max_iter: int) -> int:
    c = complex(-0.7, 0.27015)
    z = complex(x, y)
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return 0

def frange(r_from: float, r_to: float, size: int) -> Iterator[tuple[int, float]]:
    step = (r_to - r_from) / size
    for i in range(size):
        yield i, r_from + i * step
BINDINGS = [
Binding("up, w", "move( 0, -1 )", "Up", show=False),
Binding("down, s", "move( 0, 1 )", "Down", show=False),
Binding("left, a", "move( -1, 0 )", "Left", show=False),
Binding("right, d", "move( 1, 0 )", "Right", show=False),
Binding("pageup, right_square_bracket", "zoom( -1.2 )", "In"),
Binding("pagedown, left_square_bracket", "zoom( 1.2 )", "Out"),
]
class SoundCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_sound = 0
        self._cooldown = 0.5
        self.last_tone = None
        self.last_raw_buffer = None
        self.last_coords = None
        self.x_min, self.x_max = -2.5, 1.5
        self.y_min, self.y_max = -1.5, 1.5
        self.max_iter = 70
        self.fractal_func = mandelbrot


    def render(self) -> None:
        with self.batch_refresh():
            for x_pixel, x_point in frange(self.x_min, self.x_max, self.width):
                for y_pixel, y_point in frange(self.y_min, self.y_max, self.height):
                    value = self.fractal_func(x_point, y_point, self.max_iter)
                    color = BLUE_BROWN[value % 16] if value else Color(0, 0, 0)
                    self.set_pixel(x_pixel, y_pixel, color)
        self.refresh()

    async def on_mouse_down(self, event: events.MouseDown) -> None:
        current_time = time.time()
        if current_time - self._last_sound < self._cooldown:
            return
        x, y = event.offset.x, event.offset.y
        if 0 <= x < self.width and 0 <= y < self.height:
            x_coord = self.x_min + (self.x_max - self.x_min) * x / self.width
            y_coord = self.y_min + (self.y_max - self.y_min) * y / self.height
            escape_time = self.fractal_func(x_coord, y_coord, self.max_iter)
            freq = 100 * (1.2 ** escape_time)
            volume = min(0.3 + (escape_time / 50), 1.0)
            tone, raw_buffer = generate_tone(freq, 0.5, volume)
            tone.play()
            self.last_tone = tone
            self.last_raw_buffer = raw_buffer
            self.last_coords = (x_coord, y_coord)
            self._last_sound = current_time

class Mandelbrot(Widget):
    CSS_PATH = "Styling.tcss"
    async def on_choose_done(self, message: Choose.Done) -> None:
        await self.query_one(Choose).remove()
        if message.name.strip():
            self.save_last_sound(message.name.strip())
        cntrrr = self.query_one("#mainrow")
        await cntrrr.remove_children()
        await cntrrr.mount(
            Container(
                SoundCanvas(100, 70, id="canvs"),
                id="contnr",
            ),
            Vertical(
                Label("Fractals:", classes="label1"),
                VerticalScroll(
                    Button("Mandelbrot", id="mandelbrot_btn"),
                    Button("Burning Ship", id="burning_ship_btn"),
                    Button("Phoenix", id="phoenix_btn"),
                    Button("Tricorn", id="tricorn_btn"),
                    Button("Julia Set", id="julia_btn"),
                    id="mandelbrotscroll",
                ),
                classes="bar"
            ),
        )
        self.canvas = self.query_one(SoundCanvas)
        self.canvas.render()

    def compose(self):
        yield Vertical(
            Horizontal(
                Container(
                    SoundCanvas(100, 70, id="canvs"),
                    id="contnr",
                ),
                Vertical(
                    Label("Fractals:", classes="label1"),
                    VerticalScroll(
                        Button("Mandelbrot", id="mandelbrot_btn"),
                        Button("Burning Ship", id="burning_ship_btn"),
                        Button("Phoenix", id="phoenix_btn"),
                        Button("Tricorn", id="tricorn_btn"),
                        Button("Julia Set", id="julia_btn"),
                        id="mandelbrotscroll",
                    ),
                    classes="bar"
                ),
                id="mainrow",
            ),
            Static(
                "Controls: Press v to save sound - wasd to pan - PU and PD to zoom",
                id="footer",
            ),
        )

    def on_mount(self) -> None:
        self.canvas = self.query_one(SoundCanvas)
        self.canvas.fractal_func = mandelbrot
        self.canvas.render()
        self.focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        self.canvas.x_min, self.canvas.x_max = -2.5, 1.5
        self.canvas.y_min, self.canvas.y_max = -1.5, 1.5
        if event.button.id == "mandelbrot_btn":
            self.canvas.fractal_func = mandelbrot
        elif event.button.id == "burning_ship_btn":
            self.canvas.fractal_func = burning_ship
        elif event.button.id == "phoenix_btn":
            self.canvas.fractal_func = phoenix
        elif event.button.id == "tricorn_btn":
            self.canvas.fractal_func = tricorn
        elif event.button.id == "julia_btn":
            self.canvas.fractal_func = julia
        self.canvas.render()

    def save_last_sound(self, filename: str = None):
        if self.canvas.last_raw_buffer and self.canvas.last_coords:
            freq_samples = 44100
            buf = self.canvas.last_raw_buffer
            os.makedirs(LIBRARY_DIR, exist_ok=True)
            if not filename:
                x_coord, y_coord = self.canvas.last_coords
                filename = f"sound_{x_coord:.4f}_{y_coord:.4f}"
            path = LIBRARY_DIR / f"{filename}.wav"  
            with wave.open(str(path), "wb") as wf: 
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(freq_samples)
                wf.writeframes(buf)


    
    async def on_key(self, event: events.Key) -> None:
        cntrrr = self.query_one("#mainrow")
        if event.key == "v":
            event.prevent_default()
            event.stop()
            await cntrrr.remove_children()
            await cntrrr.mount(Choose())
            return

        try:
            self.canvas = self.query_one(SoundCanvas)
        except Exception:
            return

              
        self.canvas = self.query_one(SoundCanvas)
        pan = 0.1  
        if event.key == "a":
            dx = (self.canvas.x_max - self.canvas.x_min) * pan
            self.canvas.x_min -= dx
            self.canvas.x_max -= dx
            self.canvas.render()
        if event.key == "d":
            dx = (self.canvas.x_max - self.canvas.x_min) * pan
            self.canvas.x_min += dx
            self.canvas.x_max += dx
            self.canvas.render()
        if event.key == "w":    
            dy = (self.canvas.y_max - self.canvas.y_min) * pan
            self.canvas.y_min -= dy
            self.canvas.y_max -= dy
            self.canvas.render()
        if event.key == "s":
            dy = (self.canvas.y_max - self.canvas.y_min) * pan
            self.canvas.y_min += dy
            self.canvas.y_max += dy
            self.canvas.render()
        if event.key == "pagedown":
            factor = 0.8
            x_center = (self.canvas.x_min + self.canvas.x_max) / 2
            y_center = (self.canvas.y_min + self.canvas.y_max) / 2
            x_range = (self.canvas.x_max - self.canvas.x_min) * factor / 2
            y_range = (self.canvas.y_max - self.canvas.y_min) * factor / 2
            self.canvas.x_min = x_center - x_range
            self.canvas.x_max = x_center + x_range
            self.canvas.y_min = y_center - y_range
            self.canvas.y_max = y_center + y_range
            self.canvas.render()

        if event.key == "pageup":
            factor = 1.25
            x_center = (self.canvas.x_min + self.canvas.x_max) / 2
            y_center = (self.canvas.y_min + self.canvas.y_max) / 2
            x_range = (self.canvas.x_max - self.canvas.x_min) * factor / 2
            y_range = (self.canvas.y_max - self.canvas.y_min) * factor / 2
            self.canvas.x_min = x_center - x_range
            self.canvas.x_max = x_center + x_range
            self.canvas.y_min = y_center - y_range
            self.canvas.y_max = y_center + y_range
            self.canvas.render()

class MandelbrotApp(App):
    CSS_PATH = "Styling.tcss"

    def compose(self):
        yield Mandelbrot()

    def on_mount(self):
        self.query_one(Mandelbrot).focus()

if __name__ == "__main__":
    MandelbrotApp().run()
