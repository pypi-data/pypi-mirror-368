from basecmd import BaseCmd


class MyCmd(BaseCmd):
    "Demo command"

    def add_arguments(self):
        self.parser.add_argument("--foo", help="Custom command line option")

    def __call__(self):
        self.log.debug("Command line options: %s", self.options)


if __name__ == "__main__":
    cmd = MyCmd()
    cmd()
