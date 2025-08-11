# Pricing and Topology Feature Design

This document proposes minimal, high‑impact additions to expose spot price visibility and machine topology in Flow while maintaining clean abstractions and small blast radius.

## Goals
- Pricing
  - Provide a quick way to view current spot prices per region/type in terminal
  - Link to rich price graphs in the Mithril console
  - Keep default limit‑price guidance in `flow pricing` intact; no behavior changes
- Topology
  - Help users understand internode/intranode interconnect for planning clusters
  - Allow optional topology preferences in task configs (future), while preserving provider‑agnostic API

## Non‑Goals
- No scheduling policy changes
- No provider‑specific coupling in public APIs beyond optional fields
- No persistence or heavy caching beyond existing TTLs

## User Stories
- As a user, I want to see current spot prices and availability so I can set competitive limit prices.
- As a user, I want to understand which regions and instance types offer InfiniBand vs Ethernet for multi‑node jobs.

## CLI UX
- Pricing
  - Extend `flow pricing` with an optional live view flag:
    - `flow pricing --market [--region us-central1-b]`
    - Shows a table of region, type, price per instance, price per GPU, GPUs, available
    - Prints a link to Mithril console for graphs
  - Default `flow pricing` (no flag) remains a config/limit‑price helper.
- Topology
  - New command (future): `flow topology [--region <r>] [--type <t>] [--json]`
    - Displays internode (e.g., InfiniBand/IB_3200/Ethernet) and intranode (e.g., SXM5/PCIe)
    - Sorted to prefer stronger interconnects, then by price

## API/Model Design (Future‑proofing)
- Optional fields (provider‑agnostic) on domain models:
  - `AvailableInstance`: `internode_interconnect?: str`, `intranode_interconnect?: str`
  - `TaskConfig` (preferences only): `internode_interconnect?: str`, `intranode_interconnect?: str`
- Providers may populate these when available; Flow surfaces them without hard dependencies.
- Providers may optionally filter by these in their internal selection logic.

## Data Sources
- Live pricing/availability via existing Mithril endpoints already used by provider:
  - `/v2/spot/availability` (price/capacity by region/type)
- Rich graphs: `https://app.mithril.ai/instances/spot` (linked from CLI)

## Implementation Plan (Phased)
1) Pricing live view flag (low risk)
   - Add `--market [--region]` to `flow pricing`
   - Reuse `Flow.find_instances({...})` to fetch up to N current offers
   - Render table with per‑instance and per‑GPU price; sorted by region then price
   - Add console link for graphs
   - Guard with try/except; keep default view untouched

2) Topology readout (new command; medium risk, behind feature flag if needed)
   - `flow topology` reads `AvailableInstance` fields, if present
   - Filter by optional `--region`, `--type`; JSON output for automation
   - If topology fields are absent, show “-” and keep working

3) Optional preferences (defer by default)
   - Add optional prefs to `TaskConfig`
   - Provider integrates these into its auction matching if supported
   - Backward compatible: omit fields → existing behavior

## Backward Compatibility & Safety
- Default behaviors unchanged
- All new fields optional; all new flags opt‑in
- No changes to submission, billing, or scheduling logic

## Edge Cases & Failure Modes
- Pricing endpoint transient failures → show a friendly error and return
- Missing topology metadata → display “-” (do not fail)
- Large outputs → cap at N entries; possibly add `--json` for scripts

## Testing Strategy
- Unit: table formatting for pricing and topology; parse per‑GPU price correctly
- Integration (mocked HTTP): verify `--market` invokes availability API and renders rows
- CLI: golden snapshots for output with/without flags

## Rollout
- Phase 1: `flow pricing --market` only
- Phase 2: `flow topology` command in a minor release
- Phase 3 (optional): `TaskConfig` preferences + provider matching behind safety checks

## Rationale
- Minimal edits leverage existing availability and pricing plumbing
- Adds high value (price transparency, interconnect clarity) without invasive changes
- Aligns with SOLID/DRY: optional metadata flows through existing models; CLI remains a thin presentation layer
