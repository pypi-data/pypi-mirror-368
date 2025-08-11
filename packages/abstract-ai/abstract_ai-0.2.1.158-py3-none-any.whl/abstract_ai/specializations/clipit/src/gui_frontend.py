#!/usr/bin/env python3
# gui_frontend.py (with a toggleable log console)

import sys
import os
from PyQt5 import QtCore, QtWidgets, QtGui
from typing import List

#(Adjust this import path to wherever your robust_reader actually lives.)
from abstract_utilities.robust_reader import read_file_as_text, collect_filepaths

DEFAULT_EXCLUDE_DIRS = {"node_modules", "__pycache__"}
DEFAULT_EXCLUDE_FILE_PATTERNS = {"*.ini", "*.tmp", "*.log"}


class FileDropArea(QtWidgets.QWidget):
    """
    Right‐hand pane: “Drag‐Drop → Clipboard.”
    """
    def __init__(self, log_widget: QtWidgets.QTextEdit, parent=None):
        super().__init__(parent)
        self.log_widget = log_widget  # reference to the shared log console

        self.setWindowTitle("Drag‐Drop → Clipboard")
        self.resize(600, 400)
        self.setAcceptDrops(True)

        layout = QtWidgets.QVBoxLayout(self)

        # Instruction label
        self.info = QtWidgets.QLabel(
            "Drag one or more supported files here,\nor click “Browse…”",
            self
        )
        self.info.setAlignment(QtCore.Qt.AlignCenter)
        self.info.setStyleSheet("font-size: 14px; color: #555;")
        layout.addWidget(self.info, stretch=1)

        # “Browse…” button
        browse_btn = QtWidgets.QPushButton("Browse Files…", self)
        browse_btn.clicked.connect(self.browse_files)
        layout.addWidget(browse_btn, alignment=QtCore.Qt.AlignHCenter)

        # Status label
        self.status = QtWidgets.QLabel("No files selected.", self)
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        self.status.setStyleSheet("color: #333; font-size: 12px;")
        layout.addWidget(self.status, stretch=1)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent):
        """
        Wrap in try/except so invalid drops don’t crash. Log everything.
        """
        try:
            urls = event.mimeData().urls()
            paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
            if not paths:
                raise ValueError("No local files detected on drop.")
            paths = self._filtered_file_list(paths)
            self._log(f"dropEvent: Received {len(paths)} path(s).")
            self.process_files(paths)
        except Exception as e:
            msg = f"dropEvent ERROR: {e}"
            self.status.setText(f"⚠️ Error: {e}")
            self._log(msg)

    def browse_files(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select Files to Copy",
            "",
            "All Supported Files (*.txt *.md *.csv *.tsv *.log "
            "*.xls *.xlsx *.ods *.parquet *.geojson *.shp);;All Files (*)"
        )
        if files:
            files = self._filtered_file_list(files)
            self._log(f"browse_files: Selected {len(files)} file(s).")
            self.process_files(files)

    def _filtered_file_list(self, raw_paths: List[str]) -> List[str]:
        """
        Recursively collect files under directories (excluding node_modules/__pycache__, etc).
        """
        from abstract_utilities.robust_reader import collect_filepaths
        filtered = collect_filepaths(
            raw_paths,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_file_patterns=DEFAULT_EXCLUDE_FILE_PATTERNS
        )
        self._log(f"_filtered_file_list: Expanded to {len(filtered)} file(s).")
        return filtered

    def process_files(self, file_paths: List[str]):
        """
        Same as before, except we log each major step.
        """
        valid_paths = [p for p in file_paths if os.path.isfile(p) or os.path.isdir(p)]
        if not valid_paths:
            self.status.setText("⚠️ No valid files detected.")
            self._log("process_files: No valid paths found.")
            return

        count = len(valid_paths)
        status_msg = f"Reading {count} file(s)…"
        self.status.setText(status_msg)
        self._log(status_msg)
        QtWidgets.QApplication.processEvents()

        combined_parts = []
        for idx, path in enumerate(valid_paths):
            header = f"=== {path} ===\n"
            combined_parts.append(header)
            self._log(f"process_files: Reading '{path}'")
            try:
                from abstract_utilities.robust_reader import read_file_as_text
                content_str = read_file_as_text(path)
                combined_parts.append(content_str)
            except Exception as e:
                err_line = f"[Error reading {os.path.basename(path)}: {e}]\n"
                combined_parts.append(err_line)
                self._log(f"process_files ERROR: {e}")

            if idx < count - 1:
                combined_parts.append("\n\n――――――――――――――――――\n\n")

        final_output = "".join(combined_parts)

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(final_output, mode=clipboard.Clipboard)

        success_msg = f"✅ Copied {count} file(s) to clipboard!"
        self.status.setText(success_msg)
        self._log(success_msg)

    def _log(self, message: str):
        """Append a line to the shared log widget, with timestamp."""
        timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.log_widget.append(f"[{timestamp}] {message}")


