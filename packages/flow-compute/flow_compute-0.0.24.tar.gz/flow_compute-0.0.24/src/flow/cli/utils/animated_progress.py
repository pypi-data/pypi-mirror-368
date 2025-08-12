"""Animated progress indicators for CLI operations.

Custom progress indicators with animated text, including dynamic ellipsis
animations for status messages.
"""

import os
import threading
import time
from datetime import datetime, timezone

from rich.console import Console
from rich.live import Live
from rich.text import Text

from flow.cli.utils.animation_config import (
    AnimationStyle,
    get_animation_config,
    get_animation_style,
)
from flow.cli.utils.animations import animation_engine


class AnimatedEllipsisProgress:
    """Progress indicator with spinner and animated ellipsis.

    Creates a progress bar with rich's spinner and a message with
    cycling ellipsis animation (., .., ...).
    """

    def __init__(
        self,
        console: Console,
        message: str,
        transient: bool = True,
        animation_style: AnimationStyle | None = None,
        start_immediately: bool = False,
        estimated_seconds: int | None = None,
        show_progress_bar: bool = False,
        task_created_at: datetime | None = None,
    ):
        """Initialize animated progress.

        Args:
            console: Rich console instance
            message: Base message to display (without ellipsis)
            transient: Whether to clear progress when done
            animation_style: Type of text animation to use
            start_immediately: If True, start animation in __init__ for immediate feedback
            estimated_seconds: Estimated time in seconds for progress bar
            show_progress_bar: Whether to show filling progress bar
            task_created_at: Task creation time (for reconnecting to existing tasks)
        """
        self.console = console
        self.base_message = message
        self.transient = transient
        # Use centralized animation selection
        self.animation_style = get_animation_style(animation_style)
        self.animation_config = get_animation_config(self.animation_style)
        self._live: Live | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._ellipsis_count = 0
        # Track cadence for ellipsis updates using monotonic time
        self._last_ellipsis_ts = time.monotonic()
        # Lock for thread-safe message updates
        self._lock = threading.Lock()

        # Use task creation time if reconnecting, otherwise use current time
        if task_created_at:
            # Ensure timezone-aware comparison
            if task_created_at.tzinfo is None:
                task_created_at = task_created_at.replace(tzinfo=timezone.utc)
            self.start_time = task_created_at.timestamp()
        else:
            self.start_time = time.time()

        # Monotonic clock for animation/progress calculations
        self.start_time_monotonic = time.monotonic()

        self.estimated_seconds = estimated_seconds
        self.show_progress_bar = show_progress_bar and estimated_seconds is not None
        # Reset animation engine's start time for fresh animations (monotonic)
        animation_engine.start_time = time.monotonic()
        self._active = False
        self._started_immediately = False

        # Adaptive frame interval: keep high FPS for complex text effects
        self._frame_interval = 0.05 if self.animation_style in ("shimmer", "wave") else 0.08

        # Start immediately if requested - provides instant feedback
        if start_immediately:
            self._start_immediate()

    def _animate(self) -> None:
        """Animation loop for updating display."""
        # Choose spinner set with ASCII fallback when needed
        ascii_only = False
        try:
            enc = getattr(self.console, "encoding", None)
            if not enc or "UTF" not in str(enc).upper() or os.getenv("FLOW_ASCII") == "1":
                ascii_only = True
        except Exception:
            ascii_only = False

        spinner_frames = (
            animation_engine.SPINNERS["line"] if ascii_only else animation_engine.SPINNERS["dots"]
        )

        while not self._stop_event.is_set():
            # Use monotonic time for animation stability
            elapsed_monotonic = time.monotonic() - self.start_time_monotonic

            # Get spinner frame
            spinner_phase = animation_engine.get_phase(0.8)
            spinner = animation_engine.get_spinner_frame(spinner_frames, spinner_phase)

            # Snapshot message under lock to avoid tearing mid-frame
            with self._lock:
                current_message = self.base_message

            # Show progress bar if enabled
            if self.show_progress_bar:
                # Calculate progress (cap at 95% to avoid false completion)
                progress_pct = min(elapsed_monotonic / self.estimated_seconds, 0.95)

                # Reuse existing progress_bar from animation_engine
                bar = animation_engine.progress_bar(
                    progress_pct,
                    width=30,
                    style="gradient",  # Subtle gradient edge like health command
                    animated=True,
                )

                # Format time display using wall clock (respects task_created_at)
                elapsed_wall = time.time() - self.start_time
                elapsed_str = f"{int(elapsed_wall)}s"
                estimate_str = f"{self.estimated_seconds}s"

                # Stack vertically: spinner + message on first line, progress bar on second
                line1 = f"{spinner} {current_message}"
                line2 = f"  {bar}  {elapsed_str}/{estimate_str}"
                display = Text(f"{line1}\n{line2}")

            elif self.animation_style == "ellipsis":
                # Classic ellipsis animation with time-based cadence
                now_mono = time.monotonic()
                if now_mono - self._last_ellipsis_ts >= self.animation_config.duration:
                    self._ellipsis_count = (self._ellipsis_count % 3) + 1
                    self._last_ellipsis_ts = now_mono
                dots = "." * self._ellipsis_count
                display = Text(f"{spinner} {current_message}{dots}")
            else:
                # Use rich animations - same as flow animations command
                phase = animation_engine.get_phase(duration=self.animation_config.duration)

                if self.animation_style == "wave":
                    animated_text = animation_engine.wave_pattern(
                        current_message, phase, intensity=self.animation_config.intensity
                    )
                elif self.animation_style == "pulse":
                    animated_text = animation_engine.pulse_effect(
                        current_message, phase, intensity=self.animation_config.intensity
                    )
                elif self.animation_style == "shimmer":
                    animated_text = animation_engine.shimmer_effect(
                        current_message, phase, intensity=self.animation_config.intensity
                    )
                elif self.animation_style == "bounce":
                    animated_text = animation_engine.bounce_effect(
                        current_message, phase, intensity=self.animation_config.intensity
                    )
                else:
                    animated_text = Text(current_message)

                # Display spinner + animated text (exactly like flow animations)
                display = Text(f"{spinner} ") + animated_text

            if self._live and self._active:
                self._live.update(display)

            time.sleep(self._frame_interval)

    def _start_immediate(self):
        """Start animation immediately for instant feedback."""
        try:
            # TTY/CI-safe fallback: skip Live when not interactive
            if os.getenv("CI") or not getattr(self.console, "is_terminal", True):
                self._live = None
                self._active = False
                self._started_immediately = True
                return
            self._live = Live(
                Text(""),  # Initial empty display
                console=self.console,
                refresh_per_second=20,
                transient=self.transient,
            )
            self._live.__enter__()
        except Exception as e:
            if "Only one live display may be active" in str(e):
                # There's already a Live display active, skip animation
                self._live = None
                self._active = False
                return
            raise

        if self._live:
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
            self._active = True
        self._started_immediately = True

    def __enter__(self):
        """Start the animated display."""
        if self._started_immediately:
            # Already started, just return
            return self

        try:
            # TTY/CI-safe fallback: skip Live when not interactive
            if os.getenv("CI") or not getattr(self.console, "is_terminal", True):
                self._live = None
                self._active = False
                return self
            self._live = Live(
                Text(""),  # Initial empty display
                console=self.console,
                refresh_per_second=20,
                transient=self.transient,
            )
            self._live.__enter__()
        except Exception as e:
            if "Only one live display may be active" in str(e):
                # There's already a Live display active, skip animation
                self._live = None
                self._active = False
                return self
            raise

        if self._live:
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
            self._active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the animated display."""
        if not self._active:
            return  # Already stopped

        self._active = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._live:
            self._live.__exit__(exc_type, exc_val, exc_tb)

    def update_message(self, new_message: str):
        """Update the progress message while animation is running.

        Args:
            new_message: New message to display
        """
        with self._lock:
            self.base_message = new_message
