import unittest
from secret_sauce.security import salt_answers, ensure_pronounceable

class TestSecurity(unittest.TestCase):
    def test_salting(self):
        result1 = salt_answers({"test": "value"})
        result2 = salt_answers({"test": "value"})  # Same input
        self.assertNotEqual(result1, result2)  # Different due to random salt

    def test_pronounceable(self):
        base = "a1b2c3d4"
        result = ensure_pronounceable(base)
        self.assertTrue(any(v in result for v in "aeiouy"))  # Has vowels

if __name__ == "__main__":
    unittest.main()