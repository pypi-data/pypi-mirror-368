# basecmd

Boilerplate for the command line.

Classes inheriting from `BaseCmd` have a `self.log` attribute
that is a standard Python logger. A basic logging configuration to `sys.stdout`
is provided.

For command line options controlling the logging verbosity
and output to a log file, call the command with `-h` or `--help`.

Defaults for logging options can be also provided as environment variables
or in a `.emv` file:

* `LOG_LEVEL`: the logging verbosity, one of `error`, `warn`, `info`, or `debug`; default: `info`.
' `LOG_FILE`: path to a log file, defaults to the standard output for easy redirection.
* `LOG_FORMAT`: a standard Python logging format, defaults to `%(asctime).19s  %(message)s` when logging to a file or a terminal and `%(message)s` otherwise.

When logging to a terminal, the output is colored by log level.

## Example usage

```python
from basecmd import BaseCmd

class MyCmd(BaseCmd):

    def add_arguments(self):
        self.parser.add_argument('--foo',
            help='Custom command line option')

    def __call__(self):
        self.log.debug(self.options.foo)

if __name__ == '__main__':
    cmd = MyCmd
    cmd()
```
