from __future__ import annotations

import textwrap

from flow.providers.mithril.runtime.startup.sections.base import ScriptContext, ScriptSection
from flow.providers.mithril.runtime.startup.utils import ensure_command_available


class PortForwardingSection(ScriptSection):
    @property
    def name(self) -> str:
        return "port_forwarding"

    @property
    def priority(self) -> int:
        return 20

    def should_include(self, context: ScriptContext) -> bool:
        return bool(context.ports)

    def generate(self, context: ScriptContext) -> str:
        if not context.ports:
            return ""
        nginx_configs = [self._generate_nginx_config(port) for port in context.ports]
        nginx_config_blob = "\n".join(nginx_configs)
        return textwrap.dedent(
            f"""
            # Only configure port forwarding on head node (rank 0)
            if [ "${{FLOW_NODE_RANK:-0}}" != "0" ]; then
              echo "[port_forwarding] skipping on non-head node (rank=${{FLOW_NODE_RANK:-0}})"
            else
              echo "Configuring port forwarding for ports: {', '.join(map(str, context.ports))}"
              {ensure_command_available('nginx')}
              rm -f /etc/nginx/sites-enabled/default || true
              {nginx_config_blob}
              nginx -t || true
              if command -v systemctl >/dev/null 2>&1; then
                  systemctl enable nginx || true
                  systemctl restart nginx || true
              else
                  nginx -s reload || nginx || true
              fi
              {self._generate_foundrypf_service()}
            fi
        """
        ).strip()

    def _generate_nginx_config(self, port: int) -> str:
        # Prefer template for the NGINX server block; fallback to inline
        server_block = None
        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                server_block = self.template_engine.render_file(
                    _Path("sections/nginx_server_block.conf.j2"), {"port": port}
                ).strip()
            except Exception:
                server_block = None

        if server_block is None:
            server_block = textwrap.dedent(
                f"""
                server {{
                    listen {port};
                    server_name _;
                    location / {{
                        proxy_pass http://127.0.0.1:{port};
                        proxy_http_version 1.1;
                        proxy_set_header Upgrade $http_upgrade;
                        proxy_set_header Connection 'upgrade';
                        proxy_set_header Host $host;
                        proxy_set_header X-Real-IP $remote_addr;
                        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                        proxy_set_header X-Forwarded-Proto $scheme;
                        proxy_cache_bypass $http_upgrade;
                        proxy_read_timeout 86400;
                    }}
                }}
                """
            ).strip()

        return textwrap.dedent(
            f"""
            if [ -d /etc/nginx/sites-available ]; then
                mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
                cat > /etc/nginx/sites-available/port{port} <<'NGINX_EOF'
{server_block}
                NGINX_EOF
                ln -sf /etc/nginx/sites-available/port{port} /etc/nginx/sites-enabled/
            else
                mkdir -p /etc/nginx/conf.d
                cat > /etc/nginx/conf.d/port{port}.conf <<'NGINX_EOF'
{server_block}
                NGINX_EOF
            fi
        """
        ).strip()

    def _generate_foundrypf_service(self) -> str:
        # Use template for systemd service when available
        service_body = None
        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                service_body = self.template_engine.render_file(
                    _Path("sections/foundrypf.service.j2"), {}
                ).strip()
            except Exception:
                service_body = None

        if service_body is None:
            service_body = textwrap.dedent(
                """
                [Unit]
                Description=Foundry Port Forwarding
                After=network-online.target
                Wants=network-online.target

                [Service]
                Type=simple
                ExecStart=/usr/local/bin/foundrypf
                Restart=always
                RestartSec=10
                StandardOutput=journal
                StandardError=journal
                SyslogIdentifier=foundrypf

                [Install]
                WantedBy=multi-user.target
                """
            ).strip()

        return textwrap.dedent(
            f"""
            if command -v foundrypf >/dev/null 2>&1 || [ -x /usr/local/bin/foundrypf ]; then
              if command -v systemctl >/dev/null 2>&1; then
                cat > /etc/systemd/system/foundrypf.service <<'SYSTEMD_EOF'
{service_body}
                SYSTEMD_EOF
                systemctl daemon-reload || true
                systemctl enable foundrypf || true
                systemctl start foundrypf || true
              fi
            fi
            """
        ).strip()


__all__ = ["PortForwardingSection"]
