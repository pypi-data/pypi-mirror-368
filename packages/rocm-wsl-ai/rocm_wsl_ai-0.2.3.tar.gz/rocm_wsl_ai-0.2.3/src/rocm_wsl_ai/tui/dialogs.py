from __future__ import annotations
from pathlib import Path
from threading import Thread
from typing import Optional
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, ListView, ListItem, Label, ProgressBar, Input
from textual.containers import Vertical, Horizontal


class PresetSelectModal(ModalScreen[Optional[str]]):
    def __init__(self):
        super().__init__()
        self.list_view: ListView | None = None

    def compose(self) -> ComposeResult:
        from ..core.models_download import PRESETS
        with Vertical(id="preset_modal", classes="panel"):
            yield Label("Wähle ein Preset", id="title")
            items = []
            for k, spec in PRESETS.items():
                size = spec.get("size", "-")
                fn = spec.get("filename", "-")
                items.append(ListItem(Label(f"{k:<24} {size:>8}  {fn}"), id=f"preset::{k}"))
            self.list_view = ListView(*items, id="presets_list")
            yield self.list_view
            with Horizontal():
                yield Button("Download", id="ok")
                yield Button("Abbrechen", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "ok":
            if self.list_view and self.list_view.index is not None:
                item = self.list_view.get_child_by_index(self.list_view.index)
                if item and item.id and item.id.startswith("preset::"):
                    self.dismiss(item.id.split("::", 1)[1])


class DownloadProgressModal(ModalScreen[None]):
    def __init__(self, preset_key: str, override_url: str | None = None, override_filename: str | None = None):
        super().__init__()
        self.preset_key = preset_key
        self._override_url = override_url
        self._override_filename = override_filename
        self.progress: ProgressBar | None = None
        self.status: Label | None = None
        self._total: int | None = None
        self._dest: Path | None = None
        self._done: bool = False
        self._last_bytes: int = 0
        self._last_time: float = 0.0

    def compose(self) -> ComposeResult:
        with Vertical(id="dl_modal", classes="panel"):
            yield Label(f"Lade: {self.preset_key}")
            self.progress = ProgressBar(total=100)
            yield self.progress
            self.status = Label("Vorbereitung...")
            yield self.status
            with Horizontal():
                yield Button("Schließen", id="close")

    def on_mount(self) -> None:
        # Resolve URL, total size, and dest; then start background download thread
        from ..core.models_download import resolve_preset_url, preset_path, get_content_length, install_preset
        try:
            url = self._override_url or resolve_preset_url(self.preset_key)
            self._total = get_content_length(url)
            dest = preset_path(self.preset_key)
            if self._override_filename:
                # Replace filename but keep category path
                dest = dest.parent / self._override_filename
            self._dest = dest
        except Exception as e:
            if self.status:
                self.status.update(f"[red]Fehler:[/red] {e}")
            return

        def worker():
            try:
                install_preset(self.preset_key, override_url=self._override_url, override_filename=self._override_filename)
                self._done = True
                self.app.call_from_thread(self._update_done)
            except Exception as e:  # noqa: BLE001
                self.app.call_from_thread(self._update_error, str(e))

        # Poll file size periodically
        self.set_interval(0.5, self._tick)
        Thread(target=worker, daemon=True).start()

    def _tick(self):
        if self._done or not self._dest or not self._dest.exists():
            return
        import time
        try:
            cur = self._dest.stat().st_size
        except Exception:
            cur = 0
        if self._total and self.progress:
            pct = max(0, min(100, int(cur * 100 / max(1, self._total))))
            self.progress.update(progress=pct)
        if self.status:
            now = time.time()
            delta_b = cur - self._last_bytes
            delta_t = now - self._last_time if self._last_time else 0
            speed = (delta_b / delta_t) if delta_t > 0 else 0
            self._last_bytes, self._last_time = cur, now
            # ETA
            eta_s = 0
            if self._total and speed > 0:
                eta_s = int((self._total - cur) / speed)
            def fmt_bytes(b: int) -> str:
                return f"{b/1024/1024:.1f} MB"
            parts = [fmt_bytes(cur)]
            if self._total:
                parts.append(f"/ {fmt_bytes(self._total)}")
            if speed > 0:
                parts.append(f"  @ {speed/1024/1024:.2f} MB/s")
            if eta_s > 0:
                parts.append(f"  ETA {eta_s}s")
            self.status.update("".join(parts))

    def _update_done(self):
        if self.status and self.progress:
            self.progress.update(progress=100)
            self.status.update("[green]Fertig[/green]")

    def _update_error(self, msg: str):
        if self.status:
            self.status.update(f"[red]Fehler:[/red] {msg}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.dismiss(None)


class SettingsModal(ModalScreen[None]):
    def __init__(self):
        super().__init__()
        self.hf_input: Input | None = None
        self.cv_input: Input | None = None

    def compose(self) -> ComposeResult:
        from ..core.config import get_hf_token, get_civitai_token
        with Vertical(id="settings_modal", classes="panel"):
            yield Label("Downloader Settings")
            self.hf_input = Input(value=get_hf_token() or "", placeholder="HF Token", password=True)
            yield Label("Hugging Face Token")
            yield self.hf_input
            self.cv_input = Input(value=get_civitai_token() or "", placeholder="Civitai Token", password=True)
            yield Label("Civitai Token")
            yield self.cv_input
            with Horizontal():
                yield Button("Speichern", id="save")
                yield Button("Abbrechen", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            from ..core.config import save_config
            hf = self.hf_input.value if self.hf_input else None
            cv = self.cv_input.value if self.cv_input else None
            save_config(hf_token=(hf or None), civitai_token=(cv or None))
            self.dismiss(None)


class CivitaiFileSelectModal(ModalScreen[tuple[str, str] | None]):
    def __init__(self, model_id: int):
        super().__init__()
        self.model_id = model_id
        self.list_view: ListView | None = None

    def compose(self) -> ComposeResult:
        from ..core.models_download import list_civitai_files_for_model
        files = list_civitai_files_for_model(self.model_id)
        with Vertical(id="civitai_files_modal", classes="panel"):
            yield Label(f"Civitai Model {self.model_id}: Datei wählen")
            items = []
            for f in files:
                label = f"{f['versionName']}: {f['fileName']} ({(f['sizeBytes'] or 0)/1024/1024:.1f} MB)"
                items.append(ListItem(Label(label), id=f"file::{f['fileName']}::{f['downloadUrl']}"))
            self.list_view = ListView(*items)
            yield self.list_view
            with Horizontal():
                yield Button("Download", id="ok")
                yield Button("Abbrechen", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "ok" and self.list_view and self.list_view.index is not None:
            item = self.list_view.get_child_by_index(self.list_view.index)
            if item and item.id and item.id.startswith("file::"):
                _, fn, url = item.id.split("::", 2)
                self.dismiss((fn, url))
