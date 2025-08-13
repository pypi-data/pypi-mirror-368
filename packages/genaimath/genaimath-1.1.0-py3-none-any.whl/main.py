"""
Main entry point for GenAIMath.
"""


# Importing necessary libraries


import os
import copy
import google.generativeai as genai
import mpmath
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from mpmath import *

mp.pretty = True

# Creating static variables to be used throughout the application.

MPF_SAFE_LIMIT_HIGH: mpf = mpf("10") ** mpf("1e1000")
MPF_SAFE_LIMIT_LOW: mpf = mpf("1") / (mpf("10") ** mpf("1e1000"))


# Creating static functions to be used throughout the application.


def is_safe_number(obj: object) -> bool:
    """
    Check if the number is either zero or within the safe limits defined by MPF_SAFE_LIMIT_HIGH and MPF_SAFE_LIMIT_LOW.
    """
    try:
        num = mpf(str(obj))
        return MPF_SAFE_LIMIT_LOW < mpmath.fabs(num) < MPF_SAFE_LIMIT_HIGH or num == 0
    except ValueError:
        return False


def tetration_recursive(base, height):
    # type: (AINumber, int) -> AINumber
    """
    Recursive implementation of tetration (repeated exponentiation).
    """
    if height == 0:
        return 1  # Standard definition for height 0
    elif height == 1:
        return base
    else:
        return base ** tetration_recursive(base, height - 1)


def ai_calculate(prompt: str, model: str = "gemini-2.5-flash", is_local: bool = False) -> str:
    """
    Use AI to calculate the result of a mathematical expression.
    """
    if is_local:
        llm = OllamaLLM(model=model)
        return llm.invoke(prompt)
    else:
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        llm = genai.GenerativeModel(model_name=model)
        convo = llm.start_chat(history=[])
        convo.send_message(prompt)
        return str(convo.last.text)


