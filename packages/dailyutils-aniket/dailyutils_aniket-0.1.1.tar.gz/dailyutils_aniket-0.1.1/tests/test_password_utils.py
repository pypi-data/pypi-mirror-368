import unittest
from dailyutils.password_utils import generate_password, check_strength

class TestPasswordUtils(unittest.TestCase):

    def test_generate_password_default(self):
        pwd = generate_password()
        self.assertEqual(len(pwd), 12)
        self.assertTrue(any(c.isdigit() for c in pwd))
        self.assertTrue(any(not c.isalnum() for c in pwd))  

    def test_generate_password_custom_length(self):
        pwd = generate_password(length=20)
        self.assertEqual(len(pwd), 20)

    def test_generate_password_no_symbols(self):
        pwd = generate_password(use_symbols=False)
        self.assertTrue(all(c.isalnum() for c in pwd))

    def test_generate_password_short_length_error(self):
        with self.assertRaises(ValueError):
            generate_password(length=2)

    def test_check_strength_weak(self):
        self.assertEqual(check_strength("abc"), "Weak")

    def test_check_strength_moderate(self):
        self.assertEqual(check_strength("Abc12345"), "Moderate")

    def test_check_strength_strong(self):
        self.assertEqual(check_strength("Abc123!@#xyz"), "Strong")

if __name__ == '__main__':
    unittest.main()
