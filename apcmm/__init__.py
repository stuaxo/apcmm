from os.path import splitext
from sys import argv

from mnd.dispatch import Dispatcher, handle

midi = Dispatcher()

class GridButton(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class ClipButton(GridButton):
    def __init__(self, x, y):
        GridButton.__init__(self, x, y)


def read_config(config):
    print "read config ", splitext(config)

    exec "import %s" % splitext(config)[0]
    


def main():
    if len(argv) == 1:
        config = "config.py"
    else:
        config = argv[1]

    read_config(config)


if __name__=="__main__":
    main()
