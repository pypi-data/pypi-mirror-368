from secret_sauce import generate_password

answers = {
    "hobby": "hiking",
    "digit": "7",
    "nickname": "Ace"
}

print("Your new password:", generate_password(answers))