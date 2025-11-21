from PySide6.QtWidgets import QApplication
from controller import PetriNetController

app = QApplication([])
app.setStyleSheet("""
                    QWidget {
                        background-color: white;
                        color: black;
                    }
                """)
controller = PetriNetController()
controller.view.show()
app.exec()