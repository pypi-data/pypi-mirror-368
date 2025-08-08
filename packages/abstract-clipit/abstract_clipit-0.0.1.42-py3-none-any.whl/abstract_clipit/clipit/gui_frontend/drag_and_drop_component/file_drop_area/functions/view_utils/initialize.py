from .utils.utils import (
    _toggle_populate_text_view,
    _populate_text_view,
    _populate_list_view,
    populate_python_view
    )
def initialize_view_utils(self):
    self._toggle_populate_text_view = _toggle_populate_text_view
    self._populate_text_view = _populate_text_view
    self._populate_list_view = _populate_list_view
    self.populate_python_view = populate_python_view
    return self
