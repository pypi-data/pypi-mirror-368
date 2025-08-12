from .imports import *
from .functions import *
from abstract_clipit import FileDropArea,FileSystemTree,DragDropWithFileBrowser,JSBridge
from abstract_gui.managers.window_info_gui import WindowManagerApp

def getFinderTab(self,tabs):
    page = QWidget()
    layout = QVBoxLayout(page)
    self.finder = FinderWindow()
    tabs.addTab(self.finder, "Find Content")
def getClipitTab(self,tabs):
    page = QWidget()
    layout = QVBoxLayout(page)
    self.clipit = DragDropWithFileBrowser(FileSystemTree=FileSystemTree,FileDropArea=FileDropArea,JSBridge=JSBridge)
    tabs.addTab(self.clipit, "clipit")
def getApiTab(self,tabs):
    page = QWidget()
    layout = QVBoxLayout(page)
    self.api = APIConsole()
    tabs.addTab(self.api, "api Client")
def getWindowMgrTab(self,tabs):
    page = QWidget()
    layout = QVBoxLayout(page)
    self.windowMgr = WindowManagerApp()
    tabs.addTab(self.windowMgr, "Window Manager")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initializeInit()
        # ---------------- TABS ROOT (single root layout on self) ----------------
        tabs = QTabWidget(self)
        root_layout = QVBoxLayout(self)
        root_layout.addWidget(tabs)
        # ---------------- Runner page ----------------
        self.getRunner(tabs)
        # ---------------- Functions Map page ----------------
        self.getFunctions(tabs)
        getFinderTab(self,tabs)
        getApiTab(self,tabs)
        getClipitTab(self,tabs)
        getWindowMgrTab(self,tabs)



        # wire map events
        create_import_maps()
        self.graph = get_dot_data()
        self.func_map = get_import_graph_data()
        self.populate_function_buttons()
        self.btn_scan.clicked.connect(self.scan_functions)
        self.search_fn.textChanged.connect(self._filter_fn_buttons)
        self.exporters_list.itemDoubleClicked.connect(lambda it: os.system(f'code -g "{it.text()}"'))
        self.importers_list.itemDoubleClicked.connect(lambda it: os.system(f'code -g "{it.text()}"'))

        print(f"Errors list id in UI:   {id(self.errors_list)}")
        print(f"Warnings list id in UI: {id(self.warnings_list)}")
    def create_radio_group(self, labels, default_index=0, slot=None):
        """
        Create a QButtonGroup with QRadioButtons for the given labels.

        Args:
            self: parent widget (e.g. 'self' inside a class)
            labels (list[str]): button labels
            default_index (int): which button to check by default
            slot (callable): function to connect all toggled signals to
        Returns:
            (QButtonGroup, list[QRadioButton])
        """
        group = QButtonGroup(self)
        buttons = []

        for i, label in enumerate(labels):
            rb = QRadioButton(label)
            if i == default_index:
                rb.setChecked(True)
            group.addButton(rb)
            buttons.append(rb)
            if slot:
                rb.toggled.connect(slot)

        return group, buttons
    # ── actions ──────────────────────────────────────────────────────────────
    def start_work(self):
        try:
            self.run_btn.setEnabled(False)
            user = 'solcatcher' or self.user_in.text().strip()
            path = self.path_in.text().strip()
            if not path or not os.path.isdir(path):
                QMessageBox.critical(self, "Error", "Invalid project path.")
                self.run_btn.setEnabled(True)
                return

            # clear lists, keep existing log for comparison
            self.errors_list.clear()
            self.warnings_list.clear()

            self.worker = Worker(user, path)
            self.worker.log_line.connect(self.append_log)
            self.worker.build_output.connect(self.set_last_output)
            self.worker.errors_output.connect(lambda t: setattr(self, "last_errors_only", t or ""))
            self.worker.warnings_output.connect(lambda t: setattr(self, "last_warnings_only", t or ""))
            self.worker.error_entries_found.connect(self.show_error_entries)
            self.worker.warn_entries_found.connect(self.show_warning_entries)
            self.worker.finished.connect(lambda: self.run_btn.setEnabled(True))
            self.worker.start()
        except Exception:
            self.append_log("start_work error:\n" + traceback.format_exc() + "\n")
            self.run_btn.setEnabled(True)

    def clear_ui(self):
        self.log_view.clear()
        self.errors_list.clear()
        self.warnings_list.clear()
        self.last_output = ""
        self.last_errors_only = ""
        self.last_warnings_only = ""

    # ── log + entries ────────────────────────────────────────────────────────
    def append_log(self, text):
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_view.setTextCursor(cursor)
        self.log_view.insertPlainText(text)

    def set_last_output(self, text: str):
        self.last_output = text or ""
        self.apply_log_filter()

    def show_error_entries(self, entries):
        self.errors_list.clear()
        self.append_log(f"[dbg] show_error_entries entries={len(entries)} widget_id={id(self.errors_list)}\n")

 
        if self.cb_try_alt_ext.isChecked():
            entries = [(resolve_alt_ext(p, self.path_in.text().strip()), ln, col) for (p, ln, col) in entries]
        if not entries:
            self.append_log("\n✅ No matching errors.\n")
            return
        self.append_log("\nErrors found:\n")
        for path, line, col in entries:
            info = f"{path}:{line}:{col or 1}"
            self.append_log(info + "\n")
            self.errors_list.addItem(QListWidgetItem(info))

    def show_warning_entries(self, entries):
        self.warnings_list.clear()
        if self.cb_try_alt_ext.isChecked():
            entries = [(resolve_alt_ext(p, self.path_in.text().strip()), ln, col) for (p, ln, col) in entries]
        if not entries:
            self.append_log("\nℹ️ No warnings.\n")
            return
        self.append_log("\nWarnings found:\n")
        for path, line, col in entries:
            info = f"{path}:{line}:{col or 1}"
            self.append_log(info + "\n")
            self.warnings_list.addItem(QListWidgetItem(info))

    def apply_log_filter(self):
        if self.rb_err.isChecked():
            self._replace_log(self.last_errors_only or "(no errors)")
        elif self.rb_wrn.isChecked():
            self._replace_log(self.last_warnings_only or "(no warnings)")
        else:
            self._replace_log(self.last_output or "")

    # ── click handlers ───────────────────────────────────────────────────────
    def show_error_for_item(self, item: QListWidgetItem):
        info = item.text()
        try:
            path, line, col = self._parse_item(info)
            if self.cb_try_alt_ext.isChecked():
                path = resolve_alt_ext(path, self.path_in.text().strip())
            os.system(f'code -g "{path}:{line}:{col or 1}"')
            snippet = self._extract_errors_for_file(self.last_output, path, self.path_in.text().strip())
            self._replace_log(snippet if snippet else f"(No specific lines found for {path})\n\n{self.last_output}")
        except Exception:
            self.append_log("show_error_for_item error:\n" + traceback.format_exc() + "\n")

    def open_in_editor(self, item: QListWidgetItem):
        try:
            text = item.text()
            path, line, col = self._parse_item(text)
            if self.cb_try_alt_ext.isChecked():
                path = resolve_alt_ext(path, self.path_in.text().strip())
            os.system(f'code -g "{path}:{line}:{col or 1}"')
        except Exception:
            self.append_log("open_in_editor error:\n" + traceback.format_exc() + "\n")

    # ── helpers ──────────────────────────────────────────────────────────────
    def _replace_log(self, text: str):
        try:
            self.log_view.clear()
            self.log_view.insertPlainText(text)
        except Exception as e:
            print(f"{e}")
    def _parse_item(self, info: str):
        try:
            parts = info.rsplit(":", 2)
            if len(parts) == 3:
                path, line, col = parts[0], parts[1], parts[2]
            else:
                path, line, col = parts[0], parts[1], "1"
            return path, int(line), int(col)
        except Exception as e:
            print(f"{e}")
    def _extract_errors_for_file(self, combined_text: str, abs_path: str, project_root: str) -> str:
        """
        Return only lines for the clicked file (with small context windows).
        Matches absolute path and likely relative forms (e.g., src/foo.tsx(...)).
        """
        try:
            text = combined_text or ""
            if not text:
                return ""

            try:
                rel = os.path.relpath(abs_path, project_root) if (project_root and abs_path.startswith(project_root)) else os.path.basename(abs_path)
            except Exception:
                rel = os.path.basename(abs_path)

            rel_alt = rel.replace("\\", "/")
            abs_alt = abs_path.replace("\\", "/")
            base = os.path.basename(abs_alt)

            lines = text.splitlines()
            blocks = []
            for i, ln in enumerate(lines):
                if (abs_alt in ln) or (rel_alt in ln) or (("src/" + base) in ln):
                    start = max(0, i - 3)
                    end = min(len(lines), i + 6)
                    block = "\n".join(lines[start:end])
                    blocks.append(f"\n— context @ log line {i+1} —\n{block}\n")

            return "\n".join(blocks).strip()
        except Exception as e:
            print(f"{e}")
    def scan_functions(self):
        try:
            path = self.path_in.text().strip()
            if not path or not os.path.isdir(path):
                QMessageBox.critical(self, "Error", "Invalid project path.")
                return
            scope = self.scope_combo.currentText()
            self.btn_scan.setEnabled(False)
            self.append_log(f"[map] starting scan ({scope})\n")

            entries_txt = "index,main"  # or add a QLineEdit for this
            entries = [s.strip() for s in entries_txt.split(",") if s.strip()]
            self.map_worker = ImportGraphWorker(path, scope=scope, entries=entries)
            self.map_worker.log.connect(self.append_log)
            self.map_worker.ready.connect(self._on_map_ready)
            self.map_worker.finished.connect(lambda: self.btn_scan.setEnabled(True))
            self.map_worker.start()
        except Exception as e:
            print(f"{e}")

    def _on_map_ready(self, graph:dict, func_map:dict):
        try:
            self.graph = graph or {}
            self.func_map = func_map or {}
            self._rebuild_fn_buttons(self.func_map.keys())
        except Exception as e:
            print(f"error _on_map_ready: {e}")
    def _rebuild_fn_buttons(self, names_iterable):
        try:
            # clear container
            while self.fn_vbox.count():
                item = self.fn_vbox.takeAt(0)
                w = item.widget()
                if w: w.setParent(None)
            # (re)populate
            names = sorted(n for n in names_iterable if n and n != '<reexport>')
            for name in names:
                btn = QPushButton(name)
                btn.clicked.connect(lambda _, n=name: self._on_function_clicked(n))
                self.fn_vbox.addWidget(btn)
            self.fn_vbox.addStretch(1)
        except Exception as e:
            print(f"error _rebuild_fn_buttons: {e}")
    def _filter_fn_buttons(self, text:str):
        try:
            text = (text or '').strip().lower()
            if not self.func_map:
                return
            if not text:
                self._rebuild_fn_buttons(self.func_map.keys())
            else:
                match = [n for n in self.func_map.keys() if text in n.lower()]
                self._rebuild_fn_buttons(match)
        except Exception as e:
            print(f"error _filter_fn_buttons: {e}")
    def _on_function_clicked(self, fn_name: str):
        try:
            datas = self.func_map.get(fn_name, {'exported_in': [], 'imported_in': []})

            self.exporters_list.clear()
            self.importers_list.clear()

            if isinstance(datas, dict):
                for f in datas.get('exported_in', []):
                    self.exporters_list.addItem(f)
                for f in datas.get('imported_in', []):
                    self.importers_list.addItem(f)

            elif isinstance(datas, list):
                for data in datas:
                    if isinstance(data, dict):
                        for f in data.get('exported_in', []):
                            self.exporters_list.addItem(f)
                        for f in data.get('imported_in', []):
                            self.importers_list.addItem(f)
                    elif isinstance(data, str):
                        self.exporters_list.addItem(data)
                        self.importers_list.addItem(data)

        except Exception as e:
            print(f"error _on_function_clicked: {e}")
    def populate_function_buttons(self):
        # Clear old buttons
        for i in reversed(range(self.fn_vbox.count())):
            widget_item = self.fn_vbox.itemAt(i).widget()
            if widget_item:
                widget_item.setParent(None)

        # Add a button for each function name
        for fn_name in sorted(self.func_map.keys()):
            btn = QPushButton(fn_name)
            btn.clicked.connect(lambda _, name=fn_name: self._on_function_clicked(name))
            self.fn_vbox.addWidget(btn)

        self.fn_vbox.addStretch(1)
    def _on_function_clicked(self, fn_name: str):
        try:
            self.current_fn = fn_name
            self._render_fn_lists()
        except Exception as e:
            print(f"error _on_function_clicked: {e}")
    def _render_fn_lists(self):
        self.exporters_list.clear()
        self.importers_list.clear()

        if not self.current_fn or not isinstance(self.func_map, dict):
            return

        data = self.func_map.get(self.current_fn, {'exported_in': [], 'imported_in': []})

        # normalize to lists
        exported_in, imported_in = [], []
        if isinstance(data, dict):
            exported_in = list(dict.fromkeys(data.get('exported_in', [])))
            imported_in = list(dict.fromkeys(data.get('imported_in', [])))
        elif isinstance(data, list):
            for d in data:
                if isinstance(d, dict):
                    exported_in += d.get('exported_in', [])
                    imported_in += d.get('imported_in', [])
                elif isinstance(d, str):
                    exported_in.append(d); imported_in.append(d)
            exported_in = list(dict.fromkeys(exported_in))
            imported_in = list(dict.fromkeys(imported_in))

        mode = self.fn_filter_mode

        if mode == "source":
            # Only show where the function is defined/exported
            for f in sorted(exported_in):
                self.exporters_list.addItem(f)
            # leave importers empty
        elif mode == "io":
            # Split view: exporters on top, importers on bottom (your current behavior)
            for f in sorted(exported_in):
                self.exporters_list.addItem(f)
            for f in sorted(imported_in):
                self.importers_list.addItem(f)
        elif mode == "all":
            # Union of both—put them together in the top list to avoid duplication
            union = sorted(set(exported_in) | set(imported_in))
            for f in union:
                self.exporters_list.addItem(f)
            # leave bottom empty
    def _on_filter_mode_changed(self):
        if self.rb_fn_source.isChecked():
            self.fn_filter_mode = "source"
        elif self.rb_fn_all.isChecked():
            self.fn_filter_mode = "all"
        else:
            self.fn_filter_mode = "io"

        # Re-render current selection if any
        if self.current_fn:
            self._render_fn_lists()
getManagerFuncs(MainWindow)
