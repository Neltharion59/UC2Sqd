from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QDialog,  \
    QScrollArea

class DiagramWindow(QDialog):
    def __init__(self):
        super(DiagramWindow, self).__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Diagram window')
        self.resize(1080, 1080)
        self.option = ''
        self.show()

    def show_diagram(self):

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.image_label = QLabel(self)
        self.load_image("output.png")
        self.labelDiagramOutput = QLabel("Diagram output:", self)
        self.labelDiagramOutput.setFont(QFont("Arial", 13, QFont.Bold))
        self.labelDiagramOutput.setStyleSheet("color: blue; background-color: lightgray")

        self.button_close = QPushButton("Close window", self)
        self.button_close.clicked.connect(self.closeWindow)
        self.button_close.setFont(QFont("Arial", 13, QFont.Bold))
        self.button_close.setStyleSheet("background: red; color:white;")
        self.layout.addWidget(self.scroll_area)
        self.scroll_area.setWidget(self.image_label)
        self.layout.addWidget(self.button_close)


        self.show()

    def load_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)

    def closeEvent(self, event):
        event.ignore()

    def closeWindow(self,state):
        self.destroy()
