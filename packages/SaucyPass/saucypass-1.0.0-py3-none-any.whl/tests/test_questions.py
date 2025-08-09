import unittest
from secret_sauce.questions import get_questions

class TestQuestions(unittest.TestCase):
    def test_social_questions(self):
        questions = get_questions("social")
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0][1], "hobby")  # Check first question's key

    def test_invalid_category(self):
        self.assertEqual(len(get_questions("invalid")), 3)  # Falls back to general

if __name__ == "__main__":
    unittest.main()