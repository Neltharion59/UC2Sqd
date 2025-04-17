from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QLabel, QVBoxLayout


class ErrorWindow(QMainWindow):
    def __init__(self):
        super(ErrorWindow, self).__init__()

        self.setWindowTitle("Error Window")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.button_ok = QPushButton("OK", self)
        self.button_ok.clicked.connect(self.closeWindow)

        self.label = QLabel('',self)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button_ok)


    def closeWindow(self):
        self.destroy()

    def error(self,text):
        self.label.setText(text)
        self.show()


    def closeEvent(self, event):
        event.ignore()