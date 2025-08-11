from __future__ import annotations

import textwrap

from flow.providers.mithril.runtime.startup.sections.base import ScriptContext, ScriptSection
from flow.providers.mithril.runtime.startup.utils import ensure_command_available


class S3Section(ScriptSection):
    @property
    def name(self) -> str:
        return "s3_mounts"

    @property
    def priority(self) -> int:
        return 35

    def should_include(self, context: ScriptContext) -> bool:
        return any(
            k.startswith("S3_MOUNT_") and k.endswith("_BUCKET") for k in context.environment.keys()
        )

    def generate(self, context: ScriptContext) -> str:
        mount_count = int(context.environment.get("S3_MOUNTS_COUNT", "0"))
        if mount_count == 0:
            return ""

        mount_snippets: list[str] = []
        for i in range(mount_count):
            mount_key = f"S3_MOUNT_{i}"
            bucket = context.environment.get(f"{mount_key}_BUCKET")
            path = context.environment.get(f"{mount_key}_PATH", "")
            target = context.environment.get(f"{mount_key}_TARGET")
            if bucket and target:
                s3_path = f"{bucket}:/{path}" if path else bucket
                if getattr(self, "template_engine", None):
                    try:
                        from pathlib import Path as _Path

                        mount_snippets.append(
                            self.template_engine.render_file(
                                _Path("sections/s3_mount_item.sh.j2"),
                                {
                                    "bucket": bucket,
                                    "path": path,
                                    "target": target,
                                    "index": i,
                                    "s3_path": s3_path,
                                },
                            ).strip()
                        )
                        continue
                    except Exception:
                        pass
                mount_snippets.append(self._generate_s3_mount(bucket, path, target, i))

        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                return self.template_engine.render_file(
                    _Path("sections/s3_mount.sh.j2"),
                    {
                        "ensure_s3fs_cmd": ensure_command_available("s3fs"),
                        "mount_commands": "\n".join(mount_snippets),
                    },
                ).strip()
            except Exception:
                pass

        mount_blob = "\n".join(mount_snippets)
        return textwrap.dedent(
            f"""
            # S3 mounting via s3fs
            echo "Setting up S3 mounts"
            {ensure_command_available("s3fs")}
            echo 'user_allow_other' >> /etc/fuse.conf || true
            {mount_blob}
            echo "S3 mounts configured:"
            mount | grep s3fs
            rm -f /tmp/s3fs_passwd || true
        """
        ).strip()

    def _generate_s3_mount(self, bucket: str, path: str, target: str, index: int) -> str:
        s3_path = f"{bucket}:/{path}" if path else bucket
        return textwrap.dedent(
            f"""
            mkdir -p {target}
            S3FS_AUTH_OPTS=""
            if [ "${{USE_IAM_ROLE}}" = "true" ]; then
                S3FS_AUTH_OPTS="-o iam_role=auto"
            else
                S3FS_AUTH_OPTS="-o passwd_file=/tmp/s3fs_passwd"
            fi
            RW_OPT="-o ro"
            if [ "${{S3_MOUNTS_RW_ALL:-}}" = "1" ] || [ "${{S3_MOUNT_%d_RW:-}}" = "1" ]; then
                RW_OPT=""  # allow writes
            fi
            s3fs {s3_path} {target} \
                ${{S3FS_AUTH_OPTS}} \
                ${{RW_OPT}} \
                -o allow_other \
                -o use_cache=/tmp/s3fs_cache \
                -o retries=5 \
                -o connect_timeout=10 \
                -o readwrite_timeout=30
            if mountpoint -q {target}; then echo "OK: {target}"; else echo "ERROR: {target}" >&2; exit 1; fi
        """
        ).strip() % (index)


__all__ = ["S3Section"]
