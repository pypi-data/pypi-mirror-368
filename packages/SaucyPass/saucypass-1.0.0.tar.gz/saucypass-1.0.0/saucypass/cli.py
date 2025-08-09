from .questions import get_questions
from .generator import generate_multiple

def interactive_mode():
    """Command-line interactive experience"""
    print("🧂 Welcome to Secret Sauce! Let's cook up some passwords...")
    
    # Get password purpose
    purpose = input("\nWhat's this password for? (social/banking/general): ").strip()
    questions = get_questions(purpose)
    
    # Collect answers
    answers = {}
    for question, key, validator in questions:
        while True:
            answer = input(f"\n{question}: ").strip()
            try:
                if validator(answer):
                    answers[key] = answer
                    break
                print("⚠️ Invalid input, try again")
            except:
                print("⚠️ Invalid input, try again")
    
    # Generate passwords
    passwords = generate_multiple(answers)
    
    # Display results
    print("\n🔐 Here are your freshly cooked passwords:")
    for i, pwd in enumerate(passwords, 1):
        print(f"{i}. {pwd}")
    
    print("\n💡 Pro tip: The first one is extra saucy!")