import sys
from json import loads

import nltk
import stanza
from PyQt5.QtWidgets import QApplication
from convert import pipe, default_config_params
from MainWindow import MainWindow
from in_and_out import provide_use_cases, collect_puml

stanza.install_corenlp()
nltk.download('wordnet')

with open('super_config.json', 'r', encoding='utf-8') as super_config_file:
    super_config = loads(super_config_file.read())

if super_config['app_mode'] == 'gui':
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
elif super_config['app_mode'] == 'cli':
    for file_name, use_case in provide_use_cases():
        puml_string, error_message = pipe(use_case, default_config_params)
        collect_puml(file_name, puml_string, error_message)
else:
    raise ValueError('Unknown app_mode.')

