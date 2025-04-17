from PyQt5.QtCore import QTimer, QEventLoop
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QTextEdit, QCheckBox, QScrollArea
from nltk.corpus import wordnet as wn
from Configuration import Configuration
from ConversionPipeline import ConversionPipeline
from DiagramWindow import DiagramWindow
from Drawer import Drawer
from ErrorWindow import ErrorWindow
from ProjectDictionary import ProjectDictionary
from StepWindow import StepWindow
from utilities import readFilePlain


class MainWindow(QScrollArea):
    def __init__(self):
        super().__init__()
        self.number_of_sentences = 0
        self.stop = None

        self.conf = Configuration()
        self.start = True
        self.is_running = False
        self.setWindowTitle("Transform Use Case to UML")
        self.move(0, 0)
        self.resize(1100, 1100)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.label_use_case = QLabel("Enter the use case:.", self)
        self.label_use_case.setFont(QFont("Arial", 13, QFont.Bold))
        self.label_use_case.setStyleSheet("color: blue; background-color: lightgray")
        self.use_case = QTextEdit(self)
        self.use_case.insertPlainText(''.join(readFilePlain('Dataset/UseCase0.txt')))

        self.project_dictionary_subject = QLineEdit(self)
        self.project_dictionary_subject.setText("(ALL:[example]);(1:[example]);(2:[other_example])")
        self.project_dictionary_object = QLineEdit(self)
        self.project_dictionary_object.setText("(ALL:[example]);(1:[example1, example2]);(2:[other_example])")
        self.project_dictionary_relation = QLineEdit(self)
        self.project_dictionary_relation.setText("(ALL:[example]);(1:[example]);(2:[other_example])")
        self.project_dictionary_subject_label = QLabel("Enter dictionary subjects:", self)
        self.project_dictionary_subject_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.project_dictionary_subject_label.setStyleSheet("color: blue; background-color: lightgray")
        self.project_dictionary_subject_label.hide()
        self.project_dictionary_subject.hide()
        self.project_dictionary_object_label = QLabel("Enter dictionary objects:", self)
        self.project_dictionary_object_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.project_dictionary_object_label.setStyleSheet("color: blue; background-color: lightgray")
        self.project_dictionary_object_label.hide()
        self.project_dictionary_object.hide()
        self.project_dictionary_relation_label = QLabel("Enter dictionary relations:", self)
        self.project_dictionary_relation_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.project_dictionary_relation_label.setStyleSheet("color: blue; background-color: lightgray")
        self.project_dictionary_relation_label.hide()
        self.project_dictionary_relation.hide()

        self.label_fragment_pattern = QLabel("Fragment patterns:", self)
        self.label_fragment_pattern.setFont(QFont("Arial", 13, QFont.Bold))
        self.label_fragment_pattern.setStyleSheet("color: blue; background-color: lightgray")
        self.label_fragment_pattern.hide()
        self.fragment_pattern = QLineEdit(self)
        self.fragment_pattern.setText(
            "LOOP:[For each...do];OPT:[If...then, In case of...then];ALT:[If...do...otherwise];PAR:[simultaneously do...and do];")
        self.fragment_pattern.hide()
        self.label_diagram_output = QLabel("Diagram output:", self)
        self.label_diagram_loading = QLabel("Diagram is being created...:", self)
        self.label_diagram_loading.setFont(QFont("Arial", 13, QFont.Bold))
        self.label_diagram_loading.setStyleSheet("color: Red; background-color: lightgray")
        self.label_diagram_loading.hide()
        self.label_diagram_error = QLabel("Diagram is being created...:", self)
        self.label_diagram_error.setFont(QFont("Arial", 13, QFont.Bold))
        self.label_diagram_error.setStyleSheet("color: Red; background-color: lightgray")
        self.label_diagram_error.hide()
        self.label_opt_1 = QLabel("", self)
        self.label_opt_1.setFont(QFont("Arial", 13, QFont.Bold))
        self.label_opt_1.setStyleSheet("color: Red; background-color: lightgray")
        self.label_opt_1.hide()
        self.label_opt_2 = QLabel("", self)
        self.label_opt_2.setFont(QFont("Arial", 13, QFont.Bold))
        self.label_opt_2.setStyleSheet("color: Red; background-color: lightgray")
        self.label_opt_2.hide()
        self.label_diagram_output.setFont(QFont("Arial", 13, QFont.Bold))
        self.label_diagram_output.setStyleSheet("color: blue; background-color: lightgray")
        self.transform_button = QPushButton("Transform to UML", self)
        self.transform_button.clicked.connect(self.start_pipeline)

        self.pattern_label = QLabel("Used software pattern:", self)
        self.pattern_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.pattern_label.setStyleSheet("color: blue; background-color: lightgray")

        self.no_pattern_box = QCheckBox('No pattern')
        self.no_pattern_box.setChecked(True)
        self.no_pattern_box.stateChanged.connect(self.no_pattern)

        self.mvc_pattern_box = QCheckBox('MVC pattern')
        self.mvc_pattern_box.stateChanged.connect(self.mvc)
        self.diagram = QLabel(self)
        self.mode_label = QLabel("NLP method:", self)
        self.mode_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.mode_label.setStyleSheet("color: blue; background-color: lightgray")
        self.pos_check_box = QCheckBox('Part of speech')
        self.pos_check_box.setChecked(True)
        self.conf.mode = 'POS'
        self.oie_check_box = QCheckBox('Open information extraction')
        self.dp_check_box = QCheckBox('Dependency parsing')
        self.dp_check_box.stateChanged.connect(self.dp_checkbox)
        self.pos_check_box.stateChanged.connect(self.pos_checkbox)
        self.oie_check_box.stateChanged.connect(self.oie_checkbox)

        self.lib_label = QLabel("NLP library:", self)
        self.lib_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.lib_label.setStyleSheet("color: blue; background-color: lightgray")
        self.stanza_check_box = QCheckBox('Stanza')
        self.spacy_check_box = QCheckBox('Spacy')
        self.spacy_check_box.setChecked(True)
        self.spacy_check_box.stateChanged.connect(self.spacy_checkbox)
        self.stanza_check_box.stateChanged.connect(self.stanza_checkbox)
        self.conf.engine = 'spacy'

        self.other_label = QLabel("Other options:", self)
        self.other_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.other_label.setStyleSheet("color: blue; background-color: lightgray")
        self.steps_check_box = QCheckBox('Enable stepping')
        self.steps_check_box.stateChanged.connect(self.steps_checkbox)
        self.coreference_check_box = QCheckBox('Coreferences')
        self.coreference_check_box.stateChanged.connect(self.coreference_checkbox)
        self.fragments_check_box = QCheckBox('Allow fragments automatic detection')
        self.fragments_check_box.stateChanged.connect(self.fragment_checkbox)
        self.fragments_keywords_check_box = QCheckBox('Allow fragments definition though keywords')
        self.fragments_keywords_check_box.stateChanged.connect(self.fragment_keywords_checkbox)
        self.project_checkbox = QCheckBox('Project dictionary')
        self.project_checkbox.stateChanged.connect(self.set_project)
        self.parameters_checkbox = QCheckBox('Enable parameters in messages')
        self.parameters_checkbox.stateChanged.connect(self.set_parameters)

        self.label_diagram_output.hide()
        self.diagram.hide()

        layout = QVBoxLayout(self)
        main_layout = QVBoxLayout(self)

        main_layout.addWidget(self.scroll_area)
        layout_widget = QWidget(self)
        layout_widget.setLayout(layout)
        self.scroll_area.setWidget(layout_widget)
        self.scroll_area.resize(1080, 1080)
        layout.addWidget(self.mode_label)
        layout.addWidget(self.pos_check_box)
        layout.addWidget(self.dp_check_box)
        layout.addWidget(self.oie_check_box)
        layout.addWidget(self.lib_label)
        layout.addWidget(self.stanza_check_box)
        layout.addWidget(self.spacy_check_box)

        layout.addWidget(self.other_label)
        layout.addWidget(self.steps_check_box)
        layout.addWidget(self.coreference_check_box)
        layout.addWidget(self.parameters_checkbox)
        layout.addWidget(self.fragments_check_box)
        layout.addWidget(self.fragments_keywords_check_box)
        layout.addWidget(self.project_checkbox)
        layout.addWidget(self.project_dictionary_subject_label)
        layout.addWidget(self.project_dictionary_subject)
        layout.addWidget(self.project_dictionary_relation_label)
        layout.addWidget(self.project_dictionary_relation)
        layout.addWidget(self.project_dictionary_object_label)
        layout.addWidget(self.project_dictionary_object)
        layout.addWidget(self.pattern_label)
        layout.addWidget(self.no_pattern_box)
        layout.addWidget(self.mvc_pattern_box)
        layout.addWidget(self.label_fragment_pattern)
        layout.addWidget(self.fragment_pattern)
        layout.addWidget(self.label_use_case)
        layout.addWidget(self.use_case)
        layout.addWidget(self.transform_button)
        layout.addWidget(self.label_diagram_output)
        layout.addWidget(self.diagram)
        layout.addWidget(self.label_diagram_loading)
        layout.addWidget(self.label_diagram_error)
        layout.addWidget(self.label_opt_1)
        layout.addWidget(self.label_opt_2)
        self.setWidget(self.scroll_area)

    def set_project(self, state):
        if state == 2:
            self.conf.project_dictionary = True
            self.conf.enable_projects = True
            self.project_dictionary_object.show()
            self.project_dictionary_object_label.show()
            self.project_dictionary_subject.show()
            self.project_dictionary_subject_label.show()
            self.project_dictionary_relation.show()
            self.project_dictionary_relation_label.show()
        else:
            self.conf.project_dictionary = None
            self.conf.enable_projects = False
            self.project_dictionary_object.hide()
            self.project_dictionary_object_label.hide()
            self.project_dictionary_subject.hide()
            self.project_dictionary_subject_label.hide()
            self.project_dictionary_relation.hide()
            self.project_dictionary_relation_label.hide()


    def start_pipeline(self):
        if not self.is_running:
            self.diagram.hide()
            self.label_diagram_error.hide()
            self.label_opt_1.hide()
            self.label_opt_2.hide()
            self.label_diagram_loading.show()
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.pipe)
            self.timer.start(500)

    def mvc(self, state):
        if state == 2:
            self.conf.pattern = 'mvc'
            self.no_pattern_box.setChecked(False)
        else:
            self.conf.pattern = None

    def no_pattern(self, state):
        if state == 2:
            self.conf.pattern = None
            self.mvc_pattern_box.setChecked(False)
        else:
            self.conf.pattern = 'mvc'

    def stanza_checkbox(self, state):
        if state == 2:
            self.conf.engine = 'stanza'
            self.spacy_check_box.setChecked(False)

    def spacy_checkbox(self, state):
        if state == 2:
            self.conf.engine = 'spacy'
            self.stanza_check_box.setChecked(False)

    def set_parameters(self, state):
        self.conf.parameters = not self.conf.parameters

    def pos_checkbox(self, state):
        if state == 2:
            self.conf.mode = 'POS'
            self.dp_check_box.setChecked(False)
            self.oie_check_box.setChecked(False)

    def dp_checkbox(self, state):
        if state == 2:
            self.conf.mode = 'DP'
            self.pos_check_box.setChecked(False)
            self.oie_check_box.setChecked(False)

    def oie_checkbox(self, state):
        if state == 2:
            self.conf.mode = 'OIE'
            self.dp_check_box.setChecked(False)
            self.pos_check_box.setChecked(False)

    def coreference_checkbox(self, state):
        self.conf.coreference = not self.conf.coreference

    def fragment_checkbox(self, state):
        self.conf.fragments = not self.conf.fragments
        if self.conf.fragments:
            self.use_case.setText('.|LOOP|inc.\n'+self.use_case.toPlainText()+".|END|.\n")

    def fragment_keywords_checkbox(self, state):
        if state == 2:
            self.fragment_pattern.show()
            self.label_fragment_pattern.show()
        else:
            self.fragment_pattern.hide()
            self.label_fragment_pattern.hide()

    def steps_checkbox(self, state):
        self.conf.steps = not self.conf.steps

    def pipe(self):
        self.is_running = True
        i = 0
        self.exit = False
        self.original = []
        sp = self.use_case.toPlainText().lower().split('\n')

        if self.conf.mode == 'OIE' and self.conf.engine == 'spacy':
            self.exit = True

            self.label_diagram_error.setText(
                'Open information extraction is possible only with STANZA option.')
            self.label_diagram_loading.hide()

            self.label_diagram_error.show()
        num_of_present_fragments = 0
        num_of_started_fragments = 0
        num_of_ended_fragments = 0
        num_of_else_fragments = 0
        num_of_alt_fragments = 0
        while i < 50 and i < len(sp) and sp[i] != '':
            l = sp[i]
            i += 1
            if l.strip()[-1] != '.':
                self.exit = True

                self.label_diagram_error.setText(
                    'Missing dot at end of line number '+str(i))
                self.label_diagram_loading.hide()

                self.label_diagram_error.show()
            present_fragment = False

            if self.conf.fragments:
                for frag in ['.|alt|','.|par|','.|opt|','.|loop|','.|else|','.|end|']:
                    if frag in l and frag != '.|end|' and frag != '.|else|':
                        present_fragment = True
                        num_of_present_fragments+=1
                        num_of_started_fragments+=1
                    if frag in l and frag == '.|end|':
                        present_fragment = True
                        num_of_present_fragments += 1
                        num_of_ended_fragments+=1
                    if frag in l and (frag == '.|alt|' or frag == '.|par|'):
                        num_of_alt_fragments += 1
                    if frag in l and frag == '.|else|':
                        if num_of_alt_fragments == 0:
                            self.exit = True

                            self.label_diagram_error.setText(
                                'ELSE fragment label declared before ALT or fragment label. ALT or PAR fragment label must proceed ELSE one.')
                            self.label_diagram_loading.hide()

                            self.label_diagram_error.show()
                        present_fragment = True
                        num_of_present_fragments += 1
                        num_of_else_fragments += 1

            if num_of_started_fragments < num_of_ended_fragments:
                self.exit = True

                self.label_diagram_error.setText(
                    "End of fragment declared before it's start")
                self.label_diagram_loading.hide()

                self.label_diagram_error.show()


            if not present_fragment:

                try:
                    if int(l.strip()[:l.find('.')]) != i - num_of_present_fragments:
                        self.exit = True

                        self.label_diagram_error.setText(
                            'Invalid sentence numbering! Readjust numbering. Make it in order with no number left out or duplicated.')
                        self.label_diagram_loading.hide()

                        self.label_diagram_error.show()
                except:
                    self.exit = True

                    self.label_diagram_error.setText(
                        'Invalid sentence numbering! Readjust numbering. Make it in order with no number left out or duplicated.')
                    self.label_diagram_loading.hide()

                    self.label_diagram_error.show()
            sent = l.strip()[l.find('.') + 1:]
            if len(sent) > 400:
                sent = sent[:400]
            self.original.append(sent)

        self.text = ''.join(self.original)

        if num_of_started_fragments != num_of_ended_fragments:
            self.exit = True

            self.label_diagram_error.setText(
                'Number of started fragments not equals number of ended fragments!')
            self.label_diagram_loading.hide()

            self.label_diagram_error.show()

        if self.fragments_keywords_check_box.isChecked() and self.fragment_pattern.text().strip() != '':
            if ':' not in self.fragment_pattern.text() or self.fragment_pattern.text().count(':') != (
            self.fragment_pattern.text().count(';')) or self.fragment_pattern.text().count('[') != (
            self.fragment_pattern.text().count(']')) or self.fragment_pattern.text().count('(') != (
            self.fragment_pattern.text().count(')')):
                self.exit = True
                self.label_diagram_error.setText(
                    'Invalid fragment pattern. Valid fragment is LOOP/ALT/PAR/OPT:[pattern1,patter2 first part .. pattern2 second part];')
                self.label_diagram_loading.hide()

                self.label_diagram_error.show()
        self.conf.fragment_pattern = {}
        if self.fragments_keywords_check_box.isChecked():
            self.all_posible_fragments = ['alt', 'opt', 'par', 'loop']
            possibilities = self.fragment_pattern.text().split(';')
            for pos in possibilities[:-1]:

                pair = pos.split(':')
                if pair[0].lower() not in self.all_posible_fragments and not self.exit:
                    self.exit = True
                    self.label_diagram_error.setText("Invalid loop definition: " + pair[
                        0] + ' Valid pattern is LOOP/ALT/PAR/OPT:[pattern1,patter2 first part .. pattern2 second part];')
                    self.label_diagram_loading.hide()

                    self.label_diagram_error.show()
                elif not self.exit:
                    if self.conf.fragment_pattern is None:
                        self.conf.fragment_pattern = {}
                    self.conf.fragment_pattern[pair[0]] = pair[1][1:-1].split(',')

        if self.conf.mode != '' and self.start and self.text != '' and not self.exit:
            self.diagram.hide()
            if self.conf.enable_projects:
                self.init_project()

            self.start = False

            if (self.conf.steps):
                self.solutions = {}
                self.solutions['fragments'] = []
                self.stop = False
                i = 0
                if self.conf.fragments:
                    c = ConversionPipeline('.'.join(self.original),self.conf)
                    self.original = c.detect_fragments()
                    self.solutions['fragments'] = c.fragments
                num = 0
                if self.conf.fragment_pattern:
                    self.new_sentences = []
                    for sentence in self.original:
                        c = ConversionPipeline('.'.join(self.original), self.conf)
                        ret = c.find_fragment_by_pattern(sentence, num)
                        num += 1

                        if ret == []:
                            self.new_sentences.append(sentence)
                        elif ret[0] == 'ALT_AUTO':
                            self.new_sentences.append(ret[2])
                            self.new_sentences.append(ret[3])
                        elif ret[0] == 'LOOP_AUTO' or ret[0] == 'OPT_AUTO':
                            self.new_sentences.append(ret[1])
                        elif ret[0] == 'PAR_AUTO':
                            self.new_sentences.append(ret[1])
                            self.new_sentences.append(ret[2])

                        for frag in c.fragments:
                            self.solutions['fragments'].append(frag)
                    self.original = self.new_sentences


                for sentence in self.original:
                    if sentence != '' and not self.stop:

                        original = self.conf.mode
                        self.conf.mode = 'POS';
                        pos = ConversionPipeline(sentence, self.conf).run_pipeline(i)
                        self.conf.mode = 'DP'
                        dp = ConversionPipeline(sentence, self.conf).run_pipeline(i)
                        oie_message = "NOT IMPLEMENTED IN SPACY"
                        if self.conf.engine == 'stanza':
                            self.conf.mode = 'OIE'

                            oie_message = ConversionPipeline(sentence, self.conf).run_pipeline(i)
                            oie_message = oie_message[i+1]

                        self.conf.mode = original
                        i += 1;
                        self.step_window = StepWindow()
                        self.step_window.show()
                        loop = QEventLoop()

                        self.step_window.accepted.connect(loop.quit)
                        self.step_window.rejected.connect(loop.quit)
                        self.solutions[i] = {}
                        self.step_window.generate_options(sentence, pos[i], dp[i], oie_message, loop)
                        loop.exec_()
                        self.stop = self.step_window.quit
                        if not self.stop:
                            self.solutions[i]['objects'] = self.step_window.option['objects']
                            self.solutions[i]['subjects'] = self.step_window.option['subjects']
                            self.solutions[i]['relations'] = self.step_window.option['relations']
                            self.solutions[i]['main_relation']= self.step_window.option['main_relation']
                            self.errorMess = ['', 0, '']

                self.step_window.hide()
                self.number_of_sentences = i
                if self.conf.coreference:
                    self.solve_coreference('subjects')
                    self.solve_coreference('objects')
                    self.solve_coreference('relations')

                if not self.stop and len(self.conf.users.items()) != 0:
                    d = Drawer(self.solutions, self.conf)
                    d.create_PlantUml()
                else:
                    self.errorMess = ['stepping error', 0, 0]
            else:
                self.errorMess = ConversionPipeline(('').join(self.text), self.conf).run()
            if len(self.conf.users.items()) == 0:
                self.label_diagram_error.setText("No human user recognized")
                self.label_diagram_loading.hide()
                self.label_diagram_error.show()
            elif self.errorMess[0] == 'stepping error':
                self.label_diagram_error.setText("During stepping has occured error")
                self.label_diagram_loading.hide()
                self.label_diagram_error.show()
            elif self.errorMess[0] == 'subject error':
                self.label_diagram_error.setText('No subject was created at sentence number ' + str(self.errorMess[1]))
                self.label_opt_1.setText('Relation:' + str(self.errorMess[2]['relations']))
                self.label_opt_2.setText('Objects:' + str(self.errorMess[2]['objects']))
                self.label_opt_1.show()
                self.label_opt_2.show()
                self.label_diagram_loading.hide()
                self.label_diagram_error.show()
            elif self.errorMess[0] == 'object error':
                self.label_diagram_error.setText('No object was created at sentence number ' + str(self.errorMess[1]))
                self.label_opt_1.setText('Subjects:' + str(self.errorMess[2]['subjects']))
                self.label_opt_2.setText('Relation:' + str(self.errorMess[2]['relations']))
                self.label_opt_1.show()
                self.label_opt_2.show()
                self.label_diagram_loading.hide()
                self.label_diagram_error.show()
            elif self.errorMess[0] == 'relation error':
                self.label_diagram_error.setText('No relation was created at sentence number ' + str(self.errorMess[1]))
                self.label_opt_1.setText('Subjects:' + str(self.errorMess[2]['subjects']))
                self.label_opt_2.setText('Objects:' + str(self.errorMess[2]['objects']))
                self.label_opt_1.show()
                self.label_opt_2.show()
                self.label_diagram_loading.hide()
                self.label_diagram_error.show()
            else:
                self.label_diagram_loading.hide()
                self.diagramWindow = DiagramWindow()
                self.diagramWindow.show_diagram()

            self.text = ''
            self.start = True
        elif (self.text == '' and not self.exit):
            self.error1 = ErrorWindow()
            self.error1.error('Use case is empty')
        elif (self.start == False and not self.exit):
            self.error2 = ErrorWindow()
            self.error2.error('Previous pipeline is running')
        elif (self.conf.mode == '' and not self.exit):
            self.error3 = ErrorWindow()
            self.error3.error('NLP method was not set')
        elif (self.conf.engine == '' and not self.exit):
            self.error4 = ErrorWindow()
            self.error4.error('NLP library was not set')
        self.timer.stop()
        self.conf.users = {}
        self.conf.project_dictionary = None
        self.conf.fragmentsKeywords = None

        self.is_running = False

    def init_project(self):
        self.projectDictionary = ProjectDictionary()
        self.projectDictionary.init_sentences(len(self.original))

        items = self.project_dictionary_object.text().split(';')
        for item in items:
            if (item[1:item.find(':')] != 'ALL'):
                number = int(item[1:item.find(':')])
            else:
                number = 'ALL'
            possibilities = [i.strip() for i in item[item.find(':') + 2:len(item) - 2].split(',')]
            self.projectDictionary.assign_object_to_sentence(number, possibilities)

        items = self.project_dictionary_subject.text().split(';')
        for item in items:
            if (item[1:item.find(':')] != 'ALL'):
                number = int(item[1:item.find(':')])
            else:
                number = 'ALL'
            possibilities = [i.strip() for i in item[item.find(':') + 2:len(item) - 2].split(',')]
            self.projectDictionary.assign_subject_to_sentence(number, possibilities)

        items = self.project_dictionary_relation.text().split(';')
        for item in items:
            if (item[1:item.find(':')] != 'ALL'):
                number = int(item[1:item.find(':')])
            else:
                number = 'ALL'

            possibilities = [i.strip() for i in item[item.find(':') + 2:len(item) - 2].split(',')]
            self.projectDictionary.assign_relation_to_sentence(number, possibilities)

        self.conf.project_dictionary = self.projectDictionary

    def solve_coreference(self, type):

        words = []
        numbers = [0]
        for i in range(1, self.number_of_sentences + 1):
            n = 0
            for j in self.solutions[i][type].split():
                words.append(j)
                n += 1
            numbers.append(n)

        for i in range(len(words)):
            word1 = words[i].lower()
            for j in range(len(words)):
                word2 = words[j].lower()
                if word1 in self.synonyms(word2) and word2 in self.synonyms(word1):
                    if (len(self.synonyms(word2)) < len(self.synonyms(word1))):
                        words[i] = word1
                        words[j] = word1
                    else:
                        words[i] = word2
                        words[j] = word2

        n = 0
        for i in range(1, self.number_of_sentences + 1):

            self.solutions[i][type] = []
            while (numbers[i] != 0):
                numbers[i] -= 1
                self.solutions[i][type].append(words[n])
                n += 1
            self.solutions[i][type] = ' '.join(self.solutions[i][type])
        return words

    def synonyms(self, text):
        syn = []
        for sublist in wn.synonyms(text):
            for i in sublist:
                syn.append(i)
        return syn