"""Pricing visibility command.

Shows current pricing defaults and any user overrides, and explains how to
customize pricing via ~/.flow/config.yaml.
"""

from typing import Any, Dict, List, Tuple

import click

from .base import BaseCommand, console
from ..utils.table_styles import create_flow_table, wrap_table_in_panel
from ..utils.theme_manager import theme_manager
from flow._internal import pricing as pricing_core
from flow._internal.config import Config


class PricingCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "pricing"

    @property
    def help(self) -> str:
        return "Show current pricing defaults and how to customize overrides"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option(
            "--compact",
            is_flag=True,
            help="Compact output (fewer hints)",
        )
        def pricing(compact: bool = False):
            """Display merged pricing table and configuration guidance."""
            # Resolve overrides from config, merge with defaults
            try:
                cfg = Config.from_env(require_auth=False)
                overrides = None
                if cfg and isinstance(cfg.provider_config, dict):
                    overrides = cfg.provider_config.get("limit_prices")
                merged = pricing_core.get_pricing_table(overrides)
                have_overrides = bool(overrides)
            except Exception:
                merged = pricing_core.DEFAULT_PRICING
                have_overrides = False

            # Build table of prices (focus on h100 and a100 for clarity)
            table = create_flow_table(title=None, show_borders=True, padding=1)
            table.add_column("GPU", style=theme_manager.get_color("accent"), no_wrap=True)
            table.add_column("Low", justify="right")
            table.add_column("Med", justify="right")
            table.add_column("High", justify="right")

            # Only show key GPUs commonly used: h100 and a100; include 'default' last if present
            preferred: List[str] = [k for k in ("h100", "a100") if k in merged]
            extras: List[str] = []
            if "default" in merged:
                extras = ["default"]
            keys: List[str] = preferred + extras
            for gpu in keys:
                prices: Dict[str, float] = merged.get(gpu, {})
                low = prices.get("low")
                med = prices.get("med")
                high = prices.get("high")
                table.add_row(
                    gpu,
                    f"${low:.2f}/hr" if isinstance(low, (int, float)) else "-",
                    f"${med:.2f}/hr" if isinstance(med, (int, float)) else "-",
                    f"${high:.2f}/hr" if isinstance(high, (int, float)) else "-",
                )

            wrap_table_in_panel(
                table,
                "Mithril spot limit prices (per GPU per hour)",
                console,
            )

            # Source info
            if have_overrides:
                console.print(
                    "Using merged pricing: Flow defaults + your overrides from [bold]~/.flow/config.yaml[/bold] at [bold]mithril.limit_prices[/bold].\n"
                )
            else:
                console.print(
                    "Using Flow default pricing. Add overrides in [bold]~/.flow/config.yaml[/bold] under [bold]mithril.limit_prices[/bold] to customize.\n"
                )

            if not compact:
                console.print("[dim]About Mithril spot limit prices:[/dim]")
                console.print(
                    "  • These are [bold]limit prices[/bold] for Mithril spot bids. You are billed at the current market spot price (≤ your limit)."
                )
                console.print(
                    "  • Priority tiers (low/med/high) pick a per‑GPU limit; instance limit = per‑GPU × GPU count."
                )
                console.print(
                    "  • Learn more: Spot bids and auction dynamics: https://docs.mithril.ai/compute-and-storage/spot-bids\n"
                )

                # YAML guidance
                console.print("Example: set organization‑wide overrides in [bold]~/.flow/config.yaml[/bold]. Values below are illustrative (low < default, med = default, high > default):\n")
                yaml_snippet = (
                    "provider: mithril\n"
                    "mithril:\n"
                    "  project: my-project\n"
                    "  region: us-central1-b\n"
                    "  limit_prices:\n"
                    "    h100:\n"
                    "      low: 3.50   # lower than Flow default (4.00)\n"
                    "      med: 8.00   # same as Flow default (8.00)\n"
                    "      high: 18.00  # higher than Flow default (16.00)\n"
                    "    a100:\n"
                    "      low: 2.50   # lower than Flow default (3.00)\n"
                    "      med: 6.00   # same as Flow default (6.00)\n"
                    "      high: 13.00  # higher than Flow default (12.00)\n"
                )
                console.print(f"[dim]\n--- YAML ---\n[/dim]{yaml_snippet}[dim]---\n[/dim]")

                console.print("Tips:")
                console.print("  • Partial overrides are fine; unspecified tiers fall back to Flow defaults")
                console.print("  • Per‑run: use 'flow run -p high' or '--max-price-per-hour 24' to override\n")

        return pricing


# Export command instance
command = PricingCommand()


