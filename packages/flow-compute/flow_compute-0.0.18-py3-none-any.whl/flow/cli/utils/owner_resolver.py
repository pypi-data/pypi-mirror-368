"""Owner resolver and formatter (core).

Resolves current user (me) once per run; formats Owner column per spec.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional

from flow import Flow


@dataclass
class Me:
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None


class OwnerResolver:
    def __init__(self, flow: Optional[Flow] = None) -> None:
        self.flow = flow or Flow()
        self._me: Optional[Me] = None

    def get_me(self) -> Optional[Me]:
        if self._me is not None:
            return self._me
        # Use provider http to query /v2/me if available
        try:
            provider = self.flow.provider
            http = getattr(provider, "http", None)
            if http is None:
                return None
            resp = http.request(method="GET", url="/v2/me")
            data = resp.get("data", resp) if isinstance(resp, dict) else None
            if not isinstance(data, dict):
                return None
            user_id = data.get("fid") or data.get("id") or data.get("user_id")
            username = data.get("username") or data.get("user_name")
            email = data.get("email")
            if not user_id:
                return None
            self._me = Me(user_id=user_id, username=username, email=email)
            return self._me
        except Exception:
            return None

    @staticmethod
    def format_owner(created_by: Optional[str], me: Optional[Me]) -> str:
        # Prefer current user's friendly name when the creator matches the current user
        if me and created_by and created_by == me.user_id:
            # Derive a first-name style label from email (e.g., jared@ → Jared, john.doe@ → John)
            if me.email and "@" in me.email:
                local = me.email.split("@")[0]
                # Split on common separators and take the first segment
                first = re.split(r"[._-]+", local)[0]
                return first.lower() if first else "-"
            # Fallback to username if available
            if me.username:
                # Use first token of username and normalize to lowercase
                first = re.split(r"[\s._-]+", me.username)[0]
                return first.lower() if first else "-"
            # No personal info available
            return "-"
        # Compact FID for other users
        if created_by:
            return created_by.replace("user_", "")[:8]
        # Unknown owner
        return "-"
