from .src.python_utils import (
    _parse_functions,
    _extract_imports,
    map_function_dependencies,
    map_import_chain
    )
def initialize_python_utils(self):
    self._parse_functions = _parse_functions
    self._extract_imports = _extract_imports
    self.map_function_dependencies = map_function_dependencies
    self.map_import_chain = map_import_chain
    return self

