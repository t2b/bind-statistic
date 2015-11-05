#!/usr/bin/env python2

from rrdlib import rrdlib
import config


def main():
    for section in rrdlib.KEYINDEX:
        for duration in config.timespans_hourly:
            rrdlib.rrd_graph(section, duration=duration)


if __name__ == "__main__":
    main()
