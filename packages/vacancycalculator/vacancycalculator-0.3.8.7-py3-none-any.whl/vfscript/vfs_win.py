import sys
import io
import json
import contextlib
import traceback
from pathlib import Path
import shutil
import os

# Forzar backend XCB en Wayland
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QCheckBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QHBoxLayout, QPlainTextEdit, QVBoxLayout,
    QProgressBar, QSizePolicy, QComboBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QLabel
)
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np
from ovito.io import import_file
from ovito.modifiers import ConstructSurfaceModifier
from vfscript import vfs
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


# ---------- Gestión de input_params.json ----------
GUI_ROOT = Path(__file__).resolve().parent

def runtime_params_path():
    cwd_params = Path.cwd() / "input_params.json"
    if cwd_params.exists():
        return cwd_params
    src_params = GUI_ROOT / "input_params.json"
    if src_params.exists():
        shutil.copy(src_params, cwd_params)
        return cwd_params
    return src_params

PARAMS_FILE = runtime_params_path()

def load_params():
    if PARAMS_FILE.exists():
        return json.loads(PARAMS_FILE.read_text())
    return {}

def save_params(params, target_path: Path = None):
    if target_path is None:
        target_path = Path.cwd() / "input_params.json"
    target_path.write_text(json.dumps(params, indent=4))
    return target_path


# ---------- Función común de render (3D+2D) ----------
def render_dump_to(plotter: QtInteractor, fig: plt.Figure, dump_path: str):
    """Dibuja celda + puntos igual que load_dump, usando OVITO."""
    pipeline = import_file(dump_path)
    data = pipeline.compute()

    # Matriz de celda: columnas a1,a2,a3 y última columna origen
    M = np.asarray(data.cell.matrix, dtype=float)   # (3x4)
    a1 = M[:, 0]; a2 = M[:, 1]; a3 = M[:, 2]; origin = M[:, 3]

    corners = [
        origin,
        origin + a1,
        origin + a2,
        origin + a3,
        origin + a1 + a2,
        origin + a1 + a3,
        origin + a2 + a3,
        origin + a1 + a2 + a3
    ]
    edges = [(0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,5),(3,6),(4,7),(5,7),(6,7)]

    pos_prop = data.particles.positions
    positions = pos_prop.array if hasattr(pos_prop, "array") else np.asarray(pos_prop, dtype=float)

    # 3D
    plotter.clear()
    for i, j in edges:
        plotter.add_mesh(pv.Line(corners[i], corners[j]), color="blue", line_width=2)
    plotter.add_mesh(
        pv.PolyData(positions),
        color="black",
        render_points_as_spheres=True,
        point_size=8
    )
    plotter.reset_camera()
    plotter.set_scale(1, 1, 1)

    # 2D
    fig.clf()
    ax = fig.add_subplot(111)
    for i, j in edges:
        x0, y0 = corners[i][0], corners[i][1]
        x1, y1 = corners[j][0], corners[j][1]
        ax.plot([x0, x1], [y0, y1], '-', linewidth=1)
    ax.scatter(positions[:, 0], positions[:, 1], s=10)
    ax.set_xlabel('X'); ax.set_ylabel('Y')
    ax.set_aspect('equal', 'box')
    ax.grid(True, linewidth=0.3)
    fig.canvas.draw()


