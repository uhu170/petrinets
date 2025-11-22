# petrinet_app.py
from PySide6.QtWidgets import QGraphicsView, QMainWindow, QToolBar, QSplitter, QTextEdit, QWidget, QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QGraphicsScene
from PySide6.QtGui import QPainter, QAction, QFontDatabase
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStatusBar
from reachability_graph import ReachabilityGraphView
from petrinet_graph import PetrinetCanvas



class GraphicsView(QGraphicsView):
    """
    A custom QGraphicsView with antialiasing and scroll hand drag mode enabled.
    """
    def __init__(self, scene: QGraphicsScene, parent: QWidget | None = None) -> None:
        """
        Initialize the GraphicsView.

        Args:
            scene: The QGraphicsScene to display.
            parent: The parent widget.
        """
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setInteractive(True)

class View(QMainWindow):
    """
    The main window of the Petri net application.
    """
    def __init__(self, controller) -> None:
        """
        Initialize the View.

        Args:
            controller: The controller object managing the application.
        """
        super().__init__()
        self.controller = controller

        QApplication.setAttribute(Qt.AA_DontUseNativeMenuBar)
        file_menu = self.menuBar().addMenu("File")
        help_menu = self.menuBar().addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.controller.open_file_dialog)
        file_menu.addAction(open_action)

        toolbar = QToolBar("Tools")
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

        self.setWindowTitle("Petrinet Application - Mischa Kurth")
        self.resize(800, 600)
        self.show()

    def fit_all(self) -> None:
        """
        Fit the Petri net canvas to show all items.
        """
        bounding_rect = self.petri_canvas.scene.itemsBoundingRect()
        self.petri_canvas.centerOn(bounding_rect.center())
        padding = 50
        self.petri_canvas.scene.setSceneRect(
            bounding_rect.x() - padding,
            bounding_rect.y() - padding,
            bounding_rect.width() + 2 * padding,
            bounding_rect.height() + 2 * padding
        )

    def show_about_dialog(self) -> None:
        """
        Show the 'About' dialog.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("About")

        layout = QVBoxLayout(dialog)
        label = QLabel("petrinet application by Mischa Kurth\n\nversion 1.0\n\n11/2025")
        label.setWordWrap(True)
        layout.addWidget(label)

        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()