# petrinet_app.py
from PySide6.QtWidgets import QGraphicsView, QMainWindow, QToolBar, QSplitter, QTextEdit, QWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import QPainter, QAction, QFontDatabase
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStatusBar
from reachability_graph import ReachabilityGraphView
from petrinet_graph import PetrinetCanvas



class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setInteractive(True)

class View(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        file_menu = self.menuBar().addMenu("Datei")
        open_action = QAction("Dateiauswahl", self)
        open_action.triggered.connect(self.controller.open_file_dialog)
        file_menu.addAction(open_action)

        toolbar = QToolBar("Werkzeuge")
        self.addToolBar(toolbar)

        increase_mark = QAction("+1", self)
        increase_mark.triggered.connect(lambda: self.controller.add_token())

        decrease_mark = QAction("-1", self)
        decrease_mark.triggered.connect(lambda: self.controller.subtract_token())

        analyse_action = QAction("Analysis", self)
        analyse_action.triggered.connect(lambda: self.controller.analyse())

        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(lambda: self.controller.reset_reachability_graph())

        toolbar.addAction(analyse_action)
        toolbar.addAction(reset_action)
        toolbar.addAction(increase_mark)
        toolbar.addAction(decrease_mark)

        self.petri_canvas = PetrinetCanvas(controller=self.controller, parent=self)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.petri_canvas)

        self.reach_canvas = ReachabilityGraphView(controller=self.controller, parent=self)
        splitter.addWidget(self.reach_canvas)
        splitter.setSizes([400, 400])

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.text_area.setFont(font)

        text_container = QWidget()
        text_layout = QVBoxLayout()
        text_container.setLayout(text_layout)

        text_layout.addWidget(self.text_area)

        clear_button = QPushButton("Clear Text")
        clear_button.clicked.connect(self.text_area.clear)
        text_layout.addWidget(clear_button)

        vsplitter = QSplitter(Qt.Vertical)
        vsplitter.addWidget(splitter)
        vsplitter.addWidget(text_container)
        vsplitter.setSizes([400, 200])

        self.setCentralWidget(vsplitter)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage(f"Aktuelle Datei: Keine Datei geladen")

        self.setWindowTitle("Petrinetz Demo")
        self.resize(800, 600)
        self.show()

    def fit_all(self):
        bounding_rect = self.petri_canvas.scene.itemsBoundingRect()
        self.petri_canvas.centerOn(bounding_rect.center())
        padding = 50
        self.petri_canvas.scene.setSceneRect(
            bounding_rect.x() - padding,
            bounding_rect.y() - padding,
            bounding_rect.width() + 2 * padding,
            bounding_rect.height() + 2 * padding
        )