"""Unified step timeline progress UI for CLI commands.

Provides a single, coherent live region that renders a compact list of steps,
with one active step at a time. Each step can optionally display a progress
bar when an estimated duration is available. Finished steps show a checkmark
and duration; failures show a cross and a short message.

This component is intentionally lightweight and self-contained so it can be
owned by one caller (e.g., `flow dev`) without conflicting with other Live
displays.
"""

from __future__ import annotations

import os
import random
import threading
import time
from dataclasses import dataclass

from rich.console import Console
from rich.live import Live
from rich.text import Text

from flow.cli.utils.animations import animation_engine
from flow.cli.utils.theme_manager import theme_manager


@dataclass
class _Step:
    label: str
    show_bar: bool = False
    estimated_seconds: int | None = None
    status: str = "pending"  # pending | active | done | failed
    note: str = ""
    note_text: Text | None = None
    started_mono: float | None = None
    finished_mono: float | None = None
    last_percent: float | None = None
    last_speed: str | None = None
    last_eta: str | None = None
    # When resuming a wait step (e.g., SSH provisioning), seed the bar with prior elapsed seconds
    baseline_elapsed_seconds: int | None = None


class StepTimeline:
    """Render and control a multi-step timeline with minimal, tasteful UI.

    Adds tasteful animations for active labels and optional animated title using
    the centralized animation engine. Runs a lightweight render loop so that
    animations move even when no explicit progress updates are flowing.
    """

    def __init__(
        self,
        console: Console,
        title: str | None = None,
        *,
        enable_animations: bool = True,
        title_animation: str | None = None,  # "wave" | "pulse" | "shimmer" | None
        active_label_animation: str | None = "pulse",  # None to disable
    ):
        self.console = console
        self.title = title or ""
        self.steps: list[_Step] = []
        self._live: Live | None = None
        self._active_index: int | None = None
        # Animation options
        self._enable_animations = enable_animations
        self._title_animation = title_animation
        self._active_label_animation = active_label_animation
        # Global environment overrides
        env_mode = os.getenv("FLOW_ANIMATIONS", "").strip().lower()
        # Respect simple output preference globally (calmer, non-animated)
        if os.getenv("FLOW_SIMPLE_OUTPUT", "").strip().lower() in {"1", "true", "yes"}:
            self._enable_animations = False
        if os.getenv("NO_COLOR"):
            self._enable_animations = False
        if env_mode in {"off", "0", "false", "disabled"}:
            self._enable_animations = False
        elif env_mode == "minimal":
            self._enable_animations = True
            # Keep spinner only; disable label/title animations
            self._title_animation = None
            self._active_label_animation = None
            # Slightly reduce cadence
            self._frame_interval = 0.1
        elif env_mode == "full":
            # Encourage richer animations if caller didn't explicitly set
            if self._title_animation is None:
                self._title_animation = "shimmer"
            if self._active_label_animation is None:
                self._active_label_animation = "wave"
        elif env_mode == "auto" or env_mode == "":
            # If caller didn't set explicit mode, enable auto
            if self._title_animation is None:
                self._title_animation = "auto"
            if self._active_label_animation is None:
                self._active_label_animation = "auto"
        # Animation cadence
        self._frame_interval = 0.08
        # Background render loop
        self._render_thread: threading.Thread | None = None
        self._stop_event: threading.Event | None = None
        # Prevent concurrent Live.update() from multiple threads
        self._render_lock: threading.Lock = threading.Lock()

    def add_step(
        self,
        label: str,
        *,
        show_bar: bool = False,
        estimated_seconds: int | None = None,
        baseline_elapsed_seconds: int | None = None,
    ) -> int:
        self.steps.append(
            _Step(
                label=label,
                show_bar=show_bar,
                estimated_seconds=estimated_seconds,
                baseline_elapsed_seconds=baseline_elapsed_seconds,
            )
        )
        return len(self.steps) - 1

    def start(self) -> None:
        if self._live is not None:
            return
        self._live = Live(Text(""), console=self.console, refresh_per_second=20, transient=True)
        self._live.__enter__()
        self._render()
        # Start lightweight render loop if animations are enabled
        if (
            self._enable_animations
            and getattr(self.console, "is_terminal", True)
            and not os.getenv("CI")
        ):
            self._stop_event = threading.Event()
            self._render_thread = threading.Thread(target=self._render_loop, daemon=True)
            self._render_thread.start()

    def _render_loop(self) -> None:
        # Keep refreshing while live is active; only minimal work
        while self._live is not None and self._stop_event and not self._stop_event.is_set():
            has_active = self._active_index is not None
            if has_active or self._title_animation:
                # Re-render to advance spinner/animated text phases
                self._render()
            # Keep cadence light to avoid CPU burn
            time.sleep(self._frame_interval)

    def _format_bar(self, step: _Step) -> Text:
        if step.estimated_seconds and step.started_mono and step.status == "active":
            # Include any baseline elapsed time (e.g., task/instance age) so bar resumes realistically
            baseline = step.baseline_elapsed_seconds or 0
            elapsed = time.monotonic() - step.started_mono
            pct = min((baseline + elapsed) / step.estimated_seconds, 0.95)
        else:
            pct = step.last_percent if step.last_percent is not None else 0.0
        # Use our gradient progress bar for a more pleasing look (ASCII-safe fallback inside)
        bar = animation_engine.progress_bar(pct, width=28, style="gradient", animated=True)
        # Compose status line pieces
        extra = []
        if step.estimated_seconds and step.started_mono:
            baseline = step.baseline_elapsed_seconds or 0
            wall = baseline + int(time.monotonic() - step.started_mono)
            extra.append(f"{wall}s/{step.estimated_seconds}s")
        if step.last_speed:
            extra.append(step.last_speed)
        if step.last_eta:
            extra.append(f"ETA {step.last_eta}")
        extra_text = ("  " + "  ".join(extra)) if extra else ""
        return Text(f"  {bar}{extra_text}")

    def _format_line(self, idx: int, step: _Step) -> list[Text]:
        total = len(self.steps)
        prefix = f"{idx + 1}/{total} "
        lines: list[Text] = []

        if step.status == "pending":
            lines.append(Text(f"{prefix}[ ] {step.label}", style="dim"))
        elif step.status == "active":
            # ASCII-safe spinner selection
            ascii_only = False
            try:
                enc = getattr(self.console, "encoding", None)
                if not enc or "UTF" not in str(enc).upper() or os.getenv("FLOW_ASCII") == "1":
                    ascii_only = True
            except Exception:
                ascii_only = False
            spinner_frames = (
                animation_engine.SPINNERS["line"]
                if ascii_only
                else animation_engine.SPINNERS["dots"]
            )
            spinner_phase = animation_engine.get_phase(0.8)
            spinner = animation_engine.get_spinner_frame(spinner_frames, spinner_phase)

            # Animated active label (subtle)
            label_text = Text(step.label)
            chosen = self._select_active_label_animation(step)
            if chosen:
                phase = animation_engine.get_phase(1.6)
                if chosen == "wave":
                    label_text = animation_engine.wave_pattern(step.label, phase, intensity=0.6)
                elif chosen == "pulse":
                    label_text = animation_engine.pulse_effect(step.label, phase, intensity=0.7)
                elif chosen == "shimmer":
                    label_text = animation_engine.shimmer_effect(step.label, phase, intensity=0.5)

            accent = theme_manager.get_color("accent")
            header = Text(f"{prefix}") + Text(spinner, style=accent) + Text(" ") + label_text
            lines.append(header)
            if step.show_bar:
                lines.append(self._format_bar(step))
            if step.note_text is not None:
                lines.append(step.note_text)
        elif step.status == "done":
            # Duration display
            dur = ""
            if step.started_mono and step.finished_mono:
                dur_secs = int(step.finished_mono - step.started_mono)
                dur = f" ({dur_secs}s)"
            note = f" – {step.note}" if step.note else ""
            lines.append(Text(f"{prefix}[green]✓[/green] {step.label}{dur}{note}"))
        else:  # failed
            note = f" – {step.note}" if step.note else ""
            lines.append(Text(f"{prefix}[red]✗[/red] {step.label}{note}"))

        return lines

    def _render(self) -> None:
        parts: list[Text] = []
        if self.title:
            chosen_title_anim = None
            if self._title_animation and self._enable_animations:
                if self._title_animation == "auto":
                    # Titles default to subtle shimmer for tasteful motion
                    chosen_title_anim = "shimmer"
                elif self._title_animation == "random":
                    # Avoid playful bounce for headers
                    chosen_title_anim = random.choice(["wave", "pulse", "shimmer"])
                else:
                    chosen_title_anim = self._title_animation
            if chosen_title_anim:
                phase = animation_engine.get_phase(2.4)
                if chosen_title_anim == "wave":
                    parts.append(animation_engine.wave_pattern(self.title, phase, intensity=0.5))
                elif chosen_title_anim == "pulse":
                    parts.append(animation_engine.pulse_effect(self.title, phase, intensity=0.6))
                elif chosen_title_anim == "shimmer":
                    parts.append(animation_engine.shimmer_effect(self.title, phase, intensity=0.5))
                else:
                    parts.append(Text(self.title))
            else:
                parts.append(Text(self.title))
        for i, step in enumerate(self.steps):
            for line in self._format_line(i, step):
                parts.append(line)
        display = Text("\n").join(parts) if parts else Text("")
        if self._live:
            # Guard Live.update from concurrent access by the background loop
            with self._render_lock:
                self._live.update(display)

    def start_step(self, index: int) -> None:
        self._active_index = index
        step = self.steps[index]
        step.status = "active"
        step.started_mono = time.monotonic()
        self._render()

    def update_active(
        self,
        *,
        percent: float | None = None,
        speed: str | None = None,
        eta: str | None = None,
        message: str | None = None,
    ) -> None:
        if self._active_index is None:
            return
        step = self.steps[self._active_index]
        if percent is not None:
            # Keep within [0, 0.99] to avoid looking finished prematurely
            clamped = max(0.0, min(percent, 0.99))
            step.last_percent = clamped
        if speed is not None:
            step.last_speed = speed
        if eta is not None:
            step.last_eta = eta
        if message:
            # Augment label temporarily for extra context
            step.note = message
        self._render()

    def set_active_hint_text(self, text: Text) -> None:
        """Set a rich hint Text under the active step."""
        if self._active_index is None:
            return
        step = self.steps[self._active_index]
        step.note_text = text
        self._render()

    def complete_step(self, note: str | None = None) -> None:
        if self._active_index is None:
            return
        idx = self._active_index
        step = self.steps[idx]
        step.status = "done"
        step.finished_mono = time.monotonic()
        if note:
            step.note = note
        self._active_index = None
        self._render()

    def fail_step(self, message: str) -> None:
        if self._active_index is None:
            return
        step = self.steps[self._active_index]
        step.status = "failed"
        step.note = message
        self._active_index = None
        self._render()

    def finish(self) -> None:
        if self._live is None:
            return
        # Ensure no step remains marked active
        self._active_index = None
        # Final render without spinners/bars
        self._render()
        # Stop render loop first
        if self._stop_event is not None:
            self._stop_event.set()
        if self._render_thread is not None:
            try:
                self._render_thread.join(timeout=1.0)
                # If thread is still alive, try a short extra wait once more to ensure cleanup
                if self._render_thread.is_alive():
                    self._render_thread.join(timeout=0.5)
            except Exception:
                pass
        self._live.__exit__(None, None, None)
        self._live = None

    # Convenience to update title dynamically
    def set_title(self, title: str, *, animation: str | None = None) -> None:
        self.title = title
        if animation is not None:
            self._title_animation = animation
        self._render()

    # Heuristic selection for active label animation
    def _select_active_label_animation(self, step: _Step) -> str | None:
        if not self._enable_animations:
            return None
        choice = self._active_label_animation
        if choice is None:
            return None
        if choice == "auto":
            # For long-running steps with a bar, prefer pulse; for short ones skip
            if step.show_bar and step.estimated_seconds:
                if step.estimated_seconds >= 120:
                    return "pulse"
                if step.estimated_seconds >= 30:
                    return "wave"
                return None
            # Non-bar steps are usually brief (e.g., Connecting); mild pulse
            return "pulse"
        if choice == "random":
            # Pick from subtle set to avoid playful bounce on labels
            return random.choice(["pulse", "wave", "shimmer"])
        return choice


