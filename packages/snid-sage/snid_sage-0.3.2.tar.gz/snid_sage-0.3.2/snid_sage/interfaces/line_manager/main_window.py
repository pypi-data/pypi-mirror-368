"""
SNID Line Manager - Main Window
==============================

Spin-off GUI to manage SN and galaxy spectral lines and preset sets.
Now supports loading a spectrum and running preprocessing for analysis context.
"""

from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import os
import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui

from snid_sage.shared.utils.line_detection.user_line_store import (
    get_effective_line_db,
    load_user_lines,
    save_user_lines,
    load_user_presets,
    save_user_presets,
    add_or_update_user_line,
    delete_user_line,
)

# Reuse Template Manager theme/layout for consistency
from snid_sage.interfaces.template_manager.utils.theme_manager import (
    get_template_theme_manager,
)
from snid_sage.interfaces.template_manager.utils.layout_manager import (
    get_template_layout_manager,
)

# Plotting (pyqtgraph, optional)
try:
    import pyqtgraph as pg  # type: ignore
    PYQTGRAPH_AVAILABLE = True
except Exception:
    PYQTGRAPH_AVAILABLE = False

# Category colors
from snid_sage.shared.constants.physical import CATEGORY_COLORS

# Config manager for small UI state
try:
    from snid_sage.shared.utils.config.configuration_manager import config_manager
except Exception:
    config_manager = None  # type: ignore


class SNIDLineManagerGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_manager = get_template_theme_manager()
        self.layout_manager = get_template_layout_manager()
        self.current_spectrum: Dict[str, Any] | None = None
        self._user_presets: Dict[str, Any] = load_user_presets().get("presets", {})
        self._user_lines: List[Dict[str, Any]] = load_user_lines()
        self._build_ui()
        self._refresh_tables()

    def _build_ui(self) -> None:
        self.setWindowTitle("SNID Line Manager")
        try:
            from snid_sage.interfaces.gui.utils.logo_manager import get_logo_manager
            self.setWindowIcon(QtGui.QIcon(str(get_logo_manager().get_icon_path())))
        except Exception:
            self.setWindowIcon(QtGui.QIcon())

        self.layout_manager.setup_main_window(self)
        try:
            self.setStyleSheet(self.theme_manager.generate_complete_stylesheet())
        except Exception:
            pass

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        self.layout_manager.apply_panel_layout(central, main_layout)

        tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(tabs)

        # Lines Tab (now contains two sub-tabs: Available Lines and Test Spectrum)
        self.lines_tab = self._build_lines_tab()
        tabs.addTab(self.lines_tab, "📏 Lines")

        # Presets Tab
        self.presets_tab = self._build_presets_tab()
        tabs.addTab(self.presets_tab, "🧰 Presets")

        self._build_status_bar()

    def _build_status_bar(self) -> None:
        status = self.statusBar()
        self.count_label = QtWidgets.QLabel()
        status.addWidget(self.count_label)
        self._update_counts()

    # --- Lines Tab ---
    def _build_lines_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        self.layout_manager.apply_panel_layout(w, layout)

        # Create sub-tabs to separate concerns
        subtabs = QtWidgets.QTabWidget()
        layout.addWidget(subtabs)

        # Available Lines panel
        available_panel = self._build_available_lines_panel()
        subtabs.addTab(available_panel, "🗂 Available Lines")

        # Test Spectrum panel
        test_panel = self._build_test_spectrum_panel()
        subtabs.addTab(test_panel, "🔬 Test Spectrum")

        return w

    def _build_available_lines_panel(self) -> QtWidgets.QWidget:
        panel = QtWidgets.QWidget()
        vlayout = QtWidgets.QVBoxLayout(panel)
        self.layout_manager.apply_panel_layout(panel, vlayout)

        # Search only (kept here)
        search_layout = QtWidgets.QHBoxLayout()
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Search by name/category/origin…")
        self.search_edit.textChanged.connect(self._refresh_line_table)
        search_layout.addWidget(self.search_edit)
        vlayout.addLayout(search_layout)

        splitter = self.layout_manager.create_main_splitter()
        vlayout.addWidget(splitter)

        # Table of effective lines (built-in + user)
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        self.layout_manager.apply_panel_layout(left, left_layout)
        self.line_table = QtWidgets.QTableWidget(0, 6)
        self.line_table.setHorizontalHeaderLabels(["Name", "Air (Å)", "Vac (Å)", "Category", "Origin", "SN Types"])
        self.layout_manager.setup_table_widget(self.line_table)
        self.line_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.line_table.selectionModel().selectionChanged.connect(self._on_table_selection)
        # Redraw line overlays when selection changes (affects Test Spectrum tab plot)
        self.line_table.selectionModel().selectionChanged.connect(lambda *_: self._draw_line_overlays())
        left_layout.addWidget(self.line_table)

        btns = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add")
        self.edit_btn = QtWidgets.QPushButton("Edit")
        self.delete_btn = QtWidgets.QPushButton("Delete")
        self.save_btn = QtWidgets.QPushButton("Save All")
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.add_btn.clicked.connect(self._add_line)
        self.edit_btn.clicked.connect(self._edit_selected_line)
        self.delete_btn.clicked.connect(self._delete_selected_line)
        self.save_btn.clicked.connect(self._save_user_lines)
        for b in (self.add_btn, self.edit_btn, self.delete_btn, self.save_btn):
            btns.addWidget(b)
        left_layout.addLayout(btns)

        splitter.addWidget(left)

        # Editor on the right
        right = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(right)
        self.layout_manager.setup_form_layout(form)
        self.name_edit = QtWidgets.QLineEdit()
        self.air_spin = QtWidgets.QDoubleSpinBox()
        self.air_spin.setRange(0.0, 50000.0)
        self.air_spin.setDecimals(3)
        self.vac_spin = QtWidgets.QDoubleSpinBox()
        self.vac_spin.setRange(0.0, 50000.0)
        self.vac_spin.setDecimals(3)
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(list(_category_list()))
        self.origin_combo = QtWidgets.QComboBox()
        self.origin_combo.addItems(["sn", "galaxy", "stellar", "alias"]) 
        self.sn_types_edit = QtWidgets.QLineEdit()
        self.note_edit = QtWidgets.QLineEdit()
        form.addRow("Name:", self.name_edit)
        form.addRow("Air (Å):", self.air_spin)
        form.addRow("Vac (Å):", self.vac_spin)
        form.addRow("Category:", self.category_combo)
        form.addRow("Origin:", self.origin_combo)
        form.addRow("SN Types (comma):", self.sn_types_edit)
        form.addRow("Note:", self.note_edit)
        self.apply_btn = QtWidgets.QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self._apply_editor_changes)
        form.addRow(self.apply_btn)
        splitter.addWidget(right)

        return panel

    def _build_test_spectrum_panel(self) -> QtWidgets.QWidget:
        panel = QtWidgets.QWidget()
        vlayout = QtWidgets.QVBoxLayout(panel)
        self.layout_manager.apply_panel_layout(panel, vlayout)

        # Spectrum input and lightweight preprocessing controls
        spectrum_group = QtWidgets.QGroupBox("Test Spectrum")
        self.layout_manager.setup_group_box(spectrum_group)
        spectrum_vbox = QtWidgets.QVBoxLayout(spectrum_group)

        file_row = QtWidgets.QHBoxLayout()
        self.file_path_edit = QtWidgets.QLineEdit()
        self.file_path_edit.setPlaceholderText("Select a spectrum file…")
        browse_btn = self.layout_manager.create_action_button("Browse", "📁")
        browse_btn.clicked.connect(self._browse_spectrum_file)
        file_row.addWidget(self.file_path_edit)
        file_row.addWidget(browse_btn)
        spectrum_vbox.addLayout(file_row)

        preprocess_row = QtWidgets.QHBoxLayout()
        # Only expose Advanced Preprocessing in this GUI
        self.adv_pre_btn = self.layout_manager.create_action_button("Advanced Preprocessing", "🔧")
        self.adv_pre_btn.clicked.connect(self._open_preprocessing_dialog)
        preprocess_row.addWidget(self.adv_pre_btn)
        spectrum_vbox.addLayout(preprocess_row)

        info_label = QtWidgets.QLabel("This tool does not require log-rebinning, padding, or rescaling.")
        info_label.setStyleSheet("color: #64748b; font-style: italic;")
        spectrum_vbox.addWidget(info_label)

        vlayout.addWidget(spectrum_group)

        # Preview plot with in-range toggle
        preview_group = QtWidgets.QGroupBox("Spectrum Preview")
        self.layout_manager.setup_group_box(preview_group)
        preview_vbox = QtWidgets.QVBoxLayout(preview_group)
        if PYQTGRAPH_AVAILABLE:
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground('w')
            self.plot_item = self.plot_widget.getPlotItem()
            self._spectrum_curve = self.plot_item.plot(pen=pg.mkPen('#444444', width=1))
            self._overlay_lines_items: List[Any] = []
            preview_vbox.addWidget(self.plot_widget)
        else:
            self.plot_widget = None
            preview_vbox.addWidget(QtWidgets.QLabel("pyqtgraph not available. Install pyqtgraph to enable preview."))

        # In-range filter for overlays (separate from search)
        range_row = QtWidgets.QHBoxLayout()
        self.in_range_check = QtWidgets.QCheckBox("Show only lines within spectrum range")
        self.in_range_check.setToolTip("Overlay only lines within current spectrum wavelength range")
        self.in_range_check.toggled.connect(self._draw_line_overlays)
        range_row.addWidget(self.in_range_check)
        range_row.addStretch()
        preview_vbox.addLayout(range_row)

        vlayout.addWidget(preview_group)

        return panel

    def _on_table_selection(self) -> None:
        sel = self.line_table.currentRow()
        has = sel >= 0
        self.edit_btn.setEnabled(has)
        self.delete_btn.setEnabled(has)
        if has:
            entry = self._table_row_to_entry(sel)
            self._load_editor(entry)

    def _load_editor(self, entry: Dict[str, Any]) -> None:
        self.name_edit.setText(entry.get("key", ""))
        self.air_spin.setValue(float(entry.get("wavelength_air", 0.0) or 0.0))
        self.vac_spin.setValue(float(entry.get("wavelength_vacuum", 0.0) or 0.0))
        self.category_combo.setCurrentText(entry.get("category", ""))
        self.origin_combo.setCurrentText(entry.get("origin", "sn"))
        self.sn_types_edit.setText(
            ",".join(entry.get("sn_types", []) or [])
        )
        self.note_edit.setText(entry.get("note", ""))

    def _apply_editor_changes(self) -> None:
        entry = {
            "key": self.name_edit.text().strip(),
            "wavelength_air": self.air_spin.value(),
            "wavelength_vacuum": self.vac_spin.value(),
            "category": self.category_combo.currentText(),
            "origin": self.origin_combo.currentText(),
            "sn_types": [s.strip() for s in self.sn_types_edit.text().split(",") if s.strip()],
            "note": self.note_edit.text().strip(),
        }
        if not entry["key"]:
            QtWidgets.QMessageBox.warning(self, "Missing name", "Please provide a line name.")
            return
        if add_or_update_user_line(entry):
            self._user_lines = load_user_lines()
            self._refresh_line_table()
            self._update_counts()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to save changes.")

    def _add_line(self) -> None:
        # Clear editor for new entry
        self.name_edit.clear()
        self.air_spin.setValue(0.0)
        self.vac_spin.setValue(0.0)
        self.category_combo.setCurrentIndex(0)
        self.origin_combo.setCurrentIndex(0)
        self.sn_types_edit.clear()
        self.note_edit.clear()
        self.name_edit.setFocus()

    def _edit_selected_line(self) -> None:
        row = self.line_table.currentRow()
        if row < 0:
            return
        entry = self._table_row_to_entry(row)
        self._load_editor(entry)

    def _delete_selected_line(self) -> None:
        row = self.line_table.currentRow()
        if row < 0:
            return
        key = self.line_table.item(row, 0).text()
        if QtWidgets.QMessageBox.question(self, "Delete", f"Delete '{key}'?") == QtWidgets.QMessageBox.Yes:
            if delete_user_line(key):
                self._user_lines = load_user_lines()
                self._refresh_line_table()
                self._update_counts()

    def _save_user_lines(self) -> None:
        if save_user_lines(self._user_lines):
            QtWidgets.QMessageBox.information(self, "Saved", "User lines saved.")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to save user lines.")

    # Spectrum loading and preprocessing
    def _browse_spectrum_file(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Spectrum File",
            "",
            "All Supported (*.txt *.dat *.ascii *.asci *.lnw *.fits *.flm);;Text Files (*.txt *.dat *.ascii *.asci *.flm);;SNID Files (*.lnw);;FITS Files (*.fits);;FLM Files (*.flm);;All Files (*.*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)

    def _open_preprocessing_dialog(self) -> None:
        try:
            from snid_sage.interfaces.gui.components.pyside6_dialogs.preprocessing_dialog import (
                PySide6PreprocessingDialog,
            )
        except Exception:
            QtWidgets.QMessageBox.warning(
                self,
                "Unavailable",
                "Advanced preprocessing dialog is not available in this environment."
            )
            return

        spectrum_file = self.file_path_edit.text()
        if not spectrum_file or not os.path.exists(spectrum_file):
            QtWidgets.QMessageBox.warning(self, "No Spectrum", "Please select a valid spectrum file first.")
            return

        try:
            wave, flux = self._load_spectrum(spectrum_file)
            dialog = PySide6PreprocessingDialog(self, (wave, flux))
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                self.current_spectrum = dialog.result
                QtWidgets.QMessageBox.information(self, "Success", "Preprocessing completed and stored.")
                self._update_plot()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error in preprocessing: {e}")

    def _run_quick_preprocessing(self) -> None:
        try:
            from snid_sage.snid.snid import preprocess_spectrum
        except Exception:
            QtWidgets.QMessageBox.warning(
                self,
                "Unavailable",
                "Quick preprocessing requires SNID core components."
            )
            return

        spectrum_file = self.file_path_edit.text()
        if not spectrum_file or not os.path.exists(spectrum_file):
            QtWidgets.QMessageBox.warning(self, "No Spectrum", "Please select a valid spectrum file first.")
            return

        try:
            # Run with heavy steps skipped: no log rebinning, rescaling, or apodization
            processed_spectrum, _trace = preprocess_spectrum(
                spectrum_path=spectrum_file,
                skip_steps=[
                    'log_rebinning',
                    'flux_scaling',
                    'apodization',
                    'continuum_fitting'
                ],
                verbose=False,
            )
            # Prefer raw input spectrum for plotting in this tool
            input_spec = processed_spectrum.get('input_spectrum', {})
            wave = np.asarray(input_spec.get('wave')) if input_spec else None
            flux = np.asarray(input_spec.get('flux')) if input_spec else None
            if wave is not None and flux is not None:
                self.current_spectrum = {'wave': wave, 'flux': flux}
            else:
                # Fallback to any available keys
                self.current_spectrum = processed_spectrum
            QtWidgets.QMessageBox.information(self, "Success", "Light preprocessing finished. Plot shows raw spectrum.")
            self._update_plot()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Quick preprocessing failed: {e}")

    def _load_spectrum(self, file_path: str) -> Tuple[np.ndarray, np.ndarray]:
        if file_path.lower().endswith('.fits'):
            return self._load_fits_spectrum(file_path)
        if file_path.lower().endswith('.lnw'):
            return self._load_lnw_spectrum(file_path)
        if file_path.lower().endswith('.flm'):
            return self._load_ascii_spectrum(file_path)  # FLM files are text-based
        return self._load_ascii_spectrum(file_path)

    def _load_fits_spectrum(self, file_path: str) -> Tuple[np.ndarray, np.ndarray]:
        from astropy.io import fits  # type: ignore
        with fits.open(file_path) as hdul:
            for hdu in hdul:
                if hdu.data is not None:
                    data = hdu.data
                    if getattr(data, 'ndim', 0) == 1:
                        flux = data
                        wave = np.arange(len(flux)) + 1
                        return wave, flux
                    if getattr(data, 'ndim', 0) >= 2:
                        wave = data[:, 0]
                        flux = data[:, 1]
                        return wave, flux
        raise ValueError("FITS spectrum not found in file")

    def _load_lnw_spectrum(self, file_path: str) -> Tuple[np.ndarray, np.ndarray]:
        try:
            from snid_sage.snid.io import read_template
            template = read_template(file_path)
            return template['wave'], template['flux']
        except Exception:
            return self._load_ascii_spectrum(file_path)

    def _load_ascii_spectrum(self, file_path: str) -> Tuple[np.ndarray, np.ndarray]:
        data = np.loadtxt(file_path)
        if data.ndim == 1:
            flux = data
            wave = np.arange(len(flux)) + 1
            return wave, flux
        wave = data[:, 0]
        flux = data[:, 1]
        return wave, flux

    def _table_row_to_entry(self, row: int) -> Dict[str, Any]:
        return {
            "key": self.line_table.item(row, 0).text(),
            "wavelength_air": float(self.line_table.item(row, 1).text() or 0.0),
            "wavelength_vacuum": float(self.line_table.item(row, 2).text() or 0.0),
            "category": self.line_table.item(row, 3).text(),
            "origin": self.line_table.item(row, 4).text(),
            "sn_types": [s.strip() for s in self.line_table.item(row, 5).text().split(",") if s.strip()],
        }

    def _refresh_tables(self) -> None:
        self._refresh_line_table()
        self._refresh_presets()

    def _refresh_line_table(self) -> None:
        effective = get_effective_line_db()
        query = self.search_edit.text().strip().lower() if hasattr(self, "search_edit") else ""
        # Show merged list, but highlight user entries visually
        self.line_table.setRowCount(0)
        user_keys = {d.get("key") for d in self._user_lines}
        for entry in effective:
            name = entry.get("key", "")
            if query and (query not in name.lower() and query not in entry.get("category", "").lower() and query not in entry.get("origin", "").lower()):
                continue
            row = self.line_table.rowCount()
            self.line_table.insertRow(row)
            vals = [
                name,
                f"{float(entry.get('wavelength_air', 0.0) or 0.0):.2f}",
                f"{float(entry.get('wavelength_vacuum', 0.0) or 0.0):.2f}",
                entry.get("category", ""),
                entry.get("origin", ""),
                ",".join(entry.get("sn_types", []) or []),
            ]
            for col, val in enumerate(vals):
                item = QtWidgets.QTableWidgetItem(val)
                if name in user_keys:
                    # Bold user-defined entries
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.line_table.setItem(row, col, item)
        self.line_table.resizeColumnsToContents()
        self._update_counts()

    def _update_counts(self) -> None:
        self.count_label.setText(f"User lines: {len(self._user_lines)}  |  Total effective: {len(get_effective_line_db())}")

    # --- Presets Tab ---
    def _build_presets_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(w)
        self.layout_manager.apply_panel_layout(w, layout)

        # Preset list
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        self.layout_manager.apply_panel_layout(left, left_layout)
        self.preset_list = QtWidgets.QListWidget()
        left_layout.addWidget(self.preset_list)
        btns = QtWidgets.QHBoxLayout()
        self.add_preset_btn = QtWidgets.QPushButton("Add Preset")
        self.del_preset_btn = QtWidgets.QPushButton("Delete")
        self.add_preset_btn.clicked.connect(self._add_preset)
        self.del_preset_btn.clicked.connect(self._delete_preset)
        btns.addWidget(self.add_preset_btn)
        btns.addWidget(self.del_preset_btn)
        left_layout.addLayout(btns)
        layout.addWidget(left)

        # Preset editor
        right = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(right)
        self.layout_manager.setup_form_layout(form)
        self.preset_name_edit = QtWidgets.QLineEdit()
        self.preset_categories_edit = QtWidgets.QLineEdit()
        self.preset_origins_edit = QtWidgets.QLineEdit()
        self.preset_sn_types_edit = QtWidgets.QLineEdit()
        self.preset_strength_edit = QtWidgets.QLineEdit()
        self.preset_phase_edit = QtWidgets.QLineEdit()
        self.preset_name_patterns_edit = QtWidgets.QLineEdit()
        form.addRow("Name:", self.preset_name_edit)
        form.addRow("Categories (comma):", self.preset_categories_edit)
        form.addRow("Origins (comma):", self.preset_origins_edit)
        form.addRow("SN Types (comma):", self.preset_sn_types_edit)
        form.addRow("Strength (comma):", self.preset_strength_edit)
        form.addRow("Phase (comma):", self.preset_phase_edit)
        form.addRow("Name patterns (comma):", self.preset_name_patterns_edit)
        self.save_preset_btn = QtWidgets.QPushButton("Save Preset")
        self.save_preset_btn.clicked.connect(self._save_current_preset)
        form.addRow(self.save_preset_btn)
        layout.addWidget(right)

        self.preset_list.itemSelectionChanged.connect(self._load_selected_preset)
        return w

    def _refresh_presets(self) -> None:
        self.preset_list.clear()
        for name in sorted(self._user_presets.keys()):
            self.preset_list.addItem(name)

    def _add_preset(self) -> None:
        self.preset_list.clearSelection()
        self.preset_name_edit.clear()
        self.preset_categories_edit.clear()
        self.preset_origins_edit.clear()
        self.preset_sn_types_edit.clear()
        self.preset_strength_edit.clear()
        self.preset_phase_edit.clear()
        self.preset_name_patterns_edit.clear()
        self.preset_name_edit.setFocus()

    def _delete_preset(self) -> None:
        items = self.preset_list.selectedItems()
        if not items:
            return
        name = items[0].text()
        if QtWidgets.QMessageBox.question(self, "Delete preset", f"Delete '{name}'?") == QtWidgets.QMessageBox.Yes:
            self._user_presets.pop(name, None)
            save_user_presets({"presets": self._user_presets})
            self._refresh_presets()

    def _load_selected_preset(self) -> None:
        items = self.preset_list.selectedItems()
        if not items:
            return
        name = items[0].text()
        data = self._user_presets.get(name, {})
        crit = data.get("criteria", {})
        self.preset_name_edit.setText(name)
        self.preset_categories_edit.setText(
            ",".join(crit.get("category", []) or [])
        )
        self.preset_origins_edit.setText(
            ",".join(crit.get("origin", []) or [])
        )
        self.preset_sn_types_edit.setText(
            ",".join(crit.get("sn_types", []) or [])
        )
        self.preset_strength_edit.setText(
            ",".join(crit.get("strength", []) or [])
        )
        self.preset_phase_edit.setText(
            ",".join(crit.get("phase", []) or [])
        )
        self.preset_name_patterns_edit.setText(
            ",".join(crit.get("name_patterns", []) or [])
        )

    def _save_current_preset(self) -> None:
        name = self.preset_name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self, "Missing name", "Preset name is required.")
            return
        crit = {
            "category": _split_csv(self.preset_categories_edit.text()),
            "origin": _split_csv(self.preset_origins_edit.text()),
            "sn_types": _split_csv(self.preset_sn_types_edit.text()),
            "strength": _split_csv(self.preset_strength_edit.text()),
            "phase": _split_csv(self.preset_phase_edit.text()),
            "name_patterns": _split_csv(self.preset_name_patterns_edit.text()),
        }
        self._user_presets[name] = {"criteria": crit, "lines": []}
        save_user_presets({"presets": self._user_presets})
        self._refresh_presets()

    # --- Plot helpers ---
    def _update_plot(self) -> None:
        if not PYQTGRAPH_AVAILABLE or self.plot_widget is None:
            return
        # Update spectrum curve
        wave, flux = self._extract_wave_flux(self.current_spectrum)
        if wave is not None and flux is not None and len(wave) > 0:
            self._spectrum_curve.setData(wave, flux)
            self.plot_item.setLabel('bottom', 'Wavelength', units='Å')
            self.plot_item.setLabel('left', 'Flux')
        # Update overlays
        self._draw_line_overlays()

    def _extract_wave_flux(self, spectrum: Optional[Dict[str, Any]]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        if not spectrum:
            return None, None
        # Prefer original input if present, else common keys
        if 'input_spectrum' in spectrum and isinstance(spectrum['input_spectrum'], dict):
            wave = spectrum['input_spectrum'].get('wave')
            flux = spectrum['input_spectrum'].get('flux')
        else:
            wave = spectrum.get('wave') or spectrum.get('wavelength')
            flux = spectrum.get('flux') or spectrum.get('flat') or spectrum.get('fluxed')
        try:
            wave_arr = np.asarray(wave) if wave is not None else None
            flux_arr = np.asarray(flux) if flux is not None else None
            return wave_arr, flux_arr
        except Exception:
            return None, None

    def _get_wave_range(self) -> Tuple[Optional[float], Optional[float]]:
        wave, _ = self._extract_wave_flux(self.current_spectrum)
        if wave is None or len(wave) == 0:
            return None, None
        return float(np.nanmin(wave)), float(np.nanmax(wave))

    def _draw_line_overlays(self) -> None:
        if not PYQTGRAPH_AVAILABLE or self.plot_widget is None:
            return
        # Clear existing lines
        for item in getattr(self, '_overlay_lines_items', []) or []:
            try:
                self.plot_item.removeItem(item)
            except Exception:
                pass
        self._overlay_lines_items = []

        # Determine range filter
        min_w, max_w = self._get_wave_range()
        in_range_only = getattr(self, 'in_range_check', None).isChecked() if hasattr(self, 'in_range_check') else False

        # Build overlays
        user_keys = {d.get("key") for d in self._user_lines}
        selected_keys = set()
        for idx in self.line_table.selectionModel().selectedRows():
            selected_keys.add(self.line_table.item(idx.row(), 0).text())

        for entry in get_effective_line_db():
            name = entry.get('key', '')
            air = float(entry.get('wavelength_air', 0.0) or 0.0)
            if air <= 0:
                continue
            if in_range_only and (min_w is not None and max_w is not None):
                if not (min_w <= air <= max_w):
                    continue
            color = CATEGORY_COLORS.get(entry.get('category', ''), '#888888')
            width = 1.0
            alpha = 120
            if name in user_keys:
                width = 1.5
            if name in selected_keys:
                width = 2.5
                alpha = 200
            pen = pg.mkPen(QtGui.QColor(QtGui.QColor(color).red(), QtGui.QColor(color).green(), QtGui.QColor(color).blue(), alpha), width=width)
            inf_line = pg.InfiniteLine(pos=air, angle=90, pen=pen)
            self.plot_item.addItem(inf_line)
            self._overlay_lines_items.append(inf_line)
        # Update status
        self._update_status_with_range()

    def _update_status_with_range(self) -> None:
        min_w, max_w = self._get_wave_range()
        if min_w is None or max_w is None:
            self.count_label.setText(f"User lines: {len(self._user_lines)}  |  Total effective: {len(get_effective_line_db())}")
        else:
            self.count_label.setText(
                f"User lines: {len(self._user_lines)}  |  Total effective: {len(get_effective_line_db())}  |  Range: {min_w:.0f}–{max_w:.0f} Å"
            )


def _split_csv(text: str) -> List[str]:
    return [s.strip() for s in text.split(",") if s.strip()]


def _category_list() -> List[str]:
    from snid_sage.shared.constants.physical import SN_LINE_CATEGORIES
    return list(SN_LINE_CATEGORIES.keys())


