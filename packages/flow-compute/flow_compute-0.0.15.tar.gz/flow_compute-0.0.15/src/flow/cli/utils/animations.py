"""Rich animation patterns for Flow CLI.

Provides various animation effects including wave patterns, pulse effects,
and state-based animations for enhanced visual feedback.
"""

import math
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from rich.text import Text
from rich.style import Style


class AnimationType(Enum):
    """Available animation types."""

    WAVE = "wave"
    PULSE = "pulse"
    SPINNER = "spinner"
    PROGRESS = "progress"
    SHIMMER = "shimmer"
    BOUNCE = "bounce"


@dataclass
class AnimationPattern:
    """Defines an animation pattern."""

    type: AnimationType
    duration: float  # Duration in seconds for one cycle
    intensity: float = 1.0  # Animation intensity (0.0 to 1.0)
    delay: float = 0.0  # Delay between elements
    custom_chars: Optional[List[str]] = None  # For spinner animations


class AnimationEngine:
    """Manages animation patterns and states for Flow CLI."""

    # Built-in spinner patterns
    SPINNERS = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "dots2": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
        "line": ["-", "\\", "|", "/"],
        "arrow": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
        "pulse": ["◯", "◉", "●", "◉"],
        "wave": ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"],
        "bounce": ["⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈"],
        "bar": ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"],
    }

    # Task status animations
    STATUS_ANIMATIONS = {
        "pending": AnimationPattern(AnimationType.PULSE, duration=2.0, intensity=0.6),
        "preparing": AnimationPattern(
            AnimationType.SPINNER, duration=0.8, custom_chars=SPINNERS["dots"]
        ),
        "running": AnimationPattern(AnimationType.WAVE, duration=3.0, intensity=0.8),
        "preempting": AnimationPattern(AnimationType.PULSE, duration=1.0, intensity=1.0),
        "completed": AnimationPattern(AnimationType.SHIMMER, duration=2.0, intensity=0.5),
        "failed": AnimationPattern(AnimationType.PULSE, duration=0.5, intensity=1.0),
    }

    def __init__(self):
        """Initialize animation engine."""
        self.start_time = time.time()

    def get_phase(self, duration: float, delay: float = 0.0) -> float:
        """Calculate current animation phase.

        Args:
            duration: Duration of one animation cycle in seconds
            delay: Delay offset in seconds

        Returns:
            Phase value between 0.0 and 1.0
        """
        elapsed = time.time() - self.start_time + delay
        return (elapsed % duration) / duration

    def wave_pattern(self, text: str, phase: float, intensity: float = 1.0) -> Text:
        """Generate wave animation for text.

        Args:
            text: Text to animate
            phase: Current phase (0.0 to 1.0)
            intensity: Wave intensity (0.0 to 1.0)

        Returns:
            Animated Rich Text object
        """
        result = Text()
        text_len = len(text)

        for i, char in enumerate(text):
            # Calculate wave position for this character
            char_phase = (phase + i / text_len) % 1.0

            # Sine wave for smooth animation
            brightness = 0.5 + 0.5 * math.sin(char_phase * 2 * math.pi) * intensity

            # Convert brightness to color
            if brightness > 0.75:
                style = Style(color="bright_white", bold=True)
            elif brightness > 0.5:
                style = Style(color="white")
            elif brightness > 0.25:
                style = Style(color="bright_black")
            else:
                style = Style(color="black")

            result.append(char, style=style)

        return result

    def pulse_effect(self, text: str, phase: float, intensity: float = 1.0) -> Text:
        """Generate pulse effect for text.

        Args:
            text: Text to animate
            phase: Current phase (0.0 to 1.0)
            intensity: Pulse intensity (0.0 to 1.0)

        Returns:
            Animated Rich Text object
        """
        # Smooth pulse using sine wave
        brightness = 0.5 + 0.5 * math.sin(phase * 2 * math.pi) * intensity

        if brightness > 0.75:
            style = Style(color="bright_white", bold=True)
        elif brightness > 0.5:
            style = Style(color="white")
        elif brightness > 0.25:
            style = Style(color="bright_black")
        else:
            style = Style(dim=True)

        return Text(text, style=style)

    def shimmer_effect(self, text: str, phase: float, intensity: float = 1.0) -> Text:
        """Generate shimmer effect for text.

        Args:
            text: Text to animate
            phase: Current phase (0.0 to 1.0)
            intensity: Shimmer intensity (0.0 to 1.0)

        Returns:
            Animated Rich Text object
        """
        result = Text()
        text_len = len(text)
        shimmer_width = 0.2  # Width of shimmer band

        for i, char in enumerate(text):
            # Calculate position in shimmer cycle
            char_pos = i / text_len
            shimmer_pos = phase

            # Calculate distance from shimmer center
            distance = abs(char_pos - shimmer_pos)
            if distance > 0.5:  # Handle wrap-around
                distance = 1.0 - distance

            # Apply shimmer effect based on distance
            if distance < shimmer_width:
                brightness = 1.0 - (distance / shimmer_width)
                brightness *= intensity

                if brightness > 0.5:
                    style = Style(color="bright_white", bold=True)
                else:
                    style = Style(color="white")
            else:
                style = Style()

            result.append(char, style=style)

        return result

    def bounce_effect(self, text: str, phase: float, intensity: float = 1.0) -> Text:
        """Generate bounce effect for text.

        Args:
            text: Text to animate
            phase: Current phase (0.0 to 1.0)
            intensity: Bounce intensity (0.0 to 1.0)

        Returns:
            Animated Rich Text object
        """
        result = Text()
        text_len = len(text)

        for i, char in enumerate(text):
            # Calculate bounce position for this character
            char_phase = (phase + i / text_len * 0.5) % 1.0

            # Bounce curve (parabola)
            if char_phase < 0.5:
                height = 4 * char_phase * (1 - char_phase)
            else:
                height = 0

            # Apply vertical offset using Unicode combining characters
            if height > 0.5 * intensity and char != " ":
                # Use superscript for bounce effect
                result.append(char, style=Style(bold=True))
            else:
                result.append(char)

        return result

    def get_spinner_frame(self, pattern: List[str], phase: float) -> str:
        """Get current spinner frame.

        Args:
            pattern: List of spinner characters
            phase: Current phase (0.0 to 1.0)

        Returns:
            Current spinner character
        """
        frame_index = int(phase * len(pattern))
        return pattern[frame_index % len(pattern)]

    def state_animation(self, status: str, text: str) -> Text:
        """Get appropriate animation for task status.

        Args:
            status: Task status
            text: Text to animate

        Returns:
            Animated text based on status
        """
        pattern = self.STATUS_ANIMATIONS.get(status.lower())
        if not pattern:
            return Text(text)

        phase = self.get_phase(pattern.duration, pattern.delay)

        if pattern.type == AnimationType.WAVE:
            return self.wave_pattern(text, phase, pattern.intensity)
        elif pattern.type == AnimationType.PULSE:
            return self.pulse_effect(text, phase, pattern.intensity)
        elif pattern.type == AnimationType.SHIMMER:
            return self.shimmer_effect(text, phase, pattern.intensity)
        elif pattern.type == AnimationType.BOUNCE:
            return self.bounce_effect(text, phase, pattern.intensity)
        elif pattern.type == AnimationType.SPINNER and pattern.custom_chars:
            spinner = self.get_spinner_frame(pattern.custom_chars, phase)
            return Text(f"{spinner} {text}")
        else:
            return Text(text)

    def progress_bar(
        self, progress: float, width: int = 20, animated: bool = True, style: str = "default"
    ) -> Text:
        """Create an animated progress bar.

        Args:
            progress: Progress value (0.0 to 1.0)
            width: Bar width in characters
            animated: Whether to animate the bar
            style: Bar style ("default", "smooth", "blocks")

        Returns:
            Progress bar as Rich Text
        """
        if style == "smooth":
            chars = " ▏▎▍▌▋▊▉█"
            filled = int(progress * width * 8)
            full_blocks = filled // 8
            partial_block = filled % 8

            bar = "█" * full_blocks
            if partial_block > 0 and full_blocks < width:
                bar += chars[partial_block]
            bar += " " * (width - len(bar))

        elif style == "blocks":
            filled = int(progress * width)
            bar = "■" * filled + "□" * (width - filled)

        else:  # default
            filled = int(progress * width)
            bar = "=" * filled + "-" * (width - filled)

        result = Text(f"[{bar}]")

        if animated and progress < 1.0:
            # Add shimmer effect to the progress edge
            phase = self.get_phase(1.0)
            if filled > 0 and filled < width:
                edge_pos = filled - 1
                if phase > 0.5:
                    result.stylize(Style(bold=True), edge_pos + 1, edge_pos + 2)

        return result


# Global animation engine instance
animation_engine = AnimationEngine()