class AllocationProgressAdapter:
    """Adapter to update the timeline during instance allocation."""

    def __init__(self, timeline: StepTimeline, step_index: int, estimated_seconds: int = 120):
        self.timeline = timeline
        self.step_index = step_index
        self.estimated_seconds = estimated_seconds
        self._start = None

    def __enter__(self):
        self.timeline.start_step(self.step_index)
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc is None:
            self.timeline.complete_step()
        else:
            self.timeline.fail_step(str(exc))

    def tick(self):
        if self._start is None:
            return
        elapsed = time.monotonic() - self._start
        pct = min(elapsed / self.estimated_seconds, 0.95)
        self.timeline.update_active(percent=pct)


class SSHWaitProgressAdapter:
    """Adapter to update the timeline during SSH readiness wait."""

    def __init__(
        self,
        timeline: StepTimeline,
        step_index: int,
        estimated_seconds: int,
        baseline_elapsed_seconds: int | None = None,
    ):
        self.timeline = timeline
        self.step_index = step_index
        self.estimated_seconds = estimated_seconds
        self.baseline_elapsed_seconds = baseline_elapsed_seconds
        self._start = None

    def __enter__(self):
        self.timeline.start_step(self.step_index)
        # If provided, seed this step with a baseline elapsed so the bar resumes correctly
        try:
            step = self.timeline.steps[self.step_index]
            step.baseline_elapsed_seconds = self.baseline_elapsed_seconds
        except Exception:
            pass
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc is None:
            self.timeline.complete_step()
        else:
            self.timeline.fail_step(str(exc))

    def update_eta(self, eta: str | None = None):
        if self._start is None:
            return
        base = self.baseline_elapsed_seconds or 0
        elapsed = time.monotonic() - self._start
        pct = min((base + elapsed) / self.estimated_seconds, 0.95)
        self.timeline.update_active(percent=pct, eta=eta)


