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
        self.assertEqual(sqrt(self.a), AINumber("3.1622776601683795"))

    def test_cbrt(self):
        self.assertEqual(cbrt(self.a), AINumber("2.154434690031884"))

    def test_squared(self):
        self.assertEqual(self.a.squared(), AINumber("100"))

    def test_cubed(self):
        self.assertEqual(self.a.cubed(), AINumber("1000"))

    def test_tetrate(self):
        self.assertEqual(self.a.tetrate(3), AINumber(str(10 ** (10 ** 3))))

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


if __name__ == "__main__":
    unittest.main()

