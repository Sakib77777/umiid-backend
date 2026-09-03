import hashlib
import secrets


def generate_otp() -> str:
    """Generates a random 4-digit numeric OTP as a string, e.g. '0482'."""
    return f"{secrets.randbelow(10_000):04d}"


def hash_otp(otp: str) -> str:
    """One-way hash of the OTP so the raw value is never stored in Firestore."""
    return hashlib.sha256(otp.encode()).hexdigest()


def verify_otp_hash(otp: str, hashed: str) -> bool:
    """Constant-time comparison to avoid timing attacks."""
    return secrets.compare_digest(hash_otp(otp), hashed)