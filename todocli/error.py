import sys


def eprint(*args):
    print(*args, file=sys.stderr)


def error(msg, *args):
    eprint("Error:", msg.format(*args))
    sys.exit(-1)
