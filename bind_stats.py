#!/usr/bin/env python2

from rrdlib import rrdlib
import config


def get_last_stats():
    with open(config.named_stats) as f:
        stats = f.readlines()
    last_line = stats[-1]
    timestamp = last_line.split()[-1][1:-1]
    search_line = last_line.replace("---", "+++")
    first_line_number = stats.index(search_line)
    return timestamp, stats[first_line_number:]


def build_dict(stats):
    section = None

    main_dict = dict()

    for line in stats:
        if line[0] == "[":
            continue
        if line[:3] == "++ ":
            section = line[3:-3]
            main_dict[section] = dict()
            continue
        if line[:4] in ["+++ ", "--- "]:
            section = None
            continue
        line = line.split(" ", 1)
        key = line[1]
        value = line[0]
        main_dict[section][key] = value
    return main_dict


def main():
    timestamp, stats = get_last_stats()
    stats = map(lambda x: x.strip(), stats)

    stats_dict = build_dict(stats)

    for section in rrdlib.KEYINDEX:
        content = stats_dict[section]
        try:
            rrdlib.rrd_update(section, content, timestamp)
        except Exception, e:
            print "Error %s: %s" % (section, e)


if __name__ == "__main__":
    main()
