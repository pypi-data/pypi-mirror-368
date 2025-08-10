import inspect
from typing import Any, Dict, List, Callable, get_origin


class SigScaffold:
    """
    A tool to inspect callables (functions/classes) and derive structured
    information about their signatures, intended for automated contract generation.
    """

    def __init__(self, target: Callable[..., Any]):
        """
        Initializes the scaffolder with a target callable.

        Args:
            target: The function or class to be inspected.

        Raises:
            TypeError: If the target is not a callable.
        """
        if not callable(target):
            raise TypeError("Target must be a callable (function or class).")
        self.target = target
        try:
            self.signature = inspect.signature(self.target)
        except ValueError:
            # Handles cases like built-in types (e.g., int, str) that don't have a typical signature.
            self.signature = None

    def get_param_types(self, recursive: bool = False) -> Dict[str, Any]:
        """
        Derives a dictionary of parameter names and their types.

        If recursive is True, it will attempt to inspect the constructors of
        any parameter whose type is a class.

        Args:
            recursive: Flag to enable/disable recursive inspection.

        Returns:
            A dictionary mapping parameter names to their types.
            For recursive calls, the type may be a nested dictionary.
        """
        if not self.signature:
            return {}

        params: Dict[str, Any] = {}
        for name, param in self.signature.parameters.items():
            param_type = param.annotation

            # Check for recursion and ensure the type is a class and not a primitive/builtin container
            if recursive and inspect.isclass(param_type) and param_type.__module__ not in ['builtins', 'typing']:
                try:
                    # Recurse into the constructor of the parameter's type
                    scaffold = SigScaffold(param_type)
                    params[name] = scaffold.get_param_types(recursive=True)
                except (TypeError, ValueError):
                    # If it's not a class with a valid signature, just use the type
                    params[name] = param_type if param_type is not inspect.Parameter.empty else Any
            else:
                params[name] = param_type if param_type is not inspect.Parameter.empty else Any
        return params

    def get_required_params(self) -> List[str]:
        """
        Returns a list of parameter names that are required (have no default value).

        Returns:
            A list of strings, where each string is a required parameter name.
        """
        if not self.signature:
            return []

        required = []
        for name, param in self.signature.parameters.items():
            if param.default is inspect.Parameter.empty:
                required.append(name)
        return required

    def generate_defaults(self) -> Dict[str, Any]:
        """
        Generates a dictionary of parameters with sensible default values.

        - If a parameter has a default value, it is used.
        - If not, a default is generated based on the type hint.
        - If there is no type hint, the default is an empty string.

        Returns:
            A dictionary mapping parameter names to their generated default values.
        """
        if not self.signature:
            return {}

        defaults: Dict[str, Any] = {}
        for name, param in self.signature.parameters.items():
            if param.default is not inspect.Parameter.empty:
                defaults[name] = param.default
            else:
                param_type = param.annotation
                origin_type = get_origin(param_type) or param_type

                if origin_type is dict:
                    defaults[name] = {}
                elif origin_type is list:
                    defaults[name] = []
                elif param_type is str:
                    defaults[name] = ""
                elif param_type is int:
                    defaults[name] = 0
                elif param_type is float:
                    defaults[name] = 0.0
                elif param_type is bool:
                    defaults[name] = False
                else:
                    # For Any, custom classes, or no type hint, default to empty string as requested.
                    defaults[name] = ""
        return defaults
