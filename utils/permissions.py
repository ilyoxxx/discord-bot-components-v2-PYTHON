"""
Vérifie si un utilisateur fait partie des "owners" définis dans .env
(OWNER_IDS). Utilisé pour protéger les commandes sensibles/admin, en
plus des permissions Discord natives.
"""

import os


def get_owner_ids() -> set[int]:
    raw = os.getenv("OWNER_IDS", "")
    ids = set()
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.add(int(part))
    return ids


def is_owner(user_id: int) -> bool:
    return user_id in get_owner_ids()
