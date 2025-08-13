import unittest
from main import AINumber, sqrt, cbrt, factorial, gamma, ln, gcd, lcm


class TestGenAIMath(unittest.TestCase):
    def setUp(self):
        self.a = AINumber("10")
        self.b = AINumber("20")

    def test_add(self):
        self.assertEqual(self.a + self.b, AINumber("30"))

    def test_subtract(self):
        self.assertEqual(self.b - self.a, AINumber("10"))

    def test_multiply(self):
        self.assertEqual(self.a * self.b, AINumber("200"))

    def test_divide(self):
        self.assertEqual(self.b / self.a, AINumber("2"))

    def test_power(self):
        self.assertEqual(self.a ** AINumber("2"), AINumber("100"))

    def test_modulo(self):
        self.assertEqual(self.b % self.a, AINumber("0"))

    def test_integer_division(self):
        self.assertEqual(self.b // self.a, AINumber("2"))

    def test_sqrt(self):
        self.assertTrue(abs(sqrt(self.a) - AINumber("3.1622776601683795")) < 0.00001)

    def test_cbrt(self):
        self.assertTrue(abs(cbrt(self.a) - AINumber("2.154434690031884")) < 0.00001)

    def test_squared(self):
        self.assertEqual(self.a.squared(), AINumber("100"))

    def test_cubed(self):
        self.assertEqual(self.a.cubed(), AINumber("1000"))

    def test_tetrate(self):
        self.assertEqual(self.a.tetrate(3), AINumber("1.0e+10000000000"))

    def test_factorial(self):
        self.assertEqual(factorial(self.a), AINumber("3628800"))

    def test_gamma(self):
        self.assertAlmostEqual(float(gamma(self.a)), 362880.0, places=1)

    def test_ln(self):
        self.assertAlmostEqual(float(ln(self.a)), 2.302585, places=5)

    def test_gcd(self):
        self.assertEqual(gcd(self.a, self.b), AINumber("10"))

    def test_lcm(self):
        self.assertEqual(lcm(self.a, self.b), AINumber("20"))

    def test_factorial_edge_cases(self):
        self.assertEqual(factorial(AINumber("0")), AINumber("1"))
        self.assertEqual(factorial(AINumber("1")), AINumber("1"))
        self.assertTrue(float(factorial(AINumber("5"))) == 120.0)
        # Negative input (should handle gracefully)
        self.assertIsInstance(factorial(AINumber("-5")), AINumber)

    def test_gamma_edge_cases(self):
        self.assertTrue(abs(float(gamma(AINumber("5"))) - 24.0) < 0.0001)
        # Negative input
        self.assertIsInstance(gamma(AINumber("-2.5")), AINumber)

    def test_ln(self):
        self.assertTrue(abs(float(ln(AINumber("1"))) - 0.0) < 0.00001)
        self.assertTrue(abs(float(ln(AINumber("2.718281828459045"))) - 1.0) < 0.00001)
        # Negative input (should handle gracefully)
        self.assertIsInstance(ln(AINumber("-1")), AINumber)

    def test_gcd_lcm(self):
        self.assertEqual(gcd(self.a, self.b), AINumber("10"))
        self.assertEqual(lcm(self.a, self.b), AINumber("20"))
        # Edge cases
        self.assertEqual(gcd(AINumber("0"), self.b), AINumber("20"))
        self.assertEqual(lcm(AINumber("0"), self.b), AINumber("0"))


if __name__ == "__main__":
    unittest.main()
