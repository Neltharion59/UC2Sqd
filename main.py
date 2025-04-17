import sys

import nltk
import stanza
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow

stanza.install_corenlp()
nltk.download('wordnet')

app = QApplication(sys.argv)
MainWindow = MainWindow()
MainWindow.show()
sys.exit(app.exec_())

