"""SSH key resolution and generation service."""

from __future__ import annotations


class SSHKeyService:
    def __init__(self, ssh_key_manager) -> None:
        self._mgr = ssh_key_manager

    def resolve_keys(self, requested: list[str] | None) -> list[str] | None:
        if not requested:
            return None
        # Special sentinel to auto-generate
        if requested == ["_auto_"]:
            existing = self._mgr.list_keys()
            # Always include any project-required keys
            required_ids = [k.fid for k in existing if getattr(k, "required", False)]
            # Prefer per-instance generation per docs; append required keys
            new_id = self._mgr.auto_generate_key()
            if new_id:
                merged = required_ids + [new_id]
                # Deduplicate and return
                seen: set[str] = set()
                result: list[str] = []
                for k in merged:
                    if k and k not in seen:
                        seen.add(k)
                        result.append(k)
                return result
            # Fallback: if generation fails, include required + any existing keys
            if existing:
                fallback = required_ids + [k.fid for k in existing]
                seen2: set[str] = set()
                uniq: list[str] = []
                for k in fallback:
                    if k and k not in seen2:
                        seen2.add(k)
                        uniq.append(k)
                return uniq
            return []
        filtered = [k for k in requested if k != "_auto_"]
        if not filtered:
            return None
        ensured = self._mgr.ensure_platform_keys(filtered)
        return ensured or None

    def merge_with_required(self, ssh_key_ids: list[str] | None) -> list[str]:
        """Ensure project-required SSH keys are always included in launch.

        Args:
            ssh_key_ids: Current list of SSH key IDs selected for launch

        Returns:
            Merged list including any project-required key IDs (deduplicated)
        """
        current = list(ssh_key_ids or [])
        platform_keys = self._mgr.list_keys()
        required_ids = [k.fid for k in platform_keys if getattr(k, "required", False)]
        if not required_ids:
            return current
        # Prepend required to make visibility obvious in any logs
        merged = required_ids + current
        # Deduplicate while preserving order
        seen: set[str] = set()
        result: list[str] = []
        for k in merged:
            if k not in seen:
                seen.add(k)
                result.append(k)
        return result
