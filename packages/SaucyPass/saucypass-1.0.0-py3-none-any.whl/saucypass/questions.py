QUESTION_BANKS = {
    "social": [
        ("What's a hobby you've posted about?", "hobby", str),
        ("Last digit of your first phone number?", "digit", lambda x: x.isdigit() and len(x) == 1),
    ],
    "banking": [
        ("Historical figure you admire (first name)?", "figure", str),
        ("Your lucky number between 10-99?", "number", lambda x: x.isdigit() and 10 <= int(x) <= 99),
    ],
    "general": [
        ("Childhood friend's nickname?", "nickname", str),
        ("Year you want to time travel to?", "year", lambda x: x.isdigit() and len(x) == 4),
        ("Favorite punctuation mark?", "symbol", lambda x: x in '!@#$%^&*'),
    ]
}

def get_questions(category="general"):
    """Get question set for a specific password category"""
    return QUESTION_BANKS.get(category.lower(), QUESTION_BANKS["general"])