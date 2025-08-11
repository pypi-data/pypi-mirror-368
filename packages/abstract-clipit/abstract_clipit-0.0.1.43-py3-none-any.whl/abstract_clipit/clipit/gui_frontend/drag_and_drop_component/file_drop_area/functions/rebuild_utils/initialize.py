from .utils.utils import (
    _rebuild_dir_row,
    _rebuild_ext_row,
    _apply_ext_filter
    )
def initialize_rebuild_utils(self):
    self._rebuild_dir_row = _rebuild_dir_row
    self._rebuild_ext_row = _rebuild_ext_row
    self._apply_ext_filter = _apply_ext_filter
    return self