class AINumber:
    """
    A class to represent a number with AI capabilities.
    """

    def __init__(self, value, symbolic=None):
        """
        Accept any type and convert to mpf for unlimited precision.
        If symbolic is provided, store it for readable output.
        """
        self.symbolic = symbolic
        try:
            self.value = mpf(value)
        except Exception:
            self.value = value

    def readable(self, max_digits=10):
        """
        Return a human-readable string for any magnitude, using scientific notation for very large/small numbers.
        If symbolic representation exists, use it.
        """
        if self.symbolic:
            return self.symbolic
        try:
            return nstr(self.value, max_digits)
        except Exception:
            return str(self.value)

    def __str__(self):
        """
        Return a human-readable string for any magnitude, using scientific notation for very large/small numbers.
        """
        return self.readable()

    def __add__(self, other):
        # type: (object) -> AINumber
        """
        Implements addition for AINumber objects.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return AINumber(ai_calculate(f"{self.value} + {other_value}"))
        else:
            result: mpf = mpf(self.value) + mpf(other_value)
            if is_safe_number(result):
                return AINumber(str(result))
            else:
                return AINumber(ai_calculate(f"{self.value} + {other_value}"))

    def __sub__(self, other):
        # type: (object) -> AINumber
        """
        Implements subtraction for AINumber objects.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return AINumber(ai_calculate(f"{self.value} - {other_value}"))
        else:
            result: mpf = mpf(self.value) - mpf(other_value)
            if is_safe_number(result):
                return AINumber(str(result))
            else:
                return AINumber(ai_calculate(f"{self.value} - {other_value}"))

    def __mul__(self, other):
        # type: (object) -> AINumber
        """
        Implements multiplication for AINumber objects.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return AINumber(ai_calculate(f"{self.value} * {other_value}"))
        else:
            result: mpf = mpf(self.value) * mpf(other_value)
            if is_safe_number(result):
                return AINumber(str(result))
            else:
                return AINumber(ai_calculate(f"{self.value} * {other_value}"))

    def __pow__(self, other):
        # type: (object) -> AINumber
        """
        Implements exponentiation for AINumber objects.
        """
        if isinstance(other, AINumber):
            other_val = other.value
            other_readable = other.readable()
        else:
            other_val = mpf(other)
            other_readable = str(other)
        symbolic = f"({self.readable()})^({other_readable})"
        try:
            if not is_safe_number(self.value) or not is_safe_number(other_val):
                return AINumber(None, symbolic=symbolic)
            result = self.value ** other_val
            if is_safe_number(result):
                return AINumber(result)
            else:
                return AINumber(None, symbolic=symbolic)
        except Exception:
            return AINumber(None, symbolic=symbolic)

    def __mod__(self, other):
        # type: (object) -> AINumber
        """
        Implements the modulo operation for AINumber objects.
        If either operand is not a safe number, uses ai_calculate for the result.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return AINumber(ai_calculate(f"{self.value} % {other_value}"))
        else:
            result: mpf = mpf(self.value) % mpf(other_value)
            if is_safe_number(result):
                return AINumber(str(result))
            else:
                return AINumber(ai_calculate(f"{self.value} % {other_value}"))

    def __truediv__(self, other):
        # type: (object) -> AINumber
        """
        Implements true division for AINumber objects.
        If either operand is not a safe number, uses ai_calculate for the result.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return AINumber(ai_calculate(f"{self.value} / {other_value}"))
        else:
            result: mpf = mpf(self.value) / mpf(other_value)
            if is_safe_number(result):
                return AINumber(str(result))
            else:
                return AINumber(ai_calculate(f"{self.value} / {other_value}"))

    def __floordiv__(self, other):
        # type: (object) -> AINumber
        """
        Implements floor division for AINumber objects.
        If either operand is not a safe number, uses ai_calculate for the result.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return AINumber(ai_calculate(f"{self.value} // {other_value}"))
        else:
            result: mpf = mpmath.floor(mpf(self.value) / mpf(other_value))
            if is_safe_number(result):
                return AINumber(str(result))
            else:
                return AINumber(ai_calculate(f"{self.value} // {other_value}"))

    def __int__(self):
        # type: () -> int
        """
        Convert the AINumber object to an integer.
        Uses AI fallback if the value is not safe for direct conversion.
        """
        if is_safe_number(self.value):
            return int(mpf(self.value))
        else:
            return int(ai_calculate(f"Please convert {self.value} to an integer!"))

    def __float__(self):
        # type: () -> float
        """
        Convert the AINumber object to a float.
        Raises exceptions for underflow/overflow and uses AI fallback for unsafe values.
        """
        if is_safe_number(self.value):
            if self.value != 0 and mpmath.fabs(self.value) < mpf("2.2250738585072014e-308"):
                raise Exception("Underflow! The AINumber object is too small to be converted to a float!")
            elif mpmath.fabs(self.value) > mpf("1.7976931348623157e+308"):
                raise Exception("Overflow! The AINumber object is too large to be converted to a float!")
            else:
                return float(mpf(self.value))
        else:
            return float(ai_calculate(f"Please convert {self.value} to a float!"))

    def squared(self):
        # type: () -> AINumber
        """
        Returns the square of the AINumber object.
        Uses AI fallback if the value is not safe for direct calculation.
        """
        if is_safe_number(self.value):
            return self.__pow__(2)
        else:
            return AINumber(ai_calculate(f"{self.value} squared"))

    def cubed(self):
        # type: () -> AINumber
        """
        Returns the cube of the AINumber object.
        Uses AI fallback if the value is not safe for direct calculation.
        """
        if is_safe_number(self.value):
            return self.__pow__(3)
        else:
            return AINumber(ai_calculate(f"{self.value} cubed"))

    def tetrate(self, number):
        # type: (int) -> AINumber
        """
        Returns the result of tetration (repeated exponentiation) of the AINumber object to the given height.
        Uses AI fallback if the value is not safe for direct calculation.
        """
        symbolic = f"({self.readable()})↑↑({number})"
        if not is_safe_number(self.value):
            return AINumber(None, symbolic=symbolic)
        else:
            result: mpf = tetration_recursive(mpf(self.value), number)
            if is_safe_number(result):
                return AINumber(str(result))
            else:
                return AINumber(None, symbolic=symbolic)

    def __pos__(self):
        # type: () -> AINumber
        """
        Returns the positive value of the AINumber object as a new AINumber.
        """
        if is_safe_number(self.value):
            return self
        else:
            return AINumber(ai_calculate(f"Please return the positive value of {self.value}"))

    def __neg__(self):
        # type: () -> AINumber
        """
        Returns the negative value of the AINumber object as a new AINumber.
        """
        if is_safe_number(self.value):
            return AINumber(str(-mpf(self.value)))
        else:
            return AINumber(ai_calculate(f"Please return the negative value of {self.value}"))

    def __abs__(self):
        # type: () -> AINumber
        """
        Returns the absolute value of the AINumber object as a new AINumber.
        """
        if is_safe_number(self.value):
            return AINumber(str(mpmath.fabs(self.value)))
        else:
            return AINumber(ai_calculate(f"Please return the absolute value of {self.value}"))

    def __floor__(self):
        # type: () -> AINumber
        """
        Returns the floor value of the AINumber object as a new AINumber.
        Uses AI fallback if the value is not safe for direct calculation.
        """
        if is_safe_number(self.value):
            return AINumber(str(floor(mpf(self.value))))
        else:
            return AINumber(ai_calculate(f"Please return the floor value of {self.value}"))

    def __ceil__(self):
        # type: () -> AINumber
        """
        Returns the ceiling value of the AINumber object as a new AINumber.
        Uses AI fallback if the value is not safe for direct calculation.
        """
        if is_safe_number(self.value):
            return AINumber(str(ceil(mpf(self.value))))
        else:
            return AINumber(ai_calculate(f"Please return the ceiling value of {self.value}"))

    def __and__(self, other):
        # type: (object) -> AINumber
        """
        Implements bitwise AND operation for AINumber objects.
        Uses AI fallback if either operand is not a safe number.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return AINumber(ai_calculate(f"{self.value} & {other_value}"))
        else:
            result: mpf = mpf(self.value) & mpf(other_value)
            if is_safe_number(result):
                return AINumber(str(result))
            else:
                return AINumber(ai_calculate(f"{self.value} & {other_value}"))

    def __or__(self, other):
        # type: (object) -> AINumber
        """
        Implements bitwise OR operation for AINumber objects.
        Uses AI fallback if either operand is not a safe number.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return AINumber(ai_calculate(f"{self.value} | {other_value}"))
        else:
            result: mpf = mpf(self.value) | mpf(other_value)
            if is_safe_number(result):
                return AINumber(str(result))
            else:
                return AINumber(ai_calculate(f"{self.value} | {other_value}"))

    def __xor__(self, other):
        # type: (object) -> AINumber
        """
        Implements bitwise XOR operation for AINumber objects.
        Uses AI fallback if either operand is not a safe number.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return AINumber(ai_calculate(f"{self.value} ^ {other_value}"))
        else:
            result: mpf = mpf(self.value) ^ mpf(other_value)
            if is_safe_number(result):
                return AINumber(str(result))
            else:
                return AINumber(ai_calculate(f"{self.value} ^ {other_value}"))

    def __gt__(self, other):
        # type: (object) -> bool
        """
        Implements greater-than comparison for AINumber objects.
        Uses AI fallback if either operand is not a safe number.
        Returns True if self is greater than other, otherwise False.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return ai_calculate(f"Is {self.value} greater than {other_value}?") == "Yes"
        else:
            return mpf(self.value) > mpf(other_value)

    def __ge__(self, other):
        # type: (object) -> bool
        """
        Implements greater-than-or-equal comparison for AINumber objects.
        Uses AI fallback if either operand is not a safe number.
        Returns True if self is greater than or equal to other, otherwise False.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return ai_calculate(f"Is {self.value} greater than or equal to {other_value}?") == "Yes"
        else:
            return mpf(self.value) >= mpf(other_value)

    def __lt__(self, other):
        # type: (object) -> bool
        """
        Implements less-than comparison for AINumber objects.
        Uses AI fallback if either operand is not a safe number.
        Returns True if self is less than other, otherwise False.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return ai_calculate(f"Is {self.value} less than {other_value}?") == "Yes"
        else:
            return mpf(self.value) < mpf(other_value)

    def __le__(self, other):
        # type: (object) -> bool
        """
        Implements less-than-or-equal comparison for AINumber objects.
        Uses AI fallback if either operand is not a safe number.
        Returns True if self is less than or equal to other, otherwise False.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return ai_calculate(f"Is {self.value} less than or equal to {other_value}?") == "Yes"
        else:
            return mpf(self.value) <= mpf(other_value)

    def __eq__(self, other):
        # type: (object) -> bool
        """
        Implements equality comparison for AINumber objects.
        Uses AI fallback if either operand is not a safe number.
        Returns True if values are equal, otherwise False.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return ai_calculate(f"Is {self.value} equal to {other_value}?") == "Yes"
        else:
            return mpf(self.value) == mpf(other_value)

    def __ne__(self, other):
        # type: (object) -> bool
        """
        Implements inequality comparison for AINumber objects.
        Uses AI fallback if either operand is not a safe number.
        Returns True if values are not equal, otherwise False.
        """
        other_value: str = other.value if isinstance(other, AINumber) else str(other)
        if not is_safe_number(self.value) or not is_safe_number(other_value):
            return ai_calculate(f"Is {self.value} not equal to {other_value}?") == "Yes"
        else:
            return mpf(self.value) != mpf(other_value)

    def clone(self):
        # type: () -> AINumber
        """
        Create a deep copy of the AINumber object.
        Returns a new instance with the same value and symbolic representation.
        """
        return copy.deepcopy(self)


