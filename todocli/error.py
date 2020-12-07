import sys


def error(msg, *args, **kwargs):
    print('Error:', msg.format(*args), file=sys.stderr, **kwargs)
    sys.exit(-1)
