class ProjectDictionary:
    def __init__(self):
        self.data = {}
        self.number_of_sentences = 0

    def init_sentences(self, number_of_sentences):
        self.data = {}
        self.number_of_sentences = number_of_sentences
        self.data['ALL'] = {}
        self.data['ALL']['object'] = []
        self.data['ALL']['subject'] = []
        self.data['ALL']['relation'] = []
        for i in range(1,number_of_sentences+1):
            self.data[i] = {}
            self.data[i]['object'] = []
            self.data[i]['subject'] = []
            self.data[i]['relation'] = []

    def assign_object_to_sentence(self, sentence_number, object):
        for i in object:
            self.data[sentence_number]['object'].append(i)

    def assign_relation_to_sentence(self, sentence_number, relation):
        for i in relation:
            self.data[sentence_number]['relation'].append(i)

    def assign_subject_to_sentence(self, sentence_number, subject):
        for i in subject:
            self.data[sentence_number]['subject'].append(i)

    def assign_all_to_sentence(self, sentence_number, element):
        self.data[sentence_number]['subject'].append(element)
        self.data[sentence_number]['object'].append(element)
        self.data[sentence_number]['relation'].append(element)

    def assign_object_to_all_sentences(self, object):
        for i in range(self.number_of_sentences):
            self.data[i]['object'].append(object)

    def assign_subject_to_all_sentences(self, subject):
        for i in range(self.number_of_sentences):
            self.data[i]['subject'].append(subject)

    def assign_relation_to_all_sentences(self, relation):
        for i in range(self.number_of_sentences):
            self.data[i]['relation'].append(relation)

    def list_all_objects_of_sentence(self, sentence_number):
        return self.data[sentence_number]['object']

    def list_all_subjects_of_sentence(self, sentence_number):
        return self.data[sentence_number]['subject']

    def list_all_relations_of_sentence(self, sentence_number):
        return self.data[sentence_number]['relation']

    def list_all_objects(self):
        ret = []
        for i in range(self.number_of_sentences):
            for item in self.data[i]['object']:
                ret.append(item)
        return ret

    def list_all_subjects(self):
        ret = []
        for i in range(self.number_of_sentences):
            for item in self.data[i]['subject']:
                ret.append(item)
        return ret

    def list_all_relations(self):
        ret = []
        for i in range(self.number_of_sentences):
            for item in self.data[i]['relation']:
                ret.append(item)
        return ret

    def list_all_elements_of_sentence(self, number_of_sentence):
        return self.data[number_of_sentence]
