COMMON_PASSWORDS = {
    "123456", "123456789", "12345678", "1234567", "password",
    "qwerty", "abc123", "111111", "123123", "password1",
    "1234567890", "iloveyou", "000000", "qwerty123", "1q2w3e4r",
    "letmein", "monkey", "dragon", "football", "welcome",
    "admin123", "changeme", "passw0rd", "sunshine", "princess",
    "qwertyuiop", "123321", "654321", "666666", "7777777",
    "master", "shadow", "superman", "michael", "trustno1",
    "hunter2", "batman", "starwars", "freedom", "whatever",
}


def is_common_password(password: str) -> bool:
    return password.lower() in COMMON_PASSWORDS