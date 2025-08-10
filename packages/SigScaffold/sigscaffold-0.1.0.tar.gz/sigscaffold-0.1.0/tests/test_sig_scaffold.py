import unittest
from typing import Any, Dict

from sig_scaffold.sig_scaffold import SigScaffold


# --- Test Fixtures ---

def simple_function(a: int, b: str = "default"):
    """A simple function for testing."""
    pass


class AnotherClass:
    """A simple class for recursive testing."""
    def __init__(self, x: float, y: bool = True):
        pass


class MyClass:
    """A class with a constructor to be inspected."""
    def __init__(self, req_param: int, opt_param: str = "hello", class_param: AnotherClass = None):
        pass


def function_with_various_types(
    p_int: int,
    p_str: str,
    p_float: float,
    p_bool: bool,
    p_list: list,
    p_dict: dict,
    p_any: Any,
    p_no_hint,
    p_default_int: int = 10,
):
    """A function with a variety of parameter types."""
    pass


def no_params():
    """A function with no parameters."""
    pass


# --- Test Cases ---

class TestSigScaffold(unittest.TestCase):
    """Test suite for the SigScaffold class."""

    def test_init_with_non_callable(self):
        """Should raise TypeError when initialized with a non-callable."""
        with self.assertRaises(TypeError):
            SigScaffold(123)

    def test_get_param_types_simple(self):
        """Should correctly get parameter types for a simple function."""
        scaffold = SigScaffold(simple_function)
        expected = {'a': int, 'b': str}
        self.assertEqual(scaffold.get_param_types(), expected)

    def test_get_param_types_class_constructor(self):
        """Should correctly get parameter types for a class constructor."""
        scaffold = SigScaffold(MyClass)
        expected = {'req_param': int, 'opt_param': str, 'class_param': AnotherClass}
        self.assertEqual(scaffold.get_param_types(), expected)

    def test_get_param_types_recursive(self):
        """Should handle recursive type inspection."""
        scaffold = SigScaffold(MyClass)
        expected = {
            'req_param': int,
            'opt_param': str,
            'class_param': {
                'x': float,
                'y': bool
            }
        }
        self.assertEqual(scaffold.get_param_types(recursive=True), expected)

    def test_get_param_types_no_params(self):
        """Should return an empty dict for a function with no parameters."""
        scaffold = SigScaffold(no_params)
        self.assertEqual(scaffold.get_param_types(), {})

    def test_get_param_types_no_signature(self):
        """Should handle callables with no inspectable signature (e.g., built-ins)."""
        scaffold = SigScaffold(int)
        self.assertEqual(scaffold.get_param_types(), {})

    def test_get_required_params(self):
        """Should correctly identify required parameters."""
        scaffold = SigScaffold(MyClass)
        # Note: 'class_param' has a default value of None
        self.assertEqual(scaffold.get_required_params(), ['req_param'])

    def test_get_required_params_all_required(self):
        """Should identify all parameters as required when none have defaults."""
        def all_req(a: int, b: str): pass
        scaffold = SigScaffold(all_req)
        self.assertEqual(set(scaffold.get_required_params()), {'a', 'b'})

    def test_get_required_params_none_required(self):
        """Should identify no parameters as required when all have defaults."""
        def none_req(a: int = 1, b: str = "b"): pass
        scaffold = SigScaffold(none_req)
        self.assertEqual(scaffold.get_required_params(), [])

    def test_generate_defaults(self):
        """Should generate a dictionary of default values based on type hints."""
        scaffold = SigScaffold(function_with_various_types)
        expected = {
            'p_int': 0,
            'p_str': "",
            'p_float': 0.0,
            'p_bool': False,
            'p_list': [],
            'p_dict': {},
            'p_any': "",
            'p_no_hint': "",
            'p_default_int': 10,
        }
        self.assertEqual(scaffold.generate_defaults(), expected)

    def test_generate_defaults_with_class(self):
        """Should use provided defaults, including None for objects."""
        scaffold = SigScaffold(MyClass)
        expected = {
            'req_param': 0,
            'opt_param': 'hello',
            'class_param': None
        }
        self.assertEqual(scaffold.generate_defaults(), expected)

    def test_generate_defaults_no_params(self):
        """Should return an empty dictionary for a function with no parameters."""
        scaffold = SigScaffold(no_params)
        self.assertEqual(scaffold.generate_defaults(), {})


if __name__ == '__main__':
    unittest.main()


def function_with_generic_types(p_dict: Dict[str, int]):
    """A function with a generic Dict type hint."""
    pass


class TestSigScaffoldAdvanced(unittest.TestCase):
    """More advanced test cases for SigScaffold."""

    def test_generate_defaults_for_generic_dict(self):
        """Should correctly generate a default for Dict[str, int]."""
        scaffold = SigScaffold(function_with_generic_types)
        expected = {'p_dict': {}}
        self.assertEqual(scaffold.generate_defaults(), expected)
