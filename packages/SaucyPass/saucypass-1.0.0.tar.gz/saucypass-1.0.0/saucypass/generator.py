from .security import salt_answers, ensure_pronounceable
import random
import string

def generate_password(answers: dict, length=12) -> str:
    """Generate one pronounceable password"""
    # Create cryptographic base
    hashed = salt_answers(answers)
    pronounceable = ensure_pronounceable(hashed)
    
    # Add special characters and capitalization
    special = random.choice('!@#$%^&*')
    number = str(random.randint(0, 9))
    
    # Combine elements
    parts = [
        pronounceable[:4].capitalize(),
        number,
        special,
        pronounceable[4:8].lower()
    ]
    
    password = "".join(parts)[:length]
    return password

def generate_multiple(answers: dict, count=5) -> list:
    """Generate multiple password variants"""
    return [generate_password(answers, length=12 + i) for i in range(count)]