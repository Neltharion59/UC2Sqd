class Fragment:
    def __init__(self, type, fragment_number, start_sentence):
        self.type = type
        self.start_sentence = start_sentence
        self.end_sentence = start_sentence
        self.fragment_number = fragment_number
        self.ended = False
        self.text = ''
