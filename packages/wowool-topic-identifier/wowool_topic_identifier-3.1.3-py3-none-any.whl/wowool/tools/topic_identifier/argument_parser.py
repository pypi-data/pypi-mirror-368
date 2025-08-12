from wowool.io.console.argument_parser import ArgumentParser as ArgumentParserBase

# fmt: off
class ArgumentParser(ArgumentParserBase):
    def __init__(self):
        """
        EyeOnText Wowool Topic Identifier.
        """
        super(ArgumentParserBase, self).__init__(prog="topics", description=ArgumentParser.__call__.__doc__)
        self.add_argument("-f", "--file", help="input file")
        self.add_argument("-i", "--input", help="input text")
        self.add_argument("-p", "--pipeline", help="processing pipeline", required = True)
        self.add_argument("-c", "--count", help="count of desired topics", type=int, default=5)
        self.add_argument("-t", "--threshold", help="threshold of desired topics [0-100]", type=int, default=0)
        self.add_argument("-m", "--topic_model", help="topic model file.")
        self.add_argument("--verbose", help="verbose print", default=False, action="store_true")
        self.add_argument("--cleanup", help="remove control characters", default=False, action="store_true")
        self.add_argument("-e", "--encoding", help="encoding", default="utf8")
        self.add_argument("--json", help="verbose output", default=False, action="store_true")
        self.add_argument("--raw_print", help="print nicely", default=False, action="store_true")
        self.add_argument("--lxware", help="location of the language files")

# fmt: on