class FileSystemTree(QtWidgets.QWidget):
    """
    Left‐hand pane: file browser + “Copy Selected” button.
    """
    def __init__(self, log_widget: QtWidgets.QTextEdit, parent=None):
        super().__init__(parent)
        self.log_widget = log_widget

        layout = QtWidgets.QVBoxLayout(self)

        # QFileSystemModel + QTreeView
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(QtCore.QDir.rootPath())

        self.tree = QtWidgets.QTreeView()
        self.tree.setModel(self.model)

        for col in range(1, self.model.columnCount()):
            self.tree.hideColumn(col)

        home_index = self.model.index(QtCore.QDir.homePath())
        self.tree.setRootIndex(home_index)

        # Multi-selection & drag from tree
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tree.setDragEnabled(True)
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)

        layout.addWidget(self.tree)

        # “Copy Selected” button
        copy_btn = QtWidgets.QPushButton("Copy Selected to Clipboard")
        copy_btn.clicked.connect(self.copy_selected)
        layout.addWidget(copy_btn)

        self.setLayout(layout)

    def copy_selected(self):
        """
        Gather all selected items (column=0 only), convert to paths,
        and hand them off to parent’s on_tree_copy().
        """
        indexes = self.tree.selectionModel().selectedIndexes()
        file_paths = set()
        for idx in indexes:
            if idx.column() == 0:
                path = self.model.filePath(idx)
                file_paths.add(path)

        if not file_paths:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select at least one file or folder.")
            return

        msg = f"copy_selected: {len(file_paths)} item(s) selected."
        self._log(msg)

        parent = self.parent()
        if parent and hasattr(parent, "on_tree_copy"):
            parent.on_tree_copy(list(file_paths))

    def _log(self, message: str):
        """Write out to the shared log widget (with timestamp)."""
        timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.log_widget.append(f"[{timestamp}] {message}")


class DragDropWithBrowser(QtWidgets.QWidget):
    """
    Main window: includes menu toolbar with “Toggle Logs,”
    left = FileSystemTree, right = FileDropArea, bottom = QTextEdit for logs.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClipIt - File Browser + Drag/Drop + Logs")
        self.resize(950, 600)

        # Vertical layout: top = toolbar + splitter, bottom = log console (hidden by default)
        main_layout = QtWidgets.QVBoxLayout(self)

        # ─── Toolbar ─────────────────────────────────────────────────────────────────
        toolbar = QtWidgets.QToolBar()
        toolbar.setMovable(False)

        # Toggle‐Logs action
        self.toggle_logs_action = QtWidgets.QAction("Show Logs", self)
        self.toggle_logs_action.setCheckable(True)
        self.toggle_logs_action.triggered.connect(self._toggle_logs)
        toolbar.addAction(self.toggle_logs_action)

        # (You can add more toolbar buttons here if desired.)

        main_layout.addWidget(toolbar)

        # ─── Splitter (Tree + DropArea) ───────────────────────────────────────────────
        splitter = QtWidgets.QSplitter(self)
        splitter.setOrientation(QtCore.Qt.Horizontal)

        # Shared log widget (initially hidden)
        self.log_widget = QtWidgets.QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setStyleSheet("background: #111; color: #eee; font-family: monospace;")
        self.log_widget.hide()

        # Left pane: FileSystemTree (pass the log widget so it can write logs)
        self.tree_wrapper = FileSystemTree(log_widget=self.log_widget, parent=self)
        splitter.addWidget(self.tree_wrapper)

        # Right pane: FileDropArea (also uses the same log widget)
        self.drop_area = FileDropArea(log_widget=self.log_widget, parent=self)
        splitter.addWidget(self.drop_area)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # ─── Log Console ─────────────────────────────────────────────────────────────
        # Place it below everything; initially hidden
        main_layout.addWidget(self.log_widget)

        self.setLayout(main_layout)

        # Connect double-click in tree → process single file
        self.tree_wrapper.tree.doubleClicked.connect(self.on_tree_double_click)

    def on_tree_double_click(self, index: QtCore.QModelIndex):
        model = self.tree_wrapper.model
        path = model.filePath(index)
        if path:
            self._log(f"Double-clicked: {path}")
            self.drop_area.process_files([path])

    def on_tree_copy(self, paths: List[str]):
        """
        Called when the “Copy Selected” button is pressed.
        We log how many items, then forward to drop_area.
        """
        self._log(f"Copy Selected triggered on {len(paths)} path(s).")
        self.drop_area.process_files(paths)

    def _toggle_logs(self, checked: bool):
        """
        Show/hide the log console when the toolbar action is toggled.
        """
        if checked:
            self.log_widget.show()
            self.toggle_logs_action.setText("Hide Logs")
            self._log("Logs shown.")
        else:
            self._log("Logs hidden.")
            self.log_widget.hide()
            self.toggle_logs_action.setText("Show Logs")

    def _log(self, message: str):
        """Write directly to the log console (with timestamp)."""
        timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.log_widget.append(f"[{timestamp}] {message}")


def gui_main():
    app = QtWidgets.QApplication(sys.argv)
    window = DragDropWithBrowser()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    gui_main()
