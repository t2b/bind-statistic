#!/usr/bin/env python2

from rrdlib import rrdlib


def main():
    for section in rrdlib.KEYINDEX:
        rrdlib.rrd_tune(section)
        return


if __name__ == "__main__":
    main()
