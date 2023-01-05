#!/usr/bin/env python

import func

from config import Config
from time import sleep

config = Config()


def main():
    while 1:
        func.at_home()
        sleep(5)


if __name__ == '__main__':
    main()