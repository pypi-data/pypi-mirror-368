from ...imports import *
def getFunctions(self,tabs):

        func_page = QWidget()
        func_layout = QHBoxLayout(func_page)

        # left column
        left_col = QVBoxLayout()
        self.btn_scan = QPushButton("Scan Project Functions")
        scope_row = QHBoxLayout()
        self.scope_combo = QComboBox()
        self.scope_combo.addItems(["all", "reachable"])
        createWidget(
                layout=left_col,
                label="Scope:",
                widgetFunc=QHBoxLayout,
                getLayout={},
                addFunc='addWidget',
                widgets = (
                    (self.scope_combo, {"stretch":1}),

                )
            )



        left_col.addWidget(self.btn_scan)

        self.search_fn = QLineEdit(); self.search_fn.setPlaceholderText("Filter functions…")
        left_col.addWidget(self.search_fn)

        # filter buttons row (above function buttons)
        fn_filter_row = QHBoxLayout()
        self.rb_fn_source = QRadioButton("Function")        # only where it's defined/exported
        self.rb_fn_io     = QRadioButton("Import/Export")   # split: exporters & importers
        self.rb_fn_all    = QRadioButton("All")             # union of both
        self.rb_fn_io.setChecked(True)

        self.fn_filter_group = QButtonGroup(self)
        for rb in (self.rb_fn_source, self.rb_fn_io, self.rb_fn_all):
            self.fn_filter_group.addButton(rb)
            fn_filter_row.addWidget(rb)
        fn_filter_row.addStretch(1)

        # when mode changes, re-render the lists for the currently selected function
        self.rb_fn_source.toggled.connect(lambda _: self._on_filter_mode_changed())
        self.rb_fn_io.toggled.connect(lambda _: self._on_filter_mode_changed())
        self.rb_fn_all.toggled.connect(lambda _: self._on_filter_mode_changed())

        left_col.addLayout(fn_filter_row)


        self.fn_scroll = QScrollArea(); self.fn_scroll.setWidgetResizable(True)
        self.fn_container = QWidget()
        self.fn_vbox = QVBoxLayout(self.fn_container)
        self.fn_vbox.addStretch(1)
        self.fn_scroll.setWidget(self.fn_container)
        left_col.addWidget(self.fn_scroll, 1)

        # right column
        right_col = QVBoxLayout()
        right_col.addWidget(QLabel("Files exporting selected function:"))
        self.exporters_list = QListWidget(); right_col.addWidget(self.exporters_list, 1)
        right_col.addWidget(QLabel("Files importing selected function:"))
        self.importers_list = QListWidget(); right_col.addWidget(self.importers_list, 1)

        func_layout.addLayout(left_col, 1)
        func_layout.addLayout(right_col, 2)

        tabs.addTab(func_page, "Functions Map")
