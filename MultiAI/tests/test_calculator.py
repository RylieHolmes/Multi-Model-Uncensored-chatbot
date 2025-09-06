import unittest
import sys
import os

# Add the parent directory to the Python path to allow importing the tools module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.calculator import add

class TestCalculator(unittest.TestCase):
    """
    Unit tests for the calculator tool.
    To run tests, navigate to the MultiAI directory and run: python -m unittest discover
    """

    def test_add_positive_numbers(self):
        """Test adding two positive numbers."""
        self.assertEqual(add(5, 10), 15)

    def test_add_negative_numbers(self):
        """Test adding two negative numbers."""
        self.assertEqual(add(-5, -10), -15)

    def test_add_positive_and_negative(self):
        """Test adding a positive and a negative number."""
        self.assertEqual(add(-5, 10), 5)

    def test_add_zero(self):
        """Test adding zero to a number."""
        self.assertEqual(add(10, 0), 10)
        self.assertEqual(add(0, 10), 10)

    def test_add_floating_point_numbers(self):
        """Test adding two floating-point numbers."""
        self.assertAlmostEqual(add(0.1, 0.2), 0.3)

if __name__ == '__main__':
    unittest.main()