import sys
from PyQt6.QtWidgets import QApplication
from app.ARC_MVC.view.view import ObjectDBApp

def main():
    app = QApplication(sys.argv)
    view = ObjectDBApp()
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
