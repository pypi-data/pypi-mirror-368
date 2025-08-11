Reservations
============

Overview
--------
Reservations guarantee access to dedicated GPUs for a fixed window. Use them for launches that must start at a specific time and run uninterrupted.

Quick start
-----------

Create a reservation and schedule a run:

```bash
flow run training.yaml \
  --allocation reserved \
  --start 2025-01-31T18:00:00Z \
  --duration 6
```

Bind to an existing reservation window:

```bash
flow run training.yaml \
  --allocation reserved \
  --reservation-id rsv_abc123
```

Manage reservations:

```bash
flow reservations create \
  --instance-type 8xh100 \
  --region us-central1-b \
  --quantity 4 \
  --start 2025-01-31T18:00:00Z \
  --duration 12 \
  --name my-window

flow reservations list
flow reservations show rsv_abc123
```

Status and alloc views
----------------------

- `flow status --show-reservations` shows a compact panel of upcoming/active windows.
- Wide mode (`--wide`) adds Start In and Window columns per task when applicable.
- `flow alloc` shows a top hint for the nearest upcoming window.

Notes
-----

- Reservations are billed for the full window and cannot be canceled.
- Persistent volumes must be in the same region.
- For multi-node, set `num_instances` to the number of nodes; instances in a reservation are interconnected.

