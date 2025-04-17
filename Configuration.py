class Configuration:
    def __init__(self):
        self.text = ''                     # Text to run
        self.system = 'system'             # Phrase/word which will be considered as "System"
        self.users = {}                    # All human entities, which will be considered as users. Format User(text,number_of_sentence)
        self.project_dictionary = None     # Dictionary of all subjects, relations and objects, which will forcefully rewrite result of pipeline
        self.enable_projects = False
        self.coreference = False           # If 2 words, which reference same entity(hyponym)
        self.steps = False                 # If calculate all possibilities for sentence and manually choose sentence by sentence
        self.engine = 'spacy'              # NLP engine which will be run spacy/stanza
        self.mode = 'POS'                  # Which NLP technique will be used: POS = Part of speech, DP = Dependency parsing, OIE = Open Information Extraction
        self.model = 'en_core_web_lg'      # Spacy NLP model
        self.fragments = False             # If manually inserted fragments will be used
        self.fragment_pattern = None        # If patterns to create fragments will be used
        self.parameters = False            # Automatically infer parameters
        self.pattern = None                # Which software desing pattern should be used None/'mvc'

