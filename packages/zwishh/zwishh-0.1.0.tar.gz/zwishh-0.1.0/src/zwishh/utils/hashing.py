import hashlib
import json

def compute_cart_hash(cart: dict) -> str:
    """Compute a deterministic hash of the cart contents."""
    raw = json.dumps(cart, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()
