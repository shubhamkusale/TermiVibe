from textual.widgets import Static
from textual.reactive import reactive
from rich.align import Align
from rich.panel import Panel
from rich.text import Text

class Visualizer(Static):
    """A widget to display audio frequency spectrum."""
    
    spectrum_data = reactive([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spectrum_data = [0.0] * 64

    def watch_spectrum_data(self, data):
        self.refresh()

    def render(self):
        # Create a bar chart using block characters
        bars = []
        height = self.content_size.height or 10
        
        # Simple rendering: use blocks of varying height
        # characters:  ▂▃▄▅▆▇█
        blocks = "  ▂▃▄▅▆▇█"
        
        for value in self.spectrum_data:
            # Value is 0.0 to 1.0
            idx = int(value * (len(blocks) - 1))
            idx = max(0, min(idx, len(blocks) - 1))
            bars.append(blocks[idx])
            
        # For a more advanced view, we could do vertical bars, but for now horizontal string of blocks
        # Wait, usually visualizers are vertical bars.
        # Let's try to make it look like a bar chart.
        # But Static.render returns a Renderable.
        # We can return a Text object.
        
        return Panel(Align.center(Text("".join(bars), style="bold green")), title="Frequency Spectrum")
