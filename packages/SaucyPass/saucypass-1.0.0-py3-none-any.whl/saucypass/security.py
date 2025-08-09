import hashlib
import os
import secrets

def salt_answers(answers: dict) -> str:
    """Cryptographically mix user answers with random salt"""
    salt = secrets.token_hex(8)
    combined = salt + "|".join(f"{k}:{v}" for k,v in answers.items())
    return hashlib.sha256(combined.encode()).hexdigest()

def ensure_pronounceable(base: str) -> str:
    """Make sure the password has vowel/consonant patterns"""
    vowels = "aeiouy"
    consonants = "bcdfghjklmnpqrstvwxz"
    result = []
    for i, c in enumerate(base[:8]):  # First 8 chars form the base
        if i % 2 == 0:
            result.append(secrets.choice(consonants))
        else:
            result.append(secrets.choice(vowels))
    return "".join(result)