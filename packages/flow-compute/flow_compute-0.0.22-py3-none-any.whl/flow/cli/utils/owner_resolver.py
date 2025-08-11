"""Owner resolver and formatter (core).

Resolves current user (me) once per run; formats Owner column per spec.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from flow import Flow


@dataclass
class Me:
    user_id: str
    username: str | None = None
    email: str | None = None


class OwnerResolver:
    def __init__(self, flow: Flow | None = None) -> None:
        self.flow = flow or Flow()
        self._me: Me | None = None

    def get_me(self) -> Me | None:
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
    def format_owner(created_by: str | None, me: Me | None) -> str:
        # Prefer current user's friendly name when the creator matches the current user
        if me and created_by:
            try:
                # Normalize inputs (case-insensitive, strip common prefixes)
                created_by_str = str(created_by)
                me_user_id = str(me.user_id or "")
                me_username = str(me.username or "")
                me_email = str(me.email or "")

                # Direct equality first (exact provider IDs)
                if created_by_str == me_user_id:
                    pass  # treat as same user
                else:
                    # Normalize common ID formats to handle provider differences
                    # Examples:
                    #   created_by: "ClUS4619" vs me.user_id: "user_ClUS4619AbCdEf"
                    #   created_by: "user_kfV4CCaapLiqCNlv" vs me.user_id: "user_kfV4CCaapLiqCNlv"
                    created_token = re.sub(r"^user_", "", created_by_str)
                    me_token = re.sub(r"^user_", "", me_user_id)
                    # Lowercase and strip non-alphanumerics to tolerate formatting
                    created_token_l = re.sub(r"[^a-z0-9]", "", created_token.lower())
                    me_token_l = re.sub(r"[^a-z0-9]", "", me_token.lower())
                    # Consider a match if one token starts with the other (handles short IDs)
                    is_same_user = False
                    if created_token_l and me_token_l:
                        if (
                            created_token_l == me_token_l
                            or me_token_l.startswith(created_token_l)
                            or created_token_l.startswith(me_token_l)
                        ):
                            is_same_user = True
                        else:
                            # Also compare first 8 chars which are commonly displayed
                            is_same_user = created_token_l[:8] == me_token_l[:8]
                    # Also consider username-based identity commonly shown in external systems
                    if not is_same_user and me_username:
                        ct = created_by_str.lower()
                        un = me_username.lower()
                        if ct == un or ct.startswith(un) or un.startswith(ct):
                            is_same_user = True
                    # And finally compare against email local part (before @)
                    if not is_same_user and me_email and "@" in me_email:
                        local = me_email.split("@")[0].lower()
                        ct = created_by_str.lower()
                        if ct == local or ct.startswith(local) or local.startswith(ct):
                            is_same_user = True
                    if not is_same_user:
                        raise ValueError("not same user")
                # Derive a first-name style label from email (e.g., jared@ → jared, john.doe@ → john)
                if me_email and "@" in me_email:
                    local = me_email.split("@")[0]
                    # Split on common separators and take the first segment
                    first = re.split(r"[._-]+", local)[0]
                    return first.lower() if first else "-"
                # Fallback to username if available
                if me_username:
                    # Use first token of username and normalize to lowercase
                    first = re.split(r"[\s._-]+", me_username)[0]
                    return first.lower() if first else "-"
                # No personal info available
                return "-"
            except Exception:
                # Fall through to compact FID formatting below
                pass
        # Compact FID for other users
        if created_by:
            return created_by.replace("user_", "")[:8]
        # Unknown owner
        return "-"