# ---------- Ventana genérica de visualización ----------
class DumpViewerWindow(QMainWindow):
    def __init__(self, title="Dump Viewer"):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(900, 700)

        # Barra superior con path + botones
        top = QWidget()
        top_l = QHBoxLayout(top)
        self.path_edit = QLineEdit()
        self.btn_browse = QPushButton("Browse")
        self.btn_load = QPushButton("Load")
        top_l.addWidget(QLabel("File:"))
        top_l.addWidget(self.path_edit, 1)
        top_l.addWidget(self.btn_browse)
        top_l.addWidget(self.btn_load)

        # Vista 3D + 2D
        center = QWidget()
        center_l = QVBoxLayout(center)
        self.plotter = QtInteractor(center)
        center_l.addWidget(self.plotter)
        self.fig = plt.figure(figsize=(4, 4))
        self.canvas = FigureCanvas(self.fig)
        center_l.addWidget(self.canvas)

        root = QWidget()
        root_l = QVBoxLayout(root)
        root_l.addWidget(top)
        root_l.addWidget(center, 1)
        self.setCentralWidget(root)

        self.btn_browse.clicked.connect(self._browse)
        self.btn_load.clicked.connect(self._load_clicked)

    def _browse(self):
        filtros = "All Files (*);;Dump Files (*.dump)"
        start_dir = getattr(self, "_last_dir", str(Path.cwd()))
        abs_path, _ = QFileDialog.getOpenFileName(self, "Select File", start_dir, filtros)
        if abs_path:
            self._last_dir = str(Path(abs_path).parent)
            self.path_edit.setText(abs_path)

    def _load_clicked(self):
        p = self.path_edit.text().strip()
        if not p:
            QMessageBox.warning(self, "Sin archivo", "Seleccione un archivo primero.")
            return
        try:
            render_dump_to(self.plotter, self.fig, p)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def render_dump(self, p: str):
        self.path_edit.setText(p)
        render_dump_to(self.plotter, self.fig, p)


# ---------- Ventana específica para key_area_{i}.dump ----------
class KeyAreaSeqViewer(QMainWindow):
    def __init__(self, title="Key Area Viewer", pattern: str = "outputs/dump/key_area_{i}.dump"):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(900, 700)
        self.pattern = pattern

        # Barra superior con controles de índice
        top = QWidget()
        top_l = QHBoxLayout(top)
        self.lbl = QLabel("Archivo:")
        self.idx = QSpinBox()
        self.idx.setRange(0, 1_000_000)  # amplio
        self.btn_prev = QPushButton("◀ Prev")
        self.btn_next = QPushButton("Next ▶")
        self.btn_load = QPushButton("Load")
        self.path_lbl = QLineEdit()
        self.path_lbl.setReadOnly(True)
        top_l.addWidget(QLabel("key_area_{i}.dump   i="))
        top_l.addWidget(self.idx)
        top_l.addWidget(self.btn_prev)
        top_l.addWidget(self.btn_next)
        top_l.addWidget(self.btn_load)
        top_l.addWidget(self.lbl)
        top_l.addWidget(self.path_lbl, 1)

        # Vista 3D + 2D
        center = QWidget()
        center_l = QVBoxLayout(center)
        self.plotter = QtInteractor(center)
        center_l.addWidget(self.plotter)
        self.fig = plt.figure(figsize=(4, 4))
        self.canvas = FigureCanvas(self.fig)
        center_l.addWidget(self.canvas)

        root = QWidget()
        root_l = QVBoxLayout(root)
        root_l.addWidget(top)
        root_l.addWidget(center, 1)
        self.setCentralWidget(root)

        # Conexiones
        self.btn_prev.clicked.connect(lambda: self._step(-1))
        self.btn_next.clicked.connect(lambda: self._step(+1))
        self.btn_load.clicked.connect(self._load_idx)

        # Autodetectar un i válido si existe
        self._auto_seed_index()

    def _pattern_path(self, i: int) -> str:
        return self.pattern.format(i=i)

    def _auto_seed_index(self):
        # Busca el primer i que exista (0..9999)
        for i in range(0, 10000):
            if Path(self._pattern_path(i)).exists():
                self.idx.setValue(i)
                self._load_idx()
                return
        # Si no hay ninguno, solo deja en 0 y limpia
        self.path_lbl.setText("(no encontrado)")

    def _step(self, delta: int):
        new_i = max(0, self.idx.value() + delta)
        self.idx.setValue(new_i)
        self._load_idx()

    def _load_idx(self):
        p = self._pattern_path(self.idx.value())
        self.path_lbl.setText(p)
        if not Path(p).exists():
            QMessageBox.warning(self, "No existe", f"No se encontró:\n{p}")
            return
        try:
            render_dump_to(self.plotter, self.fig, p)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ---------- Ventana principal ----------
