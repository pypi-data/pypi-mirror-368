"""Pricing visibility command.

Shows current pricing defaults and any user overrides, and explains how to
customize pricing via ~/.flow/config.yaml.
"""

from typing import Any

import click

from flow._internal import pricing as pricing_core
from flow._internal.config import Config
from flow.cli.commands.base import BaseCommand, console


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
        @click.option(
            "--market",
            is_flag=True,
            help="Show current market spot prices by region and instance type",
        )
        @click.option(
            "--region",
            help="Filter market pricing by region (e.g., us-central1-b)",
        )
        def pricing(compact: bool = False, market: bool = False, region: str | None = None):
            """Display merged pricing table and configuration guidance."""
            # Market view: live spot prices and availability
            if market:
                try:
                    from flow import Flow
                    from flow.cli.utils.table_styles import create_flow_table, wrap_table_in_panel
                    from flow.cli.utils.theme_manager import theme_manager

                    client = Flow()
                    requirements: dict[str, Any] = {}
                    if region:
                        requirements["region"] = region
                    # Fetch up to 100 current auctions converted to AvailableInstance
                    instances = client.find_instances(requirements, limit=100)

                    # Build table
                    table = create_flow_table(title=None, show_borders=True, padding=1, expand=False)
                    table.add_column(
                        "Region", style=theme_manager.get_color("accent"), no_wrap=True
                    )
                    table.add_column("Type", no_wrap=True)
                    table.add_column("Price/inst", justify="right")
                    table.add_column("Price/GPU", justify="right")
                    table.add_column("GPUs", justify="right")
                    table.add_column("Avail", justify="right")

                    def _per_gpu_price(inst) -> str:
                        try:
                            g = int(inst.gpu_count or 0)
                            if g > 0 and inst.price_per_hour:
                                return f"${inst.price_per_hour / g:.2f}/hr"
                        except Exception:
                            pass
                        return "-"

                    # Sort by region then price
                    instances.sort(key=lambda i: (i.region or "", i.price_per_hour))
                    for inst in instances:
                        table.add_row(
                            inst.region or "",
                            inst.instance_type,
                            f"${inst.price_per_hour:.2f}/hr",
                            _per_gpu_price(inst),
                            str(inst.gpu_count or "-"),
                            str(inst.available_quantity or "-"),
                        )

                    wrap_table_in_panel(
                        table,
                        f"Current spot prices{' • ' + region if region else ''}",
                        console,
                    )

                    # Show provider-specific console link when Mithril is active
                    import os as _os
                    from flow.links import WebLinks

                    if (_os.environ.get("FLOW_PROVIDER") or "mithril").lower() == "mithril":
                        console.print(
                            f"More details and price graphs: {WebLinks.instances_spot()}\n"
                        )
                    else:
                        console.print(
                            "More details and price graphs are available in your provider console\n"
                        )
                except Exception as e:
                    console.print(f"[red]Failed to fetch market prices:[/red] {e}")
                return

            # Resolve overrides from config, merge with defaults (default view)
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
            table = create_flow_table(title=None, show_borders=True, padding=1, expand=False)
            table.add_column("GPU", style=theme_manager.get_color("accent"), no_wrap=True)
            table.add_column("Low", justify="right")
            table.add_column("Med", justify="right")
            table.add_column("High", justify="right")

            # Only show key GPUs commonly used: h100 and a100; include 'default' last if present
            preferred: list[str] = [k for k in ("h100", "a100") if k in merged]
            extras: list[str] = []
            if "default" in merged:
                extras = ["default"]
            keys: list[str] = preferred + extras
            for gpu in keys:
                prices: dict[str, float] = merged.get(gpu, {})
                low = prices.get("low")
                med = prices.get("med")
                high = prices.get("high")
                table.add_row(
                    gpu,
                    f"${low:.2f}/hr" if isinstance(low, (int, float)) else "-",
                    f"${med:.2f}/hr" if isinstance(med, (int, float)) else "-",
                    f"${high:.2f}/hr" if isinstance(high, (int, float)) else "-",
                )

            wrap_table_in_panel(table, "Spot limit prices (per GPU per hour)", console)

            # Source info
            if have_overrides:
                console.print(
                    "Using merged pricing: Flow defaults + your overrides in ~/.flow/config.yaml under provider-specific pricing.\n"
                )
            else:
                console.print(
                    "Using Flow default pricing. Add overrides in ~/.flow/config.yaml under your provider-specific pricing to customize.\n"
                )

            if not compact:
                console.print("[dim]About spot limit prices:[/dim]")
                console.print(
                    "  • These are [bold]limit prices[/bold] used for spot capacity; you are billed at the current market spot price (≤ your limit)."
                )
                console.print(
                    "  • Priority tiers (low/med/high) pick a per‑GPU limit; instance limit = per‑GPU × GPU count."
                )
                console.print("  • Learn more: consult your provider docs for spot bids/auctions\n")

                # YAML guidance
                console.print(
                    "Example: set organization‑wide overrides in [bold]~/.flow/config.yaml[/bold]. Values below are illustrative (low < default, med = default, high > default):\n"
                )
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
                console.print(
                    "  • Partial overrides are fine; unspecified tiers fall back to Flow defaults"
                )
                console.print(
                    "  • Per‑run: use 'flow run -p high' or '--max-price-per-hour 24' to override\n"
                )

            # Next steps
            try:
                actions = [
                    "Run with high priority: [accent]flow run task.yaml -p high[/accent]",
                    "Show allocations: [accent]flow alloc[/accent]",
                    "See market prices: [accent]flow pricing --market[/accent]",
                ]
                self.show_next_actions(actions)
            except Exception:
                pass

        return pricing


# Export command instance
command = PricingCommand()
