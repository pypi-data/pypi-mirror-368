from __future__ import annotations
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, ListView, ListItem, Label
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from rich import box
import sys

class Main(App):
    CSS = """
    Screen { align: center middle; }
    #title { content-align: center middle; height: 3; }
    .panel { width: 68; border: round $accent; padding: 1; }
    .buttons { height: auto; }
    """

    install_items = [
        ("base", "ROCm & PyTorch Nightly (base)"),
        ("comfyui", "ComfyUI"),
        ("sdnext", "SD.Next"),
        ("fooocus", "Fooocus"),
        ("textgen", "Text Generation WebUI"),
        ("forge", "SD WebUI Forge"),
        ("llama.cpp", "llama.cpp"),
        ("koboldcpp", "KoboldCpp"),
        ("fastchat", "FastChat"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("ROCm-WSL-AI", id="title")
        with Vertical(classes="panel"):
            yield Label("Installation")
            lv = ListView(*[ListItem(Label(f"{k:<10} {v}")) for k, v in self.install_items], id="install_list")
            yield lv
            with Horizontal(classes="buttons"):
                yield Button("Install", id="install")
                yield Button("Start ComfyUI", id="start_comfyui")
                yield Button("Update", id="update")
                yield Button("Doctor", id="doctor")
                yield Button("Models", id="models")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        from ..cli import app as cli_app  # reuse logic by invoking via system
        import subprocess
        lv: ListView = self.query_one("#install_list")
        idx = lv.index
        key = self.install_items[idx][0] if idx is not None else None
        # Prefer running via current python -m to avoid PATH issues
        python = sys.executable
        base_cmd = [python, "-m", "rocm_wsl_ai.cli"]
        if event.button.id == "install" and key:
            subprocess.call([*base_cmd, "install", key])
        elif event.button.id == "start_comfyui":
            subprocess.call([*base_cmd, "start", "comfyui"])
        elif event.button.id == "update":
            subprocess.call([*base_cmd, "update"])
        elif event.button.id == "doctor":
            subprocess.call([*base_cmd, "doctor"])
        elif event.button.id == "models":
            from .models import run as models_run
            models_run()


def run():
    Main().run()