# Creating additional functions for AINumber class


def sqrt(ai_number: AINumber) -> AINumber:
    """
    Compute the square root of a number with error handling and input validation.
    """
    try:
        value = mpf(ai_number.value)
        if value < 0:
            return AINumber("nan")
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the square root of {ai_number.value}"))
        result: mpf = mpmath.sqrt(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the square root of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def cbrt(ai_number: AINumber) -> AINumber:
    """
    Compute the cube root of a number with error handling and input validation.
    """
    try:
        value = mpf(ai_number.value)
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the cube root of {ai_number.value}"))
        result: mpf = mpmath.root(value, 3)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the cube root of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def sin(ai_number: AINumber) -> AINumber:
    """
    Compute the sine of a number with error handling and input validation.
    """
    try:
        value = mpf(ai_number.value)
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the sine of {ai_number.value}"))
        result: mpf = mpmath.sin(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the sine of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def cos(ai_number: AINumber) -> AINumber:
    """
    Compute the cosine of a number with error handling and input validation.
    """
    try:
        value = mpf(ai_number.value)
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the cosine of {ai_number.value}"))
        result: mpf = mpmath.cos(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the cosine of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def tan(ai_number: AINumber) -> AINumber:
    """
    Compute the tangent of a number with error handling and input validation.
    """
    try:
        value = mpf(ai_number.value)
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the tangent of {ai_number.value}"))
        result: mpf = mpmath.tan(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the tangent of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def cosec(ai_number: AINumber) -> AINumber:
    """
    Compute the cosecant of a number with error handling and input validation.
    Returns 'nan' for zero input and uses AI fallback for unsafe values.
    """
    try:
        value = mpf(ai_number.value)
        if value == 0:
            return AINumber("nan")
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the cosecant of {ai_number.value}"))
        result: mpf = mpf("1") / mpmath.sin(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the cosecant of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def sec(ai_number: AINumber) -> AINumber:
    """
    Compute the secant of a number with error handling and input validation.
    Returns 'nan' for zero input and uses AI fallback for unsafe values.
    """
    try:
        value = mpf(ai_number.value)
        if value == 0:
            return AINumber("nan")
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the secant of {ai_number.value}"))
        result: mpf = mpf("1") / mpmath.cos(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the secant of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def cot(ai_number: AINumber) -> AINumber:
    """
    Compute the cotangent of a number with error handling and input validation.
    Returns 'nan' for zero input and uses AI fallback for unsafe values.
    """
    try:
        value = mpf(ai_number.value)
        if value == 0:
            return AINumber("nan")
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the cotangent of {ai_number.value}"))
        result: mpf = mpf("1") / mpmath.tan(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the cotangent of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def sinh(ai_number: AINumber) -> AINumber:
    """
    Compute the hyperbolic sine of a number with error handling and input validation.
    """
    try:
        value = mpf(ai_number.value)
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the hyperbolic sine of {ai_number.value}"))
        result: mpf = mpmath.sinh(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the hyperbolic sine of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def cosh(ai_number: AINumber) -> AINumber:
    """
    Compute the hyperbolic cosine of a number with error handling and input validation.
    """
    try:
        value = mpf(ai_number.value)
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the hyperbolic cosine of {ai_number.value}"))
        result: mpf = mpmath.cosh(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the hyperbolic cosine of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def tanh(ai_number: AINumber) -> AINumber:
    """
    Compute the hyperbolic tangent of a number with error handling and input validation.
    """
    try:
        value = mpf(ai_number.value)
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the hyperbolic tangent of {ai_number.value}"))
        result: mpf = mpmath.tanh(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the hyperbolic tangent of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def cosech(ai_number: AINumber) -> AINumber:
    """
    Compute the hyperbolic cosecant of a number with error handling and input validation.
    Returns 'nan' for zero input and uses AI fallback for unsafe values.
    """
    try:
        value = mpf(ai_number.value)
        if value == 0:
            return AINumber("nan")
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the hyperbolic cosecant of {ai_number.value}"))
        result: mpf = mpf("1") / mpmath.sinh(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the hyperbolic cosecant of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def sech(ai_number: AINumber) -> AINumber:
    """
    Compute the hyperbolic secant of a number with error handling and input validation.
    Returns 'nan' for zero input and uses AI fallback for unsafe values.
    """
    try:
        value = mpf(ai_number.value)
        if value == 0:
            return AINumber("nan")
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the hyperbolic secant of {ai_number.value}"))
        result: mpf = mpf("1") / mpmath.cosh(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the hyperbolic secant of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def coth(ai_number: AINumber) -> AINumber:
    """
    Compute the hyperbolic cotangent of a number with error handling and input validation.
    Returns 'nan' for zero input and uses AI fallback for unsafe values.
    """
    try:
        value = mpf(ai_number.value)
        if value == 0:
            return AINumber("nan")
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the hyperbolic cotangent of {ai_number.value}"))
        result: mpf = mpf("1") / mpmath.tanh(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the hyperbolic cotangent of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def factorial(ai_number: AINumber) -> AINumber:
    """
    Compute the factorial of a number using mpmath for high precision.
    Handles edge cases and unsafe numbers gracefully.
    """
    try:
        value = mpf(ai_number.value)
        # Factorial is only defined for non-negative integers
        if value < 0 or not value % 1 == 0:
            return AINumber("nan")
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the factorial of {ai_number.value}"))
        result: mpf = mpmath.gamma(value + mpf("1"))
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the factorial of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def gamma(ai_number: AINumber) -> AINumber:
    """
    Compute the gamma function using mpmath for high precision.
    Handles unsafe numbers and errors gracefully.
    """
    try:
        value = mpf(ai_number.value)
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the gamma of {ai_number.value}"))
        result: mpf = mpmath.gamma(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the gamma of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def ln(ai_number: AINumber) -> AINumber:
    """
    Compute the natural logarithm of a number with error handling and input validation.
    """
    try:
        value = mpf(ai_number.value)
        if value <= 0:
            return AINumber("nan")
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the natural logarithm of {ai_number.value}"))
        result: mpf = mpmath.ln(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the natural logarithm of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def log_10(ai_number: AINumber) -> AINumber:
    """
    Compute the base 10 logarithm of a number with error handling and input validation.
    """
    try:
        value = mpf(ai_number.value)
        if value <= 0:
            return AINumber("nan")
        if not is_safe_number(value):
            return AINumber(ai_calculate(f"Please return the base 10 logarithm of {ai_number.value}"))
        result: mpf = mpmath.log10(value)
        if is_safe_number(result):
            return AINumber(str(result))
        else:
            return AINumber(ai_calculate(f"Please return the base 10 logarithm of {ai_number.value}"))
    except Exception:
        return AINumber("nan")


def log_base(ai_number: AINumber, base: AINumber) -> AINumber:
    """
    Compute the logarithm of a number with a specified base.
    """
    if not is_safe_number(ai_number.value) or not is_safe_number(base.value):
        return AINumber(ai_calculate(f"Please return the base {base.value} logarithm of {ai_number.value}"))
    else:
        return log_10(ai_number) / log_10(base)


def is_prime(ai_number: AINumber) -> bool:
    """
    Check if a number is prime.
    """
    if is_safe_number(ai_number):
        if ai_number % 1 == 0:
            up_range: int = int(ai_number.__floor__())
            factors: list = [i for i in range(1, up_range) if ai_number // mpf(i) == ai_number / mpf(i)] + [ai_number]
            return len(factors) == 2
        return False
    else:
        response: str = ai_calculate(f"Is {ai_number.value} a prime number?")
        return response.lower() == "yes" or response.lower() == "true"


# The two following functions (obtaining GCD and LCM of two numbers) are inspired by the following source.
# https://www.geeksforgeeks.org/program-to-find-lcm-of-two-numbers/


def gcd(a: AINumber, b: AINumber) -> AINumber:
    """
    Compute the greatest common divisor (GCD) of two numbers using the Euclidean algorithm.
    """
    if a == 0:
        return b
    return gcd(b % a, a)


def lcm(a: AINumber, b: AINumber) -> AINumber:
    """
    Compute the least common multiple (LCM) of two numbers using the GCD.
    """
    return (a / gcd(a, b)) * b


def main():
    """Main entry point for GenAIMath"""
    a: AINumber = AINumber("10")
    b: AINumber = AINumber("20")
    print(f"{a} + {b} = {a + b}")
    print(f"{a} - {b} = {a - b}")
    print(f"{a} * {b} = {a * b}")
    print(f"{a} / {b} = {a / b}")
    print(f"{a} ** {b} = {a ** b}")
    print(f"{a} % {b} = {a % b}")
    print(f"{a} // {b} = {a // b}")
    print(f"Square root of {a} = {sqrt(a)}")
    print(f"Cube root of {a} = {cbrt(a)}")
    print(f"{a} squared = {a.squared()}")
    print(f"{a} cubed = {a.cubed()}")
    print(f"{a} tetrated to 3 = {a.tetrate(3)}")
    print(f"Factorial of {a} = {factorial(a)}")
    print(f"Gamma function of {a} = {gamma(a)}")
    print(f"Natural logarithm of {a} = {ln(a)}")
    print(f"Base 10 logarithm of {a} = {log_10(a)}")
    print(f"Is {a} a prime number? {'Yes' if is_prime(a) else 'No'}")
    print(f"GCD of {a} and {b} = {gcd(a, b)}")
    print(f"LCM of {a} and {b} = {lcm(a, b)}")


if __name__ == "__main__":
    main()
