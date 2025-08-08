#!/usr/bin/env python3
"""Direct Pulumi + Flow SDK integration."""

import pulumi
import flow

# GPU instance
task = flow.run(
    "sleep infinity",
    instance_type="a100",
    max_price_per_hour=25.0,  # High bid for persistence
)

task.wait_for_status("RUNNING")

# Export state
pulumi.export("task_id", task.task_id)
pulumi.export("ip", task.instances[0].public_ip)
