import glob
import os
import time

import nltk
from nltk.corpus import wordnet as wn
from stanza.server import CoreNLPClient
import stanza

from Drawer import Drawer
#import spacy.cli

from Fragment import Fragment
from User import User
from utilities import init_tokens


class ConversionPipeline:

    def __init__(self, text, configuration):
        self.solutions = None
        self.text = text
        self.sentences = []
        self.fragments = []
        self.last_fragment = None
        self.configuration = configuration
        self.phrases = {}
        self.tokens = init_tokens()
        self.number_of_sentences = 0

        self.sentences = text.replace("'", '').strip().split('.')
        if len(self.sentences[-1]) == 0:
            self.sentences = self.sentences[:len(self.sentences) - 1]
        new_sentences = []
        for sentence in self.sentences:
            if len(sentence) != 0:
                new_sentences.append(sentence)
        self.sentences = new_sentences
        print('Conversion pipeline run with following configuration:')
        print('Project: ' + str(configuration.project_dictionary))
        print('Coreference: ' + str(configuration.coreference))
        print('Steps: ' + str(configuration.steps))
        print('NLP engine: ' + str(configuration.engine))
        print('Mode: ' + str(configuration.mode))

    def run(self):
        start = time.time()
        if not self.configuration.steps:
            res = self.run_pipeline_with_configuration()
            print("Run took " + str(time.time() - start))
            for num in range(1, len(res)):
                if len(res[num]['subjects']) == 0:
                    return ['subject error', num, res[num]]
                if len(res[num]['relations']) == 0:
                    return ['relation error', num, res[num]]
                if len(res[num]['objects']) == 0:
                    return ['object error', num, res[num]]

            if (res != False and len(self.configuration.users.items()) != 0):
                d = Drawer(res, self.configuration)
                d.create_PlantUml()
                return ['ok', 0]

    def replace_phrases(self, sentence):
        if sentence.count('\"') % 2 != 0:
            raise 'Number of quotes in sentence is wrong'

        word = ""
        add = False
        for c in sentence:
            if c == '\"' and len(word) == 0:
                add = True
            elif c == '\"' and len(word) != 0:
                add = False
                word += c
                num_of_token = 0
                stop = False
                while not stop and num_of_token <= len(self.tokens):
                    token = self.tokens[num_of_token]
                    if not self.token_is_used(token):
                        self.phrases[token] = word
                        print(word + " was replaced by " + token)
                        stop = True
                    else:
                        num_of_token += 1
                        print(token + " cant be used, because it occurs in text")
                word = ""

            if add:
                word += c

        for token in self.phrases.keys():
            sentence = sentence.replace(self.phrases[token], token)
        return sentence

    def replace_tokens(self, sentence):
        for token in self.phrases.keys():
            sentence = sentence.replace(token, self.phrases[token])
        return sentence

    def token_is_used(self, token):
        for key in self.phrases.keys():
            if key == token or token in self.text:
                return True
        return False

    def remove_fragment_keywords(self):
        new_senteces = []
        for sentence in self.sentences:
            if not '|' in sentence:
                new_senteces.append(sentence)
            self.sentences = new_senteces

    def detect_fragments(self, sentences=[]):
        if sentences != []:
            self.sentences = sentences
        i = 1
        new_senteces = []
        for sentence in self.sentences:
            if '|' in sentence:
                fragment = sentence.split('|')[1].strip()
                label = sentence.split('|')[2].replace('.', '').strip()
                if fragment.lower() == 'alt':
                    self.last_fragment = Fragment('ALT', len(self.fragments), i)
                    self.last_fragment.text = label
                    self.fragments.append(self.last_fragment)
                elif fragment.lower() == 'par':
                    self.last_fragment = Fragment('PAR', len(self.fragments), i)
                    self.last_fragment.text = label
                    self.fragments.append(self.last_fragment)
                elif fragment.lower() == 'opt':
                    self.last_fragment = Fragment('OPT', len(self.fragments), i)
                    self.last_fragment.text = label
                    self.fragments.append(self.last_fragment)
                elif fragment.lower() == 'loop':
                    self.last_fragment = Fragment('LOOP', len(self.fragments), i)
                    self.last_fragment.text = label
                    self.fragments.append(self.last_fragment)
                elif fragment.lower() == 'else':
                    self.last_fragment = Fragment('ELSE', len(self.fragments), i)
                    self.last_fragment.text = label
                    self.fragments.append(self.last_fragment)
                elif fragment.lower() == 'end':
                    num = 0
                    stop = False;
                    while num < len(self.fragments) and not stop:
                        if not self.fragments[num].ended:
                            self.fragments[num].ended = True
                            self.fragments[num].end_sentence = i
                            stop = True;
                        num += 1
                else:
                    print('WRONG fragment')
            else:
                i += 1
                new_senteces.append(sentence)
            self.sentences = new_senteces
        return self.sentences

    def run_pipeline_with_configuration(self):
        if self.configuration.fragments:
            self.detect_fragments()
        else:
            self.remove_fragment_keywords()

        self.solutions = {}

        num = 0
        for i in range(len(self.sentences)):
            self.sentences[i] = self.replace_phrases(self.sentences[i])
        self.new_sentences = []
        self.add_sentences = []
        for sentence in self.sentences:
            ret = self.find_fragment_by_pattern(sentence, num)
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

        self.sentences = self.new_sentences

        self.run_pipeline()
        if self.configuration.coreference:
            self.solve_coreference('subjects')
            self.solve_coreference('objects')
            self.solve_coreference('relations')

        return self.solutions

    def run_pipeline(self, num=0):
        if self.solutions is None:
            self.solutions = {}
        self.solutions['fragments'] = self.fragments

        if self.configuration.engine == 'stanza' and self.configuration.mode != 'OIE':
            self.nlp = stanza.Pipeline(lang='en', processors=['tokenize', 'mwt', 'pos', 'lemma', 'depparse'])
            text = ". ".join(self.sentences)
            doc = self.nlp(text)
            self.original_sentences = self.sentences
            self.sentences = doc.sentences
        for sentence in self.sentences:
            result = []
            if self.configuration.engine == 'spacy':
                raise ValueError('Spacy not allowed')
                #self.nlp = spacy.load(self.configuration.model)

                if self.configuration.mode == 'POS':
                    result = self.part_of_speech_pipeline_spacy(sentence)
                elif self.configuration.mode == 'DP':
                    result = self.dependency_tree_pipeline_spacy(sentence)
                elif self.configuration.mode == 'OIE':
                    return False;

            elif self.configuration.engine == 'stanza':

                if self.configuration.mode == 'POS':
                    result = self.part_of_speech_pipeline_stanza(sentence)
                elif self.configuration.mode == 'DP':
                    result = self.dependency_tree_pipeline_stanza(sentence)
                elif self.configuration.mode == 'OIE':
                    result = self.open_information_extraction_pipeline(sentence)

            else:
                return 'Wrong processor'
            num += 1

            for i in range(1, 4):
                result[i] = self.replace_tokens(result[i]).replace('\"', "")

            self.solutions[num] = {}
            self.solutions[num]['subjects'] = result[1].strip()


            self.solutions[num]['objects'] = result[3].strip()
            self.solutions[num]['relations'] = result[2].strip()
            self.solutions[num]['main_relation'] = result[0].strip()

            new_sols = []
            for word in self.solutions[num]['objects'].split(' '):
                if word not in ('a', 'an', 'the'):
                    new_sols.append(word)
            self.solutions[num]['objects'] = ' '.join(new_sols)

            new_sols = []
            for word in self.solutions[num]['subjects'].split(' '):
                if word not in ('a', 'an', 'the'):
                    new_sols.append(word)
            self.solutions[num]['subjects'] = ' '.join(new_sols)

            new_sols = []
            for word in self.solutions[num]['relations'].split(' '):
                if word not in ('a', 'an', 'the'):
                    new_sols.append(word)
            self.solutions[num]['relations'] = ' '.join(new_sols)

            if self.configuration.engine == 'stanza' and self.configuration.mode != 'OIE':
                if self.configuration.steps:
                    orig_sentence = self.original_sentences[0]
                else:
                    orig_sentence = self.original_sentences[num - 1]
            else:
                orig_sentence = "".join(sentence);
            if self.configuration.project_dictionary != None:
                for phrase in self.configuration.project_dictionary.data[num]['subject']:
                    if phrase in orig_sentence:
                        self.solutions[num]['subjects'] = phrase
                for phrase in self.configuration.project_dictionary.data['ALL']['subject']:
                    if phrase in orig_sentence:
                        self.solutions[num]['subjects'] = phrase

                for phrase in self.configuration.project_dictionary.data[num]['relation']:
                    if phrase in orig_sentence:
                        self.solutions[num]['relations'] = phrase
                for phrase in self.configuration.project_dictionary.data['ALL']['relation']:
                    if phrase in orig_sentence:
                        self.solutions[num]['relations'] = phrase

                for phrase in self.configuration.project_dictionary.data[num]['object']:
                    if phrase in orig_sentence:
                        self.solutions[num]['objects'] = phrase
                for phrase in self.configuration.project_dictionary.data['ALL']['object']:
                    if phrase in orig_sentence:
                        self.solutions[num]['objects'] = phrase
            if self.is_user(result[1].strip()):
                new_sols = []
                for word in result[1].strip().split(' '):
                    if word not in ('a', 'an', 'the'):
                        new_sols.append(word)
                self.configuration.users[num] = User((' ').join(new_sols), num)
            self.number_of_sentences = num
        return self.solutions

    def is_user(self, words):
        ret = False
        for word in words.split(' '):
            word = nltk.WordNetLemmatizer().lemmatize(word.lower())

            synsets = wn.synsets(word)

            for synset in synsets:
                hypernyms = synset.hypernyms()
                for hypernym in hypernyms:
                    if 'person' in hypernym.lexname():
                        ret = True
        return ret

    def find_fragment_by_pattern(self, sentence, num):
        ret = []
        if self.configuration.fragment_pattern is not None:
            for key in self.configuration.fragment_pattern.keys():
                for value in self.configuration.fragment_pattern[key]:
                    first_half = value.strip().lstrip().rstrip().split('...')[0].lower()
                    second_half = value.strip().lstrip().rstrip().split('...')[1].lower()
                    if key in ['LOOP']:
                        if first_half in sentence and second_half in sentence:
                            sentence_split = value.split('...')
                            sentence = sentence.replace(sentence_split[0].strip().lstrip().rstrip(), '')
                            label = sentence.split(sentence_split[1].strip().lstrip().rstrip())[0]
                            sentence = sentence.split(sentence_split[1].strip().lstrip().rstrip())[1].lstrip()
                            fragment = Fragment('LOOP_AUTO', len(self.fragments), num + 1)
                            fragment.text = label
                            fragment.end_sentence = num + 2
                            ret = ['LOOP_AUTO', sentence]
                            self.fragments.append(fragment)
                    elif key in ['OPT']:
                        if first_half in sentence and second_half in sentence:
                            sentence_split = value.split('...')
                            sentence = sentence.replace(sentence_split[0].strip().lstrip().rstrip(), '')
                            label = sentence.split(sentence_split[1].strip().lstrip().rstrip())[0]
                            sentence = sentence.split(sentence_split[1].strip().lstrip().rstrip())[1].lstrip()
                            fragment = Fragment('OPT_AUTO', len(self.fragments), num + 1)
                            fragment.end_sentence = num + 2
                            fragment.text = label
                            ret = ['OPT_AUTO', sentence]
                            self.fragments.append(fragment)
                    elif key in ['ALT']:
                        third_half = value.strip().lstrip().rstrip().split('...')[2].lower()
                        if first_half in sentence and second_half in sentence:
                            sentence = sentence.replace(first_half, '')
                            label = sentence.split(second_half)[0].replace(first_half, '')
                            sentence1 = \
                            sentence.split(second_half)[1].replace(first_half, '').lstrip().split(third_half)[
                                0].lstrip().replace('.', '').strip()

                            sentence2 = \
                            sentence.split(second_half)[1].replace(first_half, '').lstrip().split(third_half)[
                                1].lstrip().replace('.', '').strip()
                            ret = ['ALT_AUTO', label, sentence1, sentence2]
                            fragment = Fragment('ALT_AUTO', len(self.fragments), num + 1)
                            fragment.text = label
                            fragment.end_sentence = num + 2
                            self.fragments.append(fragment)
                            fragment = Fragment('ELSE_AUTO', len(self.fragments), num + 2)
                            fragment.end_sentence = num + 3
                            self.fragments.append(fragment)

                    elif key in ['PAR']:
                        if first_half in sentence and second_half in sentence:
                            sentence_split = value.split('...')
                            sentence = sentence.replace(sentence_split[0].strip().lstrip().rstrip(), '')
                            label = sentence.split(sentence_split[1].strip().lstrip().rstrip())[0].replace(first_half,
                                                                                                           '')
                            sentence = sentence.split(sentence_split[1].strip().lstrip().rstrip())[1].lstrip().replace(
                                second_half, '')
                            ret = ['PAR_AUTO', label, sentence]
                            fragment = Fragment('PAR_AUTO', len(self.fragments), num + 1)
                            fragment.end_sentence = num + 2
                            self.fragments.append(fragment)
                            fragment = Fragment('ELSE_AUTO', len(self.fragments), num + 2)
                            fragment.end_sentence = num + 3
                            self.fragments.append(fragment)
        return ret;

    def open_information_extraction_pipeline(self, text):
        subjects = []
        objects = []
        relations = []
        main_relation = ''
        ann = ''
        try:
            with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'openie'],
                               memory='4G') as client:
                ann = client.annotate(text)
        except:
            with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'openie'],
                               memory='4G', start_server='DONT_START') as client:
                ann = client.annotate(text)

        for sentence in ann.sentence:
            for triple in sentence.openieTriple:
                if len(subjects) != 0:
                    if len(subjects[0]) < len(triple.subject):
                        subjects = []
                        subjects.append(triple.subject)
                else:
                    subjects.append(triple.subject)

                if len(objects) != 0:
                    if len(objects[0]) < len(triple.object):
                        objects = []
                        objects.append(triple.object)
                else:
                    objects.append(triple.object)

            for triple in sentence.openieTriple:
                if len(relations) != 0:
                    if len(relations[0]) < len(triple.relation) \
                            and len(set(objects[0].split(' ')).intersection(set(triple.relation.split(' ')))) == 0 \
                            and len(set(subjects[0].split(' ')).intersection(set(triple.relation.split(' ')))) == 0:
                        relations = []
                        relations.append(triple.relation)
                    if len(relations[0]) > len(triple.relation):
                        main_relation = triple.relation
                else:
                    relations.append(triple.relation)
                    main_relation = triple.relation
                    if len(set(objects[0].split(' ')).intersection(set(triple.relation.split(' ')))) != 0 \
                            or len(set(subjects[0].split(' ')).intersection(set(triple.relation.split(' ')))) != 0:
                        relations = []
                        main_relation = ''

        files_to_delete = glob.glob('*.props')

        for file in files_to_delete:
            os.remove(file)
        return [' '.join(relations), ' '.join(subjects), ' '.join(relations), ' '.join(objects)]

    def part_of_speech_pipeline_stanza(self, sent):
        subjects = []
        objects = []
        relations = []
        main_relation = ''

        for word in sent.words:
            if word.upos == 'VERB' and 'VERB' not in [t.upos for t in relations]:
                relations.append(word)
                main_relation = word.lemma
                print('Add ' + str(word.text) + ' because ' + word.text + ' to relations')
            elif word.upos == 'VERB' and 'VERB' in [t.upos for t in relations]:
                objects.append(word)
                print('Add ' + str(word.text) + ' because ' + word.upos + ' to relations')
            elif word.upos in ['NOUN', 'ADP', 'ADV', 'ADJ'] and subjects != [] and relations != []:
                objects.append(word)
                print('Add ' + str(word.text) + ' because ' + word.upos + ' to objects')
            elif word.upos not in ['ADP', 'ADV', 'ADJ'] and relations == [] and subjects != []:
                subjects.append(word)
                print('Add ' + str(word.text) + ' because ' + word.upos + ' to subjects')
            elif word.upos in ['ADP', 'ADV', 'ADJ'] and 'VERB' not in [t.upos for t in relations] and subjects != []:
                relations.append(word)
                print('Add ' + str(word.text) + ' because ' + word.upos + ' to relations')
            elif relations == []:
                subjects.append(word)
                print('Add ' + str(word.text) + ' because ' + word.upos + ' to subjects')

        return [main_relation, ' '.join([str(token.text) for token in subjects]),
                ' '.join([str(token.lemma) for token in relations]), ' '.join([str(token.text) for token in objects])]

    def part_of_speech_pipeline_spacy(self, text):
        subjects = []
        objects = []
        relations = []
        main_relation = ''
        doc = self.nlp(text)

        for token in doc:
            print(str(token))
            print(str(token.pos_))

            if token.pos_ == 'VERB' and 'VERB' not in [t.pos_ for t in relations]:
                relations.append(token)
                main_relation = token.lemma_
                print('Add ' + str(token) + ' because ' + token.pos_ + ' to relations')
            elif token.pos_ == 'VERB' and 'VERB' in [t.pos_ for t in relations]:
                objects.append(token)
                print('Add ' + str(token) + ' because ' + token.pos_ + ' to relations')
            elif token.pos_ in ['NOUN', 'ADP', 'ADV', 'ADJ'] and subjects != [] and relations != []:
                objects.append(token)
                print('Add ' + str(token) + ' because ' + token.pos_ + ' to objects')
            elif token.pos_ not in ['ADP', 'ADV', 'ADJ'] and relations == [] and subjects != []:
                subjects.append(token)
                print('Add ' + str(token) + ' because ' + token.pos_ + ' to subjects')
            elif token.pos_ in ['ADP', 'ADV', 'ADJ'] and 'VERB' not in [t.pos_ for t in relations] and subjects != []:
                relations.append(token)
                print('Add ' + str(token) + ' because ' + token.pos_ + ' to relations')
            elif relations == []:
                subjects.append(token)
                print('Add ' + str(token) + ' because ' + token.pos_ + ' to subjects')
        return [main_relation, ' '.join([str(token) for token in subjects]),
                ' '.join([str(token.lemma_) for token in relations]), ' '.join([str(token) for token in objects])]

    def get_descendants(self, word, sent):
        descendants = []
        for dep_word in sent.words:
            if dep_word.head == word.id and dep_word.text != '.':
                descendants.append(dep_word)
                descendants.extend(self.get_descendants(dep_word, sent))
        return descendants

    def descendants(self, word, sent):

        descendants = self.get_descendants(word, sent)
        ret = []
        ids = []
        for i in descendants:
            if i.deprel != 'det':
                ids.append(i.id)
        ids.sort()
        for i in ids:
            for d in descendants:
                if d.id == i:
                    ret.append(d)
        return ret

    def sort_words(self, words):
        ret = []
        ids = []
        for i in words:
            ids.append(i.id)
        ids.sort()

        for i in ids:
            for w in words:
                if w.id == i:
                    ret.append(w)
        return ret

    def give_stanza_children(self, find, sent):
        ret = []
        for word in sent.words:
            if word.head == find.id and word.text != '.' and word.deprel != 'det':
                ret.append(word)
        return ret

    def dependency_tree_pipeline_stanza(self, sent):
        subjects = []
        objects = []
        relations = []
        orig_sentence = ''.join([word.text for word in sent.words])
        main_relation = ''

        for word in sent.words:
            was_before = True
            if word.deprel == 'root':
                main_relation = word.text
                num_of_children = len([t.text for t in self.give_stanza_children(word, sent)])
                object_start = num_of_children - 1  # point from which only object will be created
                found = False
                for child in reversed([t for t in self.get_descendants(word, sent)]):
                    if child.text != '.':
                        if child.deprel not in ['obj', 'nmod', 'compound', 'case', 'obj', 'obl',
                                                'iobj'] and child.deprel != 'prep' and not found:
                            object_start -= 1
                        elif child.deprel in ['obj', 'nmod', 'compound', 'case', 'obj', 'obl',
                                              'iobj'] or child.deprel == 'prep':
                            found = True;

                if (num_of_children == 2):
                    relations.append(word)
                    [subjects.append(tt) for tt in
                     self.get_descendants([t for t in self.give_stanza_children(word, sent)][0], sent)]
                    subjects.append(self.give_stanza_children(word, sent)[0])
                    [objects.append(tt) for tt in
                     self.get_descendants([t for t in self.give_stanza_children(word, sent)][1], sent)]
                    objects.append(self.give_stanza_children(word, sent)[1])
                    print('Children ' + str(self.give_stanza_children(word, sent)))
                    print('Descendandants ' + str(
                        self.get_descendants([t for t in self.give_stanza_children(word, sent)][0], sent)))

                else:
                    [subjects.append(tt) for tt in
                     self.get_descendants([t for t in self.give_stanza_children(word, sent)][0], sent)]
                    subjects.append([t for t in self.give_stanza_children(word, sent)][0])
                    print('Children ' + str(self.give_stanza_children(word, sent)))
                    print('Descendandants ' + str(self.get_descendants([t for t in self.give_stanza_children(word, sent)][0], sent)))
                    for i in range(1, object_start):
                        new_word = [t for t in self.give_stanza_children(word, sent)][i]
                        if orig_sentence.find(new_word.text) < orig_sentence.find(word.text) and was_before:
                            relations.append(new_word)
                        elif orig_sentence.find(new_word.text) > orig_sentence.find(word.text) and was_before:
                            was_before = False
                            relations.append(word)
                            relations.append(new_word)
                        else:
                            relations.append(new_word)
                    if was_before:
                        relations.append(word)

                    for i in range(object_start, num_of_children):
                        [objects.append(tt) for tt in
                         self.get_descendants([t for t in self.give_stanza_children(word, sent)][i], sent)]
                        objects.append([t for t in self.give_stanza_children(word, sent)][i])

        subjects = [t.text for t in self.sort_words(subjects)]
        objects = [t.text for t in self.sort_words(objects)]
        relations = [t.text for t in self.sort_words(relations)]
        return [main_relation, ' '.join(subjects), ' '.join(relations), ' '.join(objects)]

    def synonyms(self, text):
        syn = []
        for sublist in wn.synonyms(text):
            for i in sublist:
                syn.append(i)
        return syn

    def get_id(self, word):
        return word.id

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
