# app/utils/ids.py
import secrets


def generate_booking_id() -> str:
    """
    Generates a simple public booking id like: LUX123456
    """
    return f"LUX{secrets.randbelow(1_000_000):06d}"
