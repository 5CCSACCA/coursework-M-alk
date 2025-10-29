from typing import Optional, Dict
import firebase_admin
from firebase_admin import auth


def get_bearer_token(authorization_header: Optional[str]) -> Optional[str]:
    if not authorization_header:
        return None
    parts = authorization_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def verify_id_token(id_token: str) -> Optional[Dict]:
    # returns a small user dict if valid
    try:
        decoded = auth.verify_id_token(id_token)
        return {
            "uid": decoded.get("uid"),
            "email": decoded.get("email"),
            "name": decoded.get("name"),
            "picture": decoded.get("picture"),
        }
    except Exception:
        return None


