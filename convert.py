from PyQt5.QtCore import QTimer, QEventLoop
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QTextEdit, QCheckBox, QScrollArea
from nltk.corpus import wordnet as wn
from Configuration import Configuration
from ConversionPipeline import ConversionPipeline

default_config_params = {
    "text": "",
    "system": "system",
    "users": {},
    "project_dictionary": None,
    "enable_projects": False,
    "coreference": False,
    "steps": False,
    "engine": "stanza",
    "mode": "POS",
    "model": "en_core_web_lg",
    "fragments": False,
    "fragment_pattern": None,
    "parameters": False,
    "pattern": None
}


def pipe(use_case, config_params_json):
    is_running = True
    start = True
    i = 0
    exit = False
    original = []
    sp = use_case.lower().split('\n')
    config_params = Configuration.from_json(config_params_json)

    if config_params.mode == 'OIE' and config_params.engine == 'spacy':
        exit = True

        return '', 'Open information extraction is possible only with STANZA option.'

    num_of_present_fragments = 0
    num_of_started_fragments = 0
    num_of_ended_fragments = 0
    num_of_else_fragments = 0
    num_of_alt_fragments = 0
    while i < 50 and i < len(sp) and sp[i] != '':
        l = sp[i]
        i += 1
        if l.strip()[-1] != '.':
            exit = True
            return '', 'Missing dot at end of line number ' + str(i)

        present_fragment = False

        if config_params.fragments:
            for frag in ['.|alt|', '.|par|', '.|opt|', '.|loop|', '.|else|', '.|end|']:
                if frag in l and frag != '.|end|' and frag != '.|else|':
                    present_fragment = True
                    num_of_present_fragments += 1
                    num_of_started_fragments += 1
                if frag in l and frag == '.|end|':
                    present_fragment = True
                    num_of_present_fragments += 1
                    num_of_ended_fragments += 1
                if frag in l and (frag == '.|alt|' or frag == '.|par|'):
                    num_of_alt_fragments += 1
                if frag in l and frag == '.|else|':
                    if num_of_alt_fragments == 0:
                        exit = True
                        return '', 'ELSE fragment label declared before ALT or fragment label. ALT or PAR fragment label must proceed ELSE one.'

                    present_fragment = True
                    num_of_present_fragments += 1
                    num_of_else_fragments += 1

        if num_of_started_fragments < num_of_ended_fragments:
            exit = True
            return '', "End of fragment declared before it's start"

        if not present_fragment:

            try:
                if int(l.strip()[:l.find('.')]) != i - num_of_present_fragments:
                    exit = True
                    return '', 'Invalid sentence numbering! Readjust numbering. Make it in order with no number left out or duplicated.'

            except:
                exit = True
                return '', 'Invalid sentence numbering! Readjust numbering. Make it in order with no number left out or duplicated.'

        sent = l.strip()[l.find('.') + 1:]
        if len(sent) > 400:
            sent = sent[:400]
        original.append(sent)

    text = ''.join(original)

    if num_of_started_fragments != num_of_ended_fragments:
        exit = True
        return '', 'Number of started fragments not equals number of ended fragments!'

    if config_params.mode != '' and start and text != '' and not exit:
        errorMess = ConversionPipeline(('').join(text), config_params).run()
        if len(config_params.users.items()) == 0:
            return '', "No human user recognized"
        elif errorMess[0] == 'stepping error':
            return '', "During stepping has occured error"
        elif errorMess[0] == 'subject error':
            return '', 'No subject was created at sentence number ' + str(errorMess[1]) + 'Relation:' + str(errorMess[2]['relations']) + 'Objects:' + str(errorMess[2]['objects'])

        elif errorMess[0] == 'object error':
            return '', 'No object was created at sentence number ' + str(errorMess[1]) + 'Relation:' + str(errorMess[2]['relations']) + 'subjects:' + str(errorMess[2]['subjects'])
        elif errorMess[0] == 'relation error':
            return '', 'No relation was created at sentence number ' + str(errorMess[1]) + 'Objects:' + str(errorMess[2]['objects']) + 'subjects:' + str(errorMess[2]['subjects'])
        else:
            with open('output.puml', 'r', encoding='utf-8') as puml_file:
                plant_uml_code = puml_file.read()

        text = ''
        start = True
    elif (text == '' and not exit):
        return '', 'Use case is empty'
    elif (start == False and not exit):
        return '', 'Previous pipeline is running'
    elif (config_params.mode == '' and not exit):
        return '', 'NLP method was not set'
    elif (config_params.engine == '' and not exit):
        return '', 'NLP library was not set'

    config_params.users = {}
    config_params.project_dictionary = None
    config_params.fragmentsKeywords = None

    is_running = False

    return plant_uml_code, ''
