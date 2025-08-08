from .get_file_drop import *
from ..imports import *
from abstract_utilities import get_media_exts, eatOuter
import os
import traceback
from PyQt5 import QtCore, QtGui, QtWidgets
from typing import List, Set, Optional
import ast
from .functions import (
    initialize_python_utils,
    initialize_view_utils,
    initialize_rebuild_utils
    )
logger = get_logFile('clipit_logs')


class FileDropArea(QtWidgets.QWidget):
    function_selected = QtCore.pyqtSignal(dict)
    file_selected = QtCore.pyqtSignal(dict)

    def __init__(self, log_widget: QtWidgets.QTextEdit, view_widget=None, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.log_widget = log_widget
        self.view_widget = view_widget
        self.dir_pieces = []
        self.ext_checks: dict[str, QtWidgets.QCheckBox] = {}
        self.dir_checks: dict[str, QtWidgets.QCheckBox] = {}
        self._last_raw_paths: list[str] = []
        self.functions: list[dict] = []
        self.python_files: list[dict] = []
        self.combined_text_lines: dict[str, dict] = {}
        self.allowed_extensions = DEFAULT_ALLOWED_EXTS
        self.unallowed_extensions = DEFAULT_UNALLOWED_EXTS
        self.exclude_types = DEFAULT_EXCLUDE_TYPES
        self.exclude_dirs = DEFAULT_EXCLUDE_DIRS | {"backup", "backups"}
        self.exclude_file_patterns = DEFAULT_EXCLUDE_PATTERNS
        self.exclude_dir_patterns = set()  # New: store user-specified dir patterns

        # Main vertical layout
        lay = QtWidgets.QVBoxLayout(self)

        # 1) “Browse Files…” button
        browse_btn = get_push_button(text="Browse Files…", action=self.browse_files)
        self.view_toggle = 'array'

        # 2) Extension-filter row
        self.ext_row = QtWidgets.QScrollArea(widgetResizable=True)
        self.ext_row.setFixedHeight(45)
        self.ext_row.setVisible(False)
        self.ext_row_w = QtWidgets.QWidget()
        self.ext_row.setWidget(self.ext_row_w)
        self.ext_row_lay = QtWidgets.QHBoxLayout(self.ext_row_w)
        self.ext_row_lay.setContentsMargins(4, 4, 4, 4)
        self.ext_row_lay.setSpacing(10)
        self._selected_text: dict[str, str] = {}

        # 3) Directory-filter row (new)
        # 3) Directory-filter row (checkboxes)
        self.dir_row = QtWidgets.QScrollArea(widgetResizable=True)
        self.dir_row.setFixedHeight(45)
        self.dir_row.setVisible(False)
        self.dir_row_w = QtWidgets.QWidget()
        self.dir_row.setWidget(self.dir_row_w)
        self.dir_row_lay = QtWidgets.QHBoxLayout(self.dir_row_w)
        self.dir_row_lay.setContentsMargins(4, 4, 4, 4)
        self.dir_row_lay.setSpacing(10)



        # 4) Tab widget to switch between “List View” and “Text View”
        self.view_tabs = QtWidgets.QTabWidget()

        # List View Tab
        list_tab = QtWidgets.QWidget()
        list_layout = get_layout(parent=list_tab)
        self.function_list = QtWidgets.QListWidget()
        self.function_list.setVisible(False)
        self.function_list.setAcceptDrops(False)
        self.function_list.itemClicked.connect(self.on_function_clicked)
        self.python_file_list = QtWidgets.QListWidget()
        self.python_file_list.setVisible(False)
        self.python_file_list.setAcceptDrops(False)
        self.python_file_list.itemClicked.connect(self.on_python_file_clicked)
        add_widgets(list_layout, {"widget": self.python_file_list}, {"widget": self.function_list})
        self.view_tabs.addTab(list_tab, "List View")

        # Text View Tab
        text_tab = QtWidgets.QWidget()
        text_layout = QtWidgets.QVBoxLayout(text_tab)
        self.text_view = QtWidgets.QTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setVisible(False)
        self.text_view.setAcceptDrops(False)
        add_widgets(text_layout, {"widget": self.text_view})
        self.view_tabs.addTab(text_tab, "Text View")

        # 5) Status label
        self.status = QtWidgets.QLabel("No files selected.", alignment=QtCore.Qt.AlignCenter)
        self.status.setStyleSheet("color: #333; font-size: 12px;")

        add_widgets(
            lay,
            {"widget": browse_btn, "kargs": {"alignment": QtCore.Qt.AlignHCenter}},
            {"widget": self.dir_row},  # Add directory filter row
            {"widget": self.ext_row},
            {"widget": self.view_tabs},
            {"widget": self.status}
        )

        # Initialize dir patterns from input
        self._update_dir_patterns()

    def _update_dir_patterns(self):
        """Update self.exclude_dir_patterns from dir_input text."""
        text = self.dir_checks
        if text:
            self.exclude_dir_patterns = self.dir_checks
        else:
            self.exclude_dir_patterns = set()
        self.exclude_dir_patterns.update(self.exclude_dirs)  # Include defaults

        #self._log(f"Directory row visible: True, checkboxes: {list(new_checks.keys())}")
    




    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent):
        try:
            urls = event.mimeData().urls()
            paths = [url.toLocalFile() for url in make_list(urls)]
            if not paths:
                raise ValueError("No local files detected on drop.")
            self.process_files(paths)
        except Exception as e:
            tb = traceback.format_exc()
            self.status.setText(f"⚠️ Error during drop: {e}")
            self._log(f"dropEvent ERROR:\n{tb}")

    def filter_paths(self, paths: list[str]) -> list[str]:
        filtered = collect_filepaths(
            paths,
            allowed_exts=self.allowed_extensions,
            unallowed_exts=self.unallowed_extensions,
            exclude_types=self.exclude_types,
            exclude_dirs=self.exclude_dir_patterns,  # Use dynamic dir patterns
            exclude_file_patterns=self.exclude_file_patterns
        )
        self._log(f"_filtered_file_list returned {len(filtered)} path(s)")
        if not filtered:
            self.status.setText("⚠️ No valid files detected in drop.")
            self._log("No valid paths after filtering.")
            return []
        self._log(f"Proceeding to process {len(filtered)} file(s).")
        return filtered

    def get_contents_text(self, file_path: str, idx: int = 0, filtered_paths: list[str] = []):
        basename = os.path.basename(file_path)
        filename, ext = os.path.splitext(basename)
        if ext not in self.unallowed_extensions:
            header = f"=== {file_path} ===\n"
            footer = "\n\n――――――――――――――――――\n\n"
            info = {
                'path': file_path,
                'basename': basename,
                'filename': filename,
                'ext': ext,
                'text': "",
                'error': False,
                'visible': True
            }
            try:
                body = read_file_as_text(file_path) or ""
                if isinstance(body, list):
                    body = "\n".join(body)
                info["text"] = [header, body, footer]
                if ext == '.py':
                    self._parse_functions(file_path, str(body))
            except Exception as exc:
                info["error"] = True
                info["text"] = f"[Error reading {basename}: {exc}]\n"
                self._log(f"Error reading {file_path} → {exc}")
            return info

    def process_files(self, paths: list[str] = None) -> None:
        paths = paths or []
        self._last_raw_paths = paths
        filtered = self.filter_paths(paths)
        if not filtered:
            return
        self._rebuild_ext_row(filtered)
        self._rebuild_dir_row(filtered)
        filtered_paths=[]
        if self.ext_checks or self.dir_checks:
            visible_exts = {ext for ext, cb in self.ext_checks.items() if cb.isChecked()}
            visible_dirs = {di for di, cb in self.dir_checks.items() if cb.isChecked()}
            self._log(f"Visible extensions: {visible_exts}")
            filtered_paths = [
                p for p in filtered
                if (os.path.isdir(p) or os.path.splitext(p)[1].lower() in visible_exts) and not is_string_in_dir(p,list(visible_dirs))
            ]
        else:
            filtered_paths  = filtered
        if not filtered_paths:
            self.text_view.clear()
            self.status.setText("⚠️ No files match current extension filter.")
            return
        self.status.setText(f"Reading {len(filtered_paths)} file(s)…")
        QtWidgets.QApplication.processEvents()
        self.combined_text_lines = {}
        self.functions = []
        self.python_files = []
        for idx, p in enumerate(filtered_paths, 1):
            info = self.get_contents_text(p, idx, filtered_paths)
            if info:
                self.combined_text_lines[p] = info
                if info['ext'] == '.py':
                    self.python_files.append(info)
        self._populate_list_view()
        self._populate_text_view()
        self.status.setText("Files processed. Switch tabs to view.")


 

    def on_function_clicked(self, item: QtWidgets.QListWidgetItem) -> None:
        index = self.function_list.row(item)
        function_info = self.functions[index]
        self.function_selected.emit(function_info)

    def on_python_file_clicked(self, item: QtWidgets.QListWidgetItem) -> None:
        index = self.python_file_list.row(item)
        file_info = self.python_files[index]
        self.file_selected.emit(file_info)

    def browse_files(self) -> None:
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select Files to Copy",
            "",
            "All Supported Files (" + " ".join(f"*{ext}" for ext in self.allowed_extensions) + ");;All Files (*)"
        )
        if files:
            filtered = self.filter_paths(files)
            if filtered:
                self.process_files(filtered)

    def _log(self, message: str) -> None:
        timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        logger.info(f"[{timestamp}] {message}")
        self.log_widget.append(f"[{timestamp}] {message}")

    def _clear_layout(self, layout: QtWidgets.QLayout) -> None:
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                
FileDropArea = initialize_rebuild_utils(FileDropArea)
FileDropArea = initialize_python_utils(FileDropArea)
FileDropArea = initialize_view_utils(FileDropArea)

