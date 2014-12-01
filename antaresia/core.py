"""

Usage: antaresia [options] <path>
       antaresia -h | --help
       antaresia -v | --version

Options:
  -h, --help            Show this screen.
  -v, --version         Show version.
  -p PORT, --port=PORT  Port that will be used [default: 5000].

"""

from docopt import docopt

from antaresia.models import Server


def main():
    args = docopt(__doc__, version='antaresia v0.1')

    port = int(args['--port'])
    directory = args['<path>']
    server = Server(port=port)
    server.run(directory)