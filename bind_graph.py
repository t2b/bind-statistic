#!/usr/bin/env python2

from rrdlib import rrdlib


def main():
    for section in rrdlib.KEYINDEX:
        if section in ['Resolver Statistics',
                       'Name Server Statistics',
                       'Socket I/O Statistics']:
            continue
        # rrd_create(section)
        # content = stats_dict[section]
        # rrd_update(section, content)
        for duration in ("6h", "12h", "1d", "7d", "30d", "180d", "1y"):
            rrdlib.rrd_graph(section, duration=duration)


if __name__ == "__main__":
    main()