class UploadProgressReporter:
    """Bridge reporter that maps code transfer progress to the timeline."""

    def __init__(self, timeline: StepTimeline, step_index: int):
        self.timeline = timeline
        self.step_index = step_index
        self._entered = False

    def ensure_started(self) -> None:
        """Public API used by context helpers to start timeline step once."""
        if not self._entered:
            self.timeline.start_step(self.step_index)
            self._entered = True

    # Matches IProgressReporter, but we deliberately avoid importing it to prevent tight coupling
    def ssh_wait_progress(self, message: str):  # noqa: D401
        class _Ctx:
            def __init__(self, outer: UploadProgressReporter):
                self.outer = outer

            def __enter__(self):
                self.outer.ensure_started()
                return self.outer

            def __exit__(self, exc_type, exc, tb):
                # Do not complete here; let transfer_progress complete
                return False

        return _Ctx(self)

    def transfer_progress(self, message: str):  # noqa: D401
        class _Ctx:
            def __init__(self, outer: UploadProgressReporter):
                self.outer = outer

            def __enter__(self):
                self.outer.ensure_started()
                return self.outer

            def __exit__(self, exc_type, exc, tb):
                if exc is None:
                    self.outer.timeline.complete_step()
                else:
                    self.outer.timeline.fail_step(str(exc))
                return False

        return _Ctx(self)

    def update_status(self, message: str) -> None:
        # Map to a subtle note; avoid excessive churn
        self.timeline.update_active(message=message)

    # Extended hook used when available by transfer manager
    def update_transfer(
        self, percentage: float | None, speed: str | None, eta: str | None, current_file: str | None
    ):
        note = None
        if current_file:
            note = f"Uploading: {current_file}"
        self.timeline.update_active(
            percent=(percentage / 100.0) if percentage is not None else None,
            speed=speed,
            eta=eta,
            message=note,
        )


class NullConsole:
    """Console that discards prints to avoid duplicate provider messages."""

    def print(self, *_args, **_kwargs):
        return None
