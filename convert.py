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
                'Missing dot at end of line number ' + str(i))
            self.label_diagram_loading.hide()

            self.label_diagram_error.show()
        present_fragment = False

        if self.conf.fragments:
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
                c = ConversionPipeline('.'.join(self.original), self.conf)
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
                        oie_message = oie_message[i + 1]

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
                        self.solutions[i]['main_relation'] = self.step_window.option['main_relation']
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