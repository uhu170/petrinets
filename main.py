from PySide6.QtWidgets import QApplication
from controller import PetriNetController
import sys

def main() -> None:
    """
    Main function to start the Petri net application.
    """
    app = QApplication(sys.argv)
    app.setStyleSheet("""
                        QWidget {
                            background-color: white;
                            color: black;
                        }
                    """)
    controller = PetriNetController()
    controller.view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()