import unittest
from secret_sauce.generator import generate_password

class TestGenerator(unittest.TestCase):
    def test_password_length(self):
        pwd = generate_password({"test": "value"}, length=10)
        self.assertEqual(len(pwd), 10)
    
    def test_password_content(self):
        pwd = generate_password({"test": "value"})
        self.assertTrue(any(c.isupper() for c in pwd))
        self.assertTrue(any(c.isdigit() for c in pwd))
        self.assertTrue(any(c in '!@#$%^&*' for c in pwd))

if __name__ == "__main__":
    unittest.main()