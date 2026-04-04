from datetime import datetime
import random
import bcrypt


def generate_ticket_id():
    """Generate unique ticket ID like CMS-20260331-4782"""
    date_str = datetime.now().strftime("%Y%m%d")
    serial = random.randint(1000, 9999)
    return f"CMS-{date_str}-{serial}"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