class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()
        self.setWindowTitle("VacancyFinder-SiMAF   0.3.7.9")

        self.params = load_params()
        cfg = self.params.setdefault('CONFIG', [{}])[0]

        form_layout = QFormLayout()

        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        form_layout.addRow("Progreso:", self.progress)

        # Log de salida (grande)
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(200)
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_layout.addRow("Output Log:", self.log_output)

        # Checkboxes
        self.check_training = QCheckBox(); self.check_training.setChecked(cfg.get('training', False))
        self.check_geometric = QCheckBox(); self.check_geometric.setChecked(cfg.get('geometric_method', False))
        self.check_activate_relax = QCheckBox(); self.check_activate_relax.setChecked(cfg.get('activate_generate_relax', False))
        form_layout.addRow("Enable Training:", self.check_training)
        form_layout.addRow("Geometric Method:", self.check_geometric)
        form_layout.addRow("Activate Generate Relax:", self.check_activate_relax)

        # generate_relax
        gr = cfg.get('generate_relax', ["bcc", 1.0]) + [1, 1, 1, "Fe"]
        self.edit_lattice = QLineEdit(gr[0])
        self.spin_lattice_a = QDoubleSpinBox()
        self._configure_spin(self.spin_lattice_a, 0.0, 100.0, float(gr[1]), step=0.1, decimals=3)
        self.spin_rx = QSpinBox(); self._configure_spin(self.spin_rx, 1, 100, gr[2], step=1)
        self.spin_ry = QSpinBox(); self._configure_spin(self.spin_ry, 1, 100, gr[3], step=1)
        self.spin_rz = QSpinBox(); self._configure_spin(self.spin_rz, 1, 100, gr[4], step=1)
        self.edit_atom = QLineEdit(gr[5])

        form_layout.addRow("Lattice Type:", self.edit_lattice)
        form_layout.addRow("Lattice Param a:", self.spin_lattice_a)
        form_layout.addRow("Replicas X:", self.spin_rx)
        form_layout.addRow("Replicas Y:", self.spin_ry)
        form_layout.addRow("Replicas Z:", self.spin_rz)
        form_layout.addRow("Atom Type:", self.edit_atom)

        # Selectores de dump
        self.edit_relax = QLineEdit(cfg.get('relax', ''))
        btn_relax = QPushButton("Browse Relax")
        btn_relax.clicked.connect(lambda: self.browse_file(self.edit_relax))
        relax_layout = QHBoxLayout(); relax_layout.addWidget(self.edit_relax); relax_layout.addWidget(btn_relax)
        form_layout.addRow("Relax Dump:", self._wrap(relax_layout))

        self.edit_defect = QLineEdit(cfg.get('defect', [''])[0])
        btn_defect = QPushButton("Browse Defect")
        btn_defect.clicked.connect(lambda: self.browse_file(self.edit_defect))
        defect_layout = QHBoxLayout(); defect_layout.addWidget(self.edit_defect); defect_layout.addWidget(btn_defect)
        form_layout.addRow("Defect Dump:", self._wrap(defect_layout))

        # CSV
        self.csv_combo = QComboBox(); self.csv_combo.setEditable(True)
        self._refresh_csv_list()
        form_layout.addRow("Resultados CSV:", self.csv_combo)
        btn_csv = QPushButton("Cargar CSV"); btn_csv.clicked.connect(self.load_csv_results)
        form_layout.addRow(btn_csv)

        # Campos numéricos
        fields = [
            ("radius", QDoubleSpinBox, 0, 100, cfg.get('radius', 0.0), 3),
            ("cutoff", QDoubleSpinBox, 0, 100, cfg.get('cutoff', 0.0), 3),
            ("max_graph_size", QSpinBox, 0, 10000, cfg.get('max_graph_size', 0), 0),
            ("max_graph_variations", QSpinBox, 0, 10000, cfg.get('max_graph_variations', 0), 0),
            ("radius_training", QDoubleSpinBox, 0, 100, cfg.get('radius_training', 0.0), 3),
            ("training_file_index", QSpinBox, 0, 10000, cfg.get('training_file_index', 0), 0),
            ("cluster tolerance", QDoubleSpinBox, 0, 100, cfg.get('cluster tolerance', 0.0), 3),
            ("divisions_of_cluster", QSpinBox, 0, 10000, cfg.get('divisions_of_cluster', 0), 0),
            ("iteraciones_clusterig", QSpinBox, 0, 10000, cfg.get('iteraciones_clusterig', 0), 0),
        ]
        for name, cls, mn, mx, val, dec in fields:
            widget = cls()
            step = 0.1 if cls is QDoubleSpinBox else 1
            decimals = dec if cls is QDoubleSpinBox else None
            self._configure_spin(widget, mn, mx, val, step=step, decimals=decimals)
            setattr(self, f"spin_{name}".replace(' ', '_'), widget)
            form_layout.addRow(f"{name.replace('_',' ').title()}:", widget)

        # Botones
        btn_save = QPushButton("Save Settings"); btn_save.clicked.connect(self.save_settings_and_notify)
        btn_run = QPushButton("Run VacancyAnalysis"); btn_run.clicked.connect(self.run_vacancy_analysis)
        hb = QHBoxLayout(); hb.addWidget(btn_save); hb.addWidget(btn_run)
        form_layout.addRow(hb)

        # Panel izquierdo (controles)
        controls_widget = QWidget(); controls_widget.setLayout(form_layout)
        controls_widget.setFixedWidth(int(320 * 1.3))
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(controls_widget)

        # Panel derecho (vista 3D+2D principal)
        viewer_widget = QWidget(); viewer_layout = QVBoxLayout(viewer_widget)
        self.plotter = QtInteractor(viewer_widget); viewer_layout.addWidget(self.plotter)
        self.fig = plt.figure(figsize=(4, 4)); self.canvas = FigureCanvas(self.fig); viewer_layout.addWidget(self.canvas)
        self.table = QTableWidget(); viewer_layout.addWidget(self.table)

        main = QWidget(); hl = QHBoxLayout(main); hl.addWidget(scroll); hl.addWidget(viewer_widget, 1)
        self.setCentralWidget(main)

        # Ventanas externas (2 más)
        self.viewer1 = DumpViewerWindow("Viewer 1")
        self.viewer1.show()
        self.viewer2 = KeyAreaSeqViewer("Viewer 2 - key_area_{i}")
        self.viewer2.show()

        # Carga inicial
        dump_path = Path.cwd() / 'outputs' / 'dump' / 'key_areas.dump'
        if dump_path.exists():
            self.load_dump(str(dump_path))
            # Reflejar también en Viewer 1
            try:
                self.viewer1.render_dump(str(dump_path))
            except Exception:
                pass

    # Utils UI
    def _wrap(self, layout: QHBoxLayout) -> QWidget:
        w = QWidget(); w.setLayout(layout); return w

    def _configure_spin(self, spin, mn, mx, val, step=None, decimals=None):
        spin.setRange(mn, mx)
        if isinstance(spin, QDoubleSpinBox):
            if decimals is not None:
                spin.setDecimals(decimals)
            spin.setSingleStep(step if step is not None else 0.1)
        else:
            spin.setSingleStep(step if step is not None else 1)
        spin.setValue(val)

    def save_settings_and_notify(self):
        saved_path = self.save_settings()
        QMessageBox.information(self, "Settings Saved", f"Parameters saved to:\n{saved_path}")

    def save_settings(self):
        cfg = self.params['CONFIG'][0]
        cfg['training'] = self.check_training.isChecked()
        cfg['geometric_method'] = self.check_geometric.isChecked()
        cfg['activate_generate_relax'] = self.check_activate_relax.isChecked()
        cfg['generate_relax'] = [
            self.edit_lattice.text(),
            float(self.spin_lattice_a.value()),
            self.spin_rx.value(), self.spin_ry.value(), self.spin_rz.value(),
            self.edit_atom.text().strip() or 'Fe'
        ]
        cfg['relax'] = self.edit_relax.text()
        cfg['defect'] = [self.edit_defect.text()]
        for key in ['radius', 'cutoff', 'max_graph_size', 'max_graph_variations',
                    'radius_training', 'training_file_index', 'cluster tolerance',
                    'divisions_of_cluster', 'iteraciones_clusterig']:
            widget = getattr(self, f"spin_{key}".replace(' ', '_'))
            cfg[key] = widget.value()
        return save_params(self.params)

    def _refresh_csv_list(self):
        csv_dir = Path.cwd() / 'outputs' / 'csv'
        self.csv_combo.clear()
        if csv_dir.exists():
            for f in sorted(csv_dir.glob('*.csv')):
                self.csv_combo.addItem(f.name)

    def load_csv_results(self):
        nombre = self.csv_combo.currentText()
        if not nombre:
            QMessageBox.warning(self, "Sin selección", "No has elegido ningún CSV.")
            return
        ruta = Path.cwd() / 'outputs' / 'csv' / nombre
        try:
            df = pd.read_csv(ruta)
        except Exception as e:
            QMessageBox.critical(self, "Error al leer CSV", str(e))
            return
        self.table.clear()
        self.table.setColumnCount(len(df.columns))
        self.table.setRowCount(len(df))
        self.table.setHorizontalHeaderLabels(df.columns.tolist())
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                self.table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
        self.table.resizeColumnsToContents()

    def browse_file(self, line_edit):
        filtros = "All Files (*);;Dump Files (*.dump)"
        start_dir = getattr(self, "_last_dir", str(Path.cwd()))
        abs_path, _ = QFileDialog.getOpenFileName(self, "Select File", start_dir, filtros)
        if abs_path:
            self._last_dir = str(Path(abs_path).parent)
            try:
                line_edit.setText(Path(abs_path).relative_to(GUI_ROOT).as_posix())
            except ValueError:
                line_edit.setText(abs_path)

    # --- Visual principal (misma lógica que viewers externos) ---
    def load_dump(self, dump_path):
        self.progress.setValue(0)
        try:
            render_dump_to(self.plotter, self.fig, dump_path)
            self.canvas.draw()
            self.progress.setValue(100)
        except Exception as e:
            self.progress.setValue(0)
            QMessageBox.critical(self, "Error al cargar dump", str(e))

    # --- Run del análisis ---
    def run_vacancy_analysis(self):
        self.log_output.clear()
        buf = io.StringIO()
        self.progress.setRange(0, 0)
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                vfs.VacancyAnalysis()
            self.progress.setRange(0, 100)
            self.progress.setValue(100)
            self.log_output.setPlainText(buf.getvalue())
            QMessageBox.information(self, "Análisis completado", "VacancyAnalysis terminó correctamente.")
            self._refresh_csv_list()
            dump_path = Path.cwd() / 'outputs' / 'dump' / 'key_areas.dump'
            if dump_path.exists():
                self.load_dump(str(dump_path))
                # Reflejar también en Viewer 1 tras el análisis
                try:
                    self.viewer1.render_dump(str(dump_path))
                except Exception:
                    pass
        except Exception:
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            buf.write(traceback.format_exc())
            self.log_output.setPlainText(buf.getvalue())
            QMessageBox.critical(self, "Error en análisis", "Falló VacancyAnalysis. Revisa el log.")


def main():
    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
