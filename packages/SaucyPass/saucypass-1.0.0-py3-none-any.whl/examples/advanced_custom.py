from secret_sauce import generate_multiple
from secret_sauce.questions import QUESTION_BANKS

# Custom question bank for foodies
QUESTION_BANKS["food"] = [
    ("Favorite spice?", "spice"),
    ("Last 2 digits of your oven temp?", "temp")
]

answers = {
    "spice": "cumin",
    "temp": "75"
}

print("Your foodie passwords:")
for pwd in generate_multiple(answers):
    print(f"🍴 {pwd}")  # Example: "Cum1n!75"