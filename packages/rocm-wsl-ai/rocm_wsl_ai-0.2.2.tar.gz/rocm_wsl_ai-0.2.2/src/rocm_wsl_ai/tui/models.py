from __future__ import annotations
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, ListView, ListItem, Label, Input
from textual.containers import Horizontal, Vertical
from threading import Thread
from .dialogs import PresetSelectModal, DownloadProgressModal, SettingsModal, CivitaiFileSelectModal


class ModelManager(App):
    CSS = """
    Screen { align: center middle; }
    #title { content-align: center middle; height: 3; }
    .panel { width: 92; border: round $accent; padding: 1; }
    .row { height: auto; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Model Manager", id="title")
        with Vertical(classes="panel"):
            with Horizontal(classes="row"):
                yield Button("Refresh", id="refresh")
                yield Button("Download Preset", id="presets")
                yield Button("Settings", id="settings")
            self.list_view = ListView(id="models")
            yield self.list_view
            # Preset-Auswahl (ausblendbar)
            self.preset_view = ListView(id="presets_list")
            self.preset_view.display = False
            yield self.preset_view
            self.status = Label("", id="status")
            yield self.status
        yield Footer()

    def on_mount(self):
        self.refresh_models()

    def refresh_models(self):
        from ..core.models_index import load_index
        idx = load_index()
        items = []
        for _, e in sorted(idx.items(), key=lambda kv: (kv[1].category, kv[1].path)):
            items.append(ListItem(Label(f"{e.category:<18} {e.size/1024/1024:6.1f} MB  {e.path}")))
        self.list_view.clear()
        self.list_view.extend(items)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh":
            from ..core.models_index import refresh_index
            refresh_index()
            self.refresh_models()
        elif event.button.id == "presets":
            def after_select(key: str | None):
                if key:
                    self.push_screen(DownloadProgressModal(key))
            self.push_screen(PresetSelectModal(), callback=after_select)
        elif event.button.id == "settings":
            self.push_screen(SettingsModal())

    # After modal closes, list refresh handled via dialog progress; keep simple here.


def run():
    ModelManager().run()
