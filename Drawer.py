import nltk
import plantuml
from nltk.corpus import wordnet as wn


class Drawer:
    def __init__(self, data, configuration):
        self.data = data
        self.configuration = configuration
        self.writes = []

    def create_PlantUml(self, ):
        self.participated = []
        self.actors_activated = []
        with open('triplets.txt', 'w') as file:
            for num in range(1, len(self.data)):
                file.write(self.data[num]['subjects'] + '\n')
                file.write(self.data[num]['relations'] + '\n')
                file.write(self.data[num]['objects'] + '\n')
        with open('output.puml', 'w') as file:
            self.writes.append('@startuml\n')

            self.make_new_system()
            self.rename_all_system_subjects_to_new_system()
            self.remake_objects_to_users()
            self.write_all_participants_and_actors()

            if self.configuration.pattern == 'mvc':
                self.mvc_drawer()
            else:
                self.no_pattern_drawer()

            self.writes.append('@enduml\n')

            for write in self.writes:
                file.write(write)
        url = "http://www.plantuml.com/plantuml/png/"

        plantuml.PlantUML(url).processes_file('output.puml')
        self.configuration.system = ''

    def make_new_system(self):
        for num in range(1, len(self.data)):
            if len(self.data[num]['subjects'].replace(' ', '_')) > len(self.configuration.system) \
                    and not self.is_user(self.data[num]['subjects'].replace(' ', '_')):
                self.configuration.system = self.data[num]['subjects'].replace(' ', '_')

        new_sols = []
        for word in self.configuration.system.split('_'):
            if word not in ('a', 'an', 'the'):
                new_sols.append(word)
        self.configuration.system = '_'.join(new_sols)

    def rename_all_system_subjects_to_new_system(self):
        for num in range(1, len(self.data)):
            if not self.is_user(self.data[num]['subjects'].replace(' ', '_')):
                self.data[num]['subjects'] = self.configuration.system

    def remake_objects_to_users(self):
        for user in self.configuration.users.values():

            for num in range(1, len(self.data)):
                if user.text in self.data[num]['objects']:
                    self.data[num]['objects'] = user.text

    def find_fragment(self, number_of_sentence):
        for fragment in self.data['fragments']:
            if fragment.type in ['LOOP_AUTO']:
                if fragment.start_sentence == number_of_sentence:
                    self.writes.append('LOOP ' + fragment.text + '\n')
            elif fragment.type in ['LOOP']:
                if fragment.start_sentence == number_of_sentence:
                    self.writes.append('LOOP ' + fragment.text + '\n')
            elif fragment.type in ['OPT']:
                if fragment.start_sentence == number_of_sentence:
                    self.writes.append('OPT ' + fragment.text + '\n')
            elif fragment.type in ['OPT_AUTO']:
                if fragment.start_sentence == number_of_sentence:
                    self.writes.append('OPT ' + fragment.text + '\n')
            elif fragment.type in ['PAR_AUTO']:
                if fragment.start_sentence == number_of_sentence:
                    self.writes.append('par \n')
            elif fragment.type in ['ELSE']:
                if fragment.start_sentence == number_of_sentence:
                    self.writes.append('else ' + fragment.text + '\n')
            elif fragment.type in ['ELSE_AUTO']:
                if fragment.start_sentence == number_of_sentence:
                    self.writes.append('else\n')
            elif fragment.type in ['ALT']:
                if fragment.start_sentence == number_of_sentence:
                    self.writes.append('ALT ' + fragment.text + '\n')
            elif fragment.type in ['PAR']:
                if fragment.start_sentence == number_of_sentence:
                    self.writes.append('PAR ' + '\n')
            elif fragment.type in ['ALT_AUTO']:
                if fragment.start_sentence == number_of_sentence:
                    self.writes.append('alt ' + fragment.text + '\n')

    def find_fragment_end(self, number_of_sentence):
        for fragment in self.data['fragments']:
            if fragment.end_sentence - 1 == number_of_sentence and fragment.type not in ['PAR_AUTO', 'ALT_AUTO',
                                                                                         'ELSE']:
                self.writes.append('end\n')

    def mvc_non_para_system_drawer(self, num):
        self.writes.append(self.configuration.system.replace(' ', '_') + ' -> ' + self.data[num][
            'objects'].replace(' ', '_') + '_view' + ': ' + self.data[num]['relations'].replace(' ',
                                                                                                '_') + '()\n')
        self.writes.append(self.data[num]['objects'].replace(' ', '_') + '_view' + ' -> ' + self.data[num][
            'objects'].replace(' ', '_') + '_controller' + ': ' + 'handle_' + self.data[num][
                               'relations'].replace(' ', '_') + '()\n')
        self.writes.append(
            self.data[num]['objects'].replace(' ', '_') + '_controller' + ' -> ' + self.data[num][
                'objects'].replace(' ', '_') + '_model' + ': ' + 'get_data' + '()\n')
        self.writes.append(self.data[num]['objects'].replace(' ', '_') + '_model' + ' --> ' + self.data[num][
            'objects'].replace(' ', '_') + '_controller' + ': ' + 'return_data' + '()\n')
        if (num + 1 < len(self.data)):
            if (self.data[num]['subjects'] == self.configuration.system) and (
                    self.data[num + 1]['subjects'] != self.configuration.system):
                self.writes.append(self.data[num]['objects'].replace(' ', '_') + '_controller' + ' --> ' +
                                   self.data[num]['objects'].replace(' ',
                                                                     '_') + '_view' + ': ' + 'update_view' + '()\n')
                self.writes.append(self.data[num]['objects'].replace(' ',
                                                                     '_') + '_view' + ' --> ' + self.configuration.system.replace(
                    ' ', '_') + ': ' + 'show_view' + '()\n')
        elif (num + 1 == len(self.data)):
            self.writes.append(self.data[num]['objects'].replace(' ', '_') + '_controller' + ' --> ' +
                               self.data[num]['objects'].replace(' ',
                                                                 '_') + '_view' + ': ' + 'update_view' + '()\n')
            self.writes.append(self.data[num]['objects'].replace(' ',
                                                                 '_') + '_view' + ' --> ' + self.configuration.system.replace(
                ' ', '_') + ': ' + 'show_view' + '()\n')

    def mvc_para_system_drawer(self, num):
        secondary_relations = []
        for rel in self.data[num]['relations'].split():
            if rel != self.data[num]['main_relation']:
                secondary_relations.append(rel)
        secondary_relations = ','.join(secondary_relations)

        self.writes.append(self.configuration.system.replace(' ', '_') + ' -> ' + self.data[num][
            'objects'].replace(' ', '_') + '_view' + ': ' + self.data[num]['main_relation'].replace(' ',
                                                                                                    '_') + '(' + secondary_relations + ')\n')
        self.writes.append(self.data[num]['objects'].replace(' ', '_') + '_view' + ' -> ' + self.data[num][
            'objects'].replace(' ', '_') + '_controller' + ': ' + 'handle_' + self.data[num]['main_relation'].replace(
            ' ', '_') + '(' + secondary_relations + ')\n')
        self.writes.append(
            self.data[num]['objects'].replace(' ', '_') + '_controller' + ' -> ' + self.data[num][
                'objects'].replace(' ', '_') + '_model' + ': ' + 'get_data' + '()\n')
        self.writes.append(self.data[num]['objects'].replace(' ', '_') + '_model' + ' --> ' + self.data[num][
            'objects'].replace(' ', '_') + '_controller' + ': ' + 'return_data' + '()\n')
        if (num + 1 < len(self.data)):
            if (self.data[num]['subjects'] == self.configuration.system) and (
                    self.data[num + 1]['subjects'] != self.configuration.system):
                self.writes.append(self.data[num]['objects'].replace(' ', '_') + '_controller' + ' --> ' +
                                   self.data[num]['objects'].replace(' ',
                                                                     '_') + '_view' + ': ' + 'update_view' + '()\n')
                self.writes.append(self.data[num]['objects'].replace(' ',
                                                                     '_') + '_view' + ' --> ' + self.configuration.system.replace(
                    ' ', '_') + ': ' + 'show_view' + '()\n')
        elif (num + 1 == len(self.data)):
            self.writes.append(self.data[num]['objects'].replace(' ', '_') + '_controller' + ' --> ' +
                               self.data[num]['objects'].replace(' ',
                                                                 '_') + '_view' + ': ' + 'update_view' + '()\n')
            self.writes.append(self.data[num]['objects'].replace(' ',
                                                                 '_') + '_view' + ' --> ' + self.configuration.system.replace(
                ' ', '_') + ': ' + 'show_view' + '()\n')

    def mvc_non_para_user_drawer(self, num):

        all_users = [t.sentence_number for t in self.configuration.users.values()]
        if num in all_users:
            if self.configuration.users[num].text.replace(' ', '_') not in self.actors_activated:
                self.actors_activated.append(self.configuration.users[num].text.replace(' ', '_'))

            self.writes.append(
                self.configuration.users[num].text.replace(' ', '_') + ' -> ' + self.data[num][
                    'objects'].replace(' ', '_') + '_view' + ': on_' + self.data[num][
                    'relations'].replace(' ',
                                         '_') + '_' + self.data[num][
                    'objects'].replace(' ', '_') + '()\n')
            self.writes.append(
                self.data[num]['objects'].replace(' ', '_') + '_view' + ' -> ' + self.data[num][
                    'objects'].replace(' ', '_') + '_controller' + ': ' + 'handle_' + self.data[num][
                    'relations'].replace(' ', '_') + '()\n')
            self.writes.append(
                self.data[num]['objects'].replace(' ', '_') + '_controller' + ' -> ' +
                self.data[num][
                    'objects'].replace(' ', '_') + '_model' + ': ' + 'get_data' + '()\n')
            self.writes.append(
                self.data[num]['objects'].replace(' ', '_') + '_model' + ' --> ' + self.data[num][
                    'objects'].replace(' ', '_') + '_controller' + ': ' + 'return_data' + '()\n')
            if (num + 1 < len(self.data)):
                if (self.data[num]['subjects'] == self.configuration.users[num].text) and (
                        self.data[num + 1]['subjects'] != self.configuration.users[num].text):
                    self.writes.append(
                        self.data[num]['objects'].replace(' ', '_') + '_controller' + ' --> ' +
                        self.data[num][
                            'objects'].replace(' ', '_') + '_view' + ': ' + 'update_view' + '()\n')
                    self.writes.append(self.data[num]['objects'].replace(' ',
                                                                         '_') + '_view' + ' --> ' + self.configuration.system.replace(
                        ' ', '_') + ': ' + 'show_view' + '()\n')
            elif (num + 1 == len(self.data)):

                self.writes.append(
                    self.data[num]['objects'].replace(' ', '_') + '_controller' + ' --> ' +
                    self.data[num][
                        'objects'].replace(' ', '_') + '_view' + ': ' + 'update_view' + '()\n')
                self.writes.append(self.data[num]['objects'].replace(' ',
                                                                     '_') + '_view' + ' --> ' + self.configuration.system.replace(
                    ' ', '_') + ': ' + 'show_view' + '()\n')

    def mvc_para_user_drawer(self, num):
        secondary_relations = []
        for rel in self.data[num]['relations'].split():
            if rel != self.data[num]['main_relation']:
                secondary_relations.append(rel)
        secondary_relations = ','.join(secondary_relations)
        all_users = [t.sentence_number for t in self.configuration.users.values()]
        if num in all_users:
            if self.configuration.users[num].text.replace(' ', '_') not in self.actors_activated:
                self.actors_activated.append(self.configuration.users[num].text.replace(' ', '_'))

            self.writes.append(
                self.configuration.users[num].text.replace(' ', '_') + ' -> ' + self.data[num][
                    'objects'].replace(' ', '_') + '_view' + ': on_' + self.data[num]['main_relation'].replace(' ',
                                                                                                               '_') + '_' +
                self.data[num][
                    'objects'].replace(' ', '_') + '(' + secondary_relations + ')\n')
            self.writes.append(
                self.data[num]['objects'].replace(' ', '_') + '_view' + ' -> ' + self.data[num][
                    'objects'].replace(' ', '_') + '_controller' + ': ' + 'handle_' + self.data[num][
                    'main_relation'].replace(' ', '_') + '(' + secondary_relations + ')\n')
            self.writes.append(
                self.data[num]['objects'].replace(' ', '_') + '_controller' + ' -> ' +
                self.data[num][
                    'objects'].replace(' ', '_') + '_model' + ': ' + 'get_data' + '()\n')
            self.writes.append(
                self.data[num]['objects'].replace(' ', '_') + '_model' + ' --> ' + self.data[num][
                    'objects'].replace(' ', '_') + '_controller' + ': ' + 'return_data' + '()\n')
            if (num + 1 < len(self.data)):
                if (self.data[num]['subjects'] == self.configuration.users[num].text) and (
                        self.data[num + 1]['subjects'] != self.configuration.users[num].text):
                    self.writes.append(
                        self.data[num]['objects'].replace(' ', '_') + '_controller' + ' --> ' +
                        self.data[num][
                            'objects'].replace(' ', '_') + '_view' + ': ' + 'update_view' + '()\n')
                    self.writes.append(self.data[num]['objects'].replace(' ',
                                                                         '_') + '_view' + ' --> ' + self.configuration.system.replace(
                        ' ', '_') + ': ' + 'show_view' + '()\n')
            elif (num + 1 == len(self.data)):

                self.writes.append(
                    self.data[num]['objects'].replace(' ', '_') + '_controller' + ' --> ' +
                    self.data[num][
                        'objects'].replace(' ', '_') + '_view' + ': ' + 'update_view' + '()\n')
                self.writes.append(self.data[num]['objects'].replace(' ',
                                                                     '_') + '_view' + ' --> ' + self.configuration.system.replace(
                    ' ', '_') + ': ' + 'show_view' + '()\n')

    def no_pattern_no_para_drawer(self, num):
        if (self.data[num]['subjects'] == self.configuration.system):
            self.writes.append(self.configuration.system.replace(' ', '_') + ' -> ' + self.data[num][
                'objects'].replace(' ', '_') + ': ' + self.data[num]['relations'].replace(' ',
                                                                                          '_') + '()\n')
            self.writes.append('activate ' + self.data[num]['objects'].replace(' ', '_') + '\n')
            self.writes.append('deactivate ' + self.data[num]['objects'].replace(' ', '_') + '\n')
        else:
            if num in self.configuration.users.keys():
                self.writes.append(self.configuration.users[num].text.replace(' ',
                                                                              '_') + ' -> ' + self.configuration.system + ': ' +
                                   self.data[num]['relations'].replace(' ', '_') + '_' + self.data[num][
                                       'objects'].replace(' ', '_') + '()\n')

                if self.configuration.users[num].text.replace(' ', '_') not in self.actors_activated:
                    self.actors_activated.append(self.configuration.users[num].text.replace(' ', '_'))
                    self.writes.append(
                        'activate ' + self.configuration.users[num].text.replace(' ', '_') + '\n')

    def mvc_drawer(self):
        for num in range(1, len(self.data)):
            self.find_fragment(num)
            if not self.configuration.parameters:
                if (self.data[num]['subjects'] == self.configuration.system):
                    self.mvc_non_para_system_drawer(num)
                else:
                    self.mvc_non_para_user_drawer(num)
            else:
                if (self.data[num]['subjects'] == self.configuration.system):
                    self.mvc_para_system_drawer(num)
                else:
                    self.mvc_para_user_drawer(num)
            self.find_fragment_end(num)

    def no_pattern_drawer(self):
        for num in range(1, len(self.data)):
            if self.data[num]['objects'].replace(' ', '_') not in self.participated and (
                    self.data[num]['subjects'] == self.configuration.system):
                self.writes.append('participant ' + self.data[num]['objects'].replace(' ', '_') + '\n')
                self.participated.append(self.data[num]['objects'].replace(' ', '_'))

            self.find_fragment(num)
            if not self.configuration.parameters:
                self.no_pattern_no_para_drawer(num)
            else:
                secondary_relations = []
                for rel in self.data[num]['relations'].split():
                    if rel != self.data[num]['main_relation']:
                        secondary_relations.append(rel)
                secondary_relations = ', '.join(secondary_relations)
                if (self.data[num]['subjects'] == self.configuration.system):
                    self.writes.append(self.data[num]['subjects'].replace(' ', '_') + ' -> ' + self.data[num][
                        'objects'].replace(' ', '_') + ': ' + self.data[num]['main_relation'].replace(' ',
                                                                                                      '_') + '(' + secondary_relations + ')\n')
                    self.writes.append('activate ' + self.data[num]['objects'].replace(' ', '_') + '\n')
                    self.writes.append('deactivate ' + self.data[num]['objects'].replace(' ', '_') + '\n')

                else:
                    self.writes.append(self.data[num]['subjects'].replace(' ',
                                                                          '_') + ' -> ' + self.configuration.system + ': ' +
                                       self.data[num]['main_relation'].replace(' ', '_') + '_' + self.data[num][
                                           'objects'] + '(' + secondary_relations + ')\n')
                    if self.data[num]['subjects'].replace(' ', '_') not in self.actors_activated:
                        self.actors_activated.append(self.data[num]['subjects'].replace(' ', '_'))
                        self.writes.append('activate ' + self.data[num]['subjects'].replace(' ', '_') + '\n')
            self.find_fragment_end(num)

    def write_all_participants_and_actors(self):

        for user in self.configuration.users.values():
            if user.text.replace(' ', '_') not in self.participated:
                self.writes.append('actor ' + user.text.replace(' ', '_') + '\n')
                self.participated.append(user.text.replace(' ', '_'))

        self.participated.append(self.configuration.system.replace(' ', '_'))
        self.writes.append('participant ' + self.configuration.system.replace(' ', '_') + '\n')
        self.writes.append('activate ' + self.configuration.system.replace(' ', '_') + '\n')

    def is_user(self, words):
        ret = False
        for word in words.split('_'):
            word = nltk.WordNetLemmatizer().lemmatize(word.lower())
            synsets = wn.synsets(word)

            for synset in synsets:
                hypernyms = synset.hypernyms()
                for hypernym in hypernyms:
                    if 'person' in hypernym.lexname():
                        ret = True
        return ret
