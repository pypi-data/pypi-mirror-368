from __future__ import annotations

import textwrap

from flow.providers.mithril.runtime.startup.sections.base import ScriptContext, ScriptSection
import logging as _log


class RuntimeMonitorSection(ScriptSection):
    @property
    def name(self) -> str:
        return "runtime_monitor"

    @property
    def priority(self) -> int:
        return 90

    def should_include(self, context: ScriptContext) -> bool:
        return bool(context.max_run_time_hours)

    def generate(self, context: ScriptContext) -> str:
        if not context.max_run_time_hours:
            return ""
        max_runtime_seconds = int(context.max_run_time_hours * 3600)
        api_key = context.environment.get("_FLOW_MITHRIL_API_KEY", "")
        api_url = context.environment.get("_FLOW_MITHRIL_API_URL", "https://api.foundryplatform.io")
        project = context.environment.get("_FLOW_MITHRIL_PROJECT", "")
        if not api_key or not project:
            return ""
        timer_seconds = max(max_runtime_seconds - 120, 60)
        # Write config; keep small inline block
        # Avoid exposing secrets in world-readable files; restrict permissions
        config_block = textwrap.dedent(
            f"""
            mkdir -p /var/lib/flow
            umask 077
            cat > /var/lib/flow/task-runtime.conf <<EOF
 TASK_NAME="{context.task_name or 'unknown'}"
 MAX_RUNTIME_HOURS="{context.max_run_time_hours}"
 MITHRIL_API_KEY="{api_key}"
 MITHRIL_API_URL="{api_url}"
 MITHRIL_PROJECT="{project}"
 EOF
            """
        ).strip()

        cancel_script_body = None
        timer_unit_body = None
        service_unit_body = None

        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                cancel_script_body = self.template_engine.render_file(
                    _Path("sections/runtime_cancel.sh.j2"), {}
                ).strip()
                timer_unit_body = self.template_engine.render_file(
                    _Path("sections/runtime_limit.timer.j2"), {"timer_seconds": timer_seconds}
                ).strip()
                service_unit_body = self.template_engine.render_file(
                    _Path("sections/runtime_limit.service.j2"), {}
                ).strip()
            except Exception:
                _log.debug("RuntimeMonitorSection: template render failed; using inline units", exc_info=True)
                cancel_script_body = None
                timer_unit_body = None
                service_unit_body = None

        if cancel_script_body is None:
            cancel_script_body = textwrap.dedent(
                """
                #!/bin/bash
                set -euo pipefail
                source /var/lib/flow/task-runtime.conf
                echo "[$(date)] Flow runtime limit reached, initiating graceful shutdown"
                docker stop -t 30 main 2>/dev/null || true
                sleep 10
                INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id || hostname)
                TASK_ID=$(curl -s --max-time 10 -H "Authorization: Bearer $MITHRIL_API_KEY" \
                    "$MITHRIL_API_URL/v2/spot/bids?project=$MITHRIL_PROJECT" | \
                    INSTANCE_ID="$INSTANCE_ID" python3 -c "import sys,json,os; iid=os.environ.get('INSTANCE_ID',''); d=json.load(sys.stdin); b=d if isinstance(d,list) else d.get('data',[]); print(next((x.get('fid') for x in b for i in x.get('instances',[]) if i.get('instance_id')==iid), 'unknown'))")
                if [ "$TASK_ID" != "unknown" ]; then
                  curl -sS -X DELETE -H "Authorization: Bearer $MITHRIL_API_KEY" -H "Content-Type: application/json" "$MITHRIL_API_URL/v2/spot/bids/$TASK_ID" --max-time 30 || true
                fi
                """
            ).strip()

        if timer_unit_body is None:
            timer_unit_body = textwrap.dedent(
                f"""
                [Unit]
                Description=Flow Runtime Limit Timer
                [Timer]
                OnBootSec={timer_seconds}s
                AccuracySec=1min
                Persistent=true
                [Install]
                WantedBy=timers.target
                """
            ).strip()

        if service_unit_body is None:
            service_unit_body = textwrap.dedent(
                """
                [Unit]
                Description=Flow Runtime Limit Enforcement
                [Service]
                Type=oneshot
                ExecStart=/usr/local/bin/flow-runtime-cancel.sh
                Restart=no
                """
            ).strip()

        return textwrap.dedent(
            f"""
            {config_block}
            cat > /usr/local/bin/flow-runtime-cancel.sh << 'CANCEL_EOF'
{cancel_script_body}
            CANCEL_EOF
            chmod +x /usr/local/bin/flow-runtime-cancel.sh
            cat > /etc/systemd/system/flow-runtime-limit.timer << TIMER_EOF
{timer_unit_body}
            TIMER_EOF
            cat > /etc/systemd/system/flow-runtime-limit.service << 'SERVICE_EOF'
{service_unit_body}
            SERVICE_EOF
            systemctl daemon-reload
            systemctl enable flow-runtime-limit.timer
            systemctl start flow-runtime-limit.timer
            """
        ).strip()


__all__ = ["RuntimeMonitorSection"]
