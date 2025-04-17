from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QCheckBox, QLabel, QVBoxLayout, QDialog


class StepWindow(QDialog):
    def __init__(self):
        super(StepWindow, self).__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Step window')
        self.resize(300, 300)
        self.option = ''
        self.quit = False
        self.show()

    def generate_options(self, sentence, pos_option, dp_option, oie_option, loop):
        self.loop = loop
        self.pos_option = pos_option
        self.dp_option = dp_option
        self.oie_option = oie_option
        self.sentence = QLabel(sentence, self)
        self.sentence.setFont(QFont("Arial", 12, QFont.Bold))
        self.sentence.setStyleSheet("color: blue; background-color: lightgray")
        self.pos_label = QLabel("Part of Speech", self)
        self.pos_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.pos_label.setStyleSheet("color: blue; background-color: lightgray")
        if len(pos_option['subjects']) == 0:
            self.pos_checkbox = QCheckBox('No subject was generated')
            self.pos_checkbox.setCheckable(False)
        elif len(pos_option['objects']) == 0:
            self.pos_checkbox = QCheckBox('No object was generated')
            self.pos_checkbox.setCheckable(False)
        elif len(pos_option['relations']) == 0:
            self.pos_checkbox = QCheckBox('No relation was generated')
            self.pos_checkbox.setCheckable(False)
        else:
            self.pos_checkbox = QCheckBox(
                pos_option['subjects'] + '-->' + pos_option['relations'] + '-->' + pos_option['objects'])

        self.dp_label = QLabel("Dependency parsing", self)
        self.dp_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.dp_label.setStyleSheet("color: blue; background-color: lightgray")
        if len(dp_option['subjects']) == 0:
            self.dp_checkbox = QCheckBox('No subject was generated')
            self.dp_checkbox.setCheckable(False)
        elif len(dp_option['objects']) == 0:
            self.dp_checkbox = QCheckBox('No object was generated')
            self.dp_checkbox.setCheckable(False)
        elif len(dp_option['relations']) == 0:
            self.dp_checkbox = QCheckBox('No relation was generated')
            self.dp_checkbox.setCheckable(False)
        else:
            self.dp_checkbox = QCheckBox(
                dp_option['subjects'] + '-->' + dp_option['relations'] + '-->' + dp_option['objects'])
        self.oie_label = QLabel("Open information extraction", self)
        self.oie_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.oie_label.setStyleSheet("color: blue; background-color: lightgray")
        if self.oie_option == 'NOT IMPLEMENTED IN SPACY':
            self.oie_checkbox = QCheckBox('NOT IMPLEMENTED IN SPACY')
            self.oie_checkbox.setCheckable(False)
        else:
            if len(oie_option['subjects']) == 0:
                self.oie_checkbox = QCheckBox('No subject was generated')
                self.oie_checkbox.setCheckable(False)
            elif len(oie_option['objects']) == 0:
                self.oie_checkbox = QCheckBox('No object was generated')
                self.oie_checkbox.setCheckable(False)
            elif len(oie_option['relations']) == 0:
                self.oie_checkbox = QCheckBox('No relation was generated')
                self.oie_checkbox.setCheckable(False)
            else:
                self.oie_checkbox = QCheckBox(
                    oie_option['subjects'] + '-->' + oie_option['relations'] + '-->' + oie_option['objects'])
        self.pos_checkbox.stateChanged.connect(self.pos)
        self.dp_checkbox.stateChanged.connect(self.dp)
        self.oie_checkbox.stateChanged.connect(self.oie)
        self.layout.addWidget(self.sentence)
        self.layout.addWidget(self.pos_label)
        self.layout.addWidget(self.pos_checkbox)
        self.layout.addWidget(self.dp_label)
        self.layout.addWidget(self.dp_checkbox)
        self.layout.addWidget(self.oie_label)
        self.layout.addWidget(self.oie_checkbox)
        self.button_close = QPushButton("Close window", self)
        self.button_close.clicked.connect(self.closeWindow)
        self.layout.addWidget(self.button_close)

        self.show()

    def pos(self):
        self.option = self.pos_option
        self.loop.quit()

    def oie(self):
        self.option = self.oie_option
        self.loop.quit()

    def dp(self):
        self.option = self.dp_option
        self.loop.quit()

    def closeEvent(self, event):
        event.ignore()

    def closeWindow(self, state):
        self.quit = True
        self.loop.quit()
