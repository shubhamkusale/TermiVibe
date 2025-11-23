from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Label, Input
from .visualizer import Visualizer
from audio_engine import AudioEngine
import os

class TermiVibeApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    
    #visualizer-container {
        height: 60%;
        width: 100%;
        border: solid green;
    }
    
    #controls {
        height: auto;
        width: 100%;
        align: center middle;
        padding: 1;
    }
    
    Button {
        margin: 1;
    }
    
    #file-input {
        width: 50%;
        margin: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("space", "toggle_play", "Play/Pause"),
        ("l", "load_file", "Load File"),
    ]

    def __init__(self):
        super().__init__()
        self.audio_engine = AudioEngine()
        self.timer = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Visualizer(id="visualizer"),
            id="visualizer-container"
        )
        yield Horizontal(
            Input(placeholder="Enter file path...", id="file-input"),
            Button("Load", id="load-btn", variant="primary"),
            Button("Play", id="play-btn", variant="success"),
            Button("Pause", id="pause-btn", variant="warning"),
            Button("Stop", id="stop-btn", variant="error"),
            id="controls"
        )
        yield Footer()

    def on_mount(self):
        self.timer = self.set_interval(1 / 30, self.update_visualizer)

    def update_visualizer(self):
        visualizer = self.query_one("#visualizer", Visualizer)
        spectrum = self.audio_engine.get_spectrum(num_bands=64)
        visualizer.spectrum_data = spectrum.tolist()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "play-btn":
            self.action_toggle_play()
        elif button_id == "pause-btn":
            self.audio_engine.pause()
        elif button_id == "stop-btn":
            self.audio_engine.stop()
        elif button_id == "load-btn":
            self.load_audio_file()

    def action_toggle_play(self):
        if self.audio_engine.is_playing:
            self.audio_engine.pause()
        else:
            self.audio_engine.play()

    def load_audio_file(self):
        file_input = self.query_one("#file-input", Input)
        file_path = file_input.value
        if os.path.exists(file_path):
            if self.audio_engine.load_file(file_path):
                self.notify(f"Loaded: {file_path}")
            else:
                self.notify("Failed to load file.", severity="error")
        else:
            self.notify("File not found.", severity="error")
