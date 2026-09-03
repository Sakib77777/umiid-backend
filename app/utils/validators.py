import re
import string

from app.utils.common_passwords import is_common_password

SPECIAL_CHARACTERS = set(string.punctuation)  # !@#$%^&*()_+-=... etc.

SEQUENTIAL_RUNS = [
    "0123456789", "1234567890", "9876543210",
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
]


def _contains_sequential_run(password: str, min_run: int = 4) -> bool:
    lower = password.lower()
    for run in SEQUENTIAL_RUNS:
        for i in range(len(run) - min_run + 1):
            if run[i : i + min_run] in lower:
                return True
    return False


def _contains_personal_info(password: str, name: str, email: str, phone: str) -> bool:
    lower = password.lower()

    for part in re.split(r"\s+", name.lower()):
        if len(part) >= 3 and part in lower:
            return True

    email_prefix = email.split("@")[0].lower()
    if len(email_prefix) >= 3 and email_prefix in lower:
        return True

    if phone and phone in password:
        return True

    return False

def _has_required_character_types(password: str) -> tuple[bool, bool]:
    """Returns (has_digit, has_special_char)."""
    has_digit = any(ch.isdigit() for ch in password)
    has_special = any(ch in SPECIAL_CHARACTERS for ch in password)
    return has_digit, has_special


def validate_password_strength(
    password: str, name: str = "", email: str = "", phone: str = ""
) -> None:
    """Raises ValueError with a user-facing message if the password is weak."""
    if is_common_password(password):
        raise ValueError("This password is too common. Please choose a stronger one.")

    has_digit, has_special = _has_required_character_types(password)
    if not has_digit and not has_special:
        raise ValueError(
            "Password must contain at least one number and one special character "
            "(e.g. ! @ # $ %)."
        )
    if not has_digit:
        raise ValueError("Password must contain at least one number.")
    if not has_special:
        raise ValueError(
            "Password must contain at least one special character (e.g. ! @ # $ %)."
        )

    if _contains_sequential_run(password):
        raise ValueError(
            "Password contains a predictable sequence (e.g. '1234' or 'qwerty'). "
            "Please choose something less guessable."
        )

    if (name or email or phone) and _contains_personal_info(password, name, email, phone):
        raise ValueError(
            "Password shouldn't contain your name, email, or phone number. "
            "Please choose something less personal."
        )