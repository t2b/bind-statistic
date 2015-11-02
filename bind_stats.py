#!/usr/bin/env python2

import rrdtool

STATSFILE = "/root/named.stats"
KEYINDEX = {'Incoming Queries' : ["A",
                                  "NS",
                                  "CNAME",
                                  "SOA",
                                  "PTR",
                                  "MX",
                                  "TXT",
                                  "AAAA",
                                  "SRV",
                                  "DS",
                                  "DNSKEY",
                                  "IXFR",
                                  "AXFR",
                                  "ANY",
                                  ],
            "Outgoing Queries" : ["A",
                                  "NS",
                                  "CNAME",
                                  "SOA",
                                  "PTR",
                                  "MX",
                                  "TXT",
                                  "AAAA",
                                  "SRV",
                                  "DS",
                                  "DNSKEY",
                                  "ANY",
                                  ],
            "Zone Maintenance Statistics" : ["IPv4 notifies sent",
                                             "IPv6 notifies sent",
                                             ],
            'Resolver Statistics' : ["IPv4 queries sent",
                                     "IPv6 queries sent",
                                     "IPv4 responses received",
                                     "IPv6 responses received",
                                     "NXDOMAIN received",
                                     "SERVFAIL received",
                                     "FORMERR received",
                                     "other errors received",
                                     "EDNS(0) query failures",
                                     "truncated responses received",
                                     "lame delegations received",
                                     "query retries",
                                     "query timeouts",
                                     "IPv4 NS address fetches",
                                     "IPv6 NS address fetches",
                                     "IPv4 NS address fetch failed",
                                     "IPv6 NS address fetch failed",
                                     "DNSSEC validation attempted",
                                     "DNSSEC validation succeeded",
                                     "DNSSEC NX validation succeeded",
                                     "DNSSEC validation failed",
                                     "queries with RTT < 10ms",
                                     "queries with RTT 10-100ms",
                                     "queries with RTT 100-500ms",
                                     "queries with RTT 500-800ms",
                                     "queries with RTT 800-1600ms",
                                     "queries with RTT > 1600ms",
                                     ],
            'Cache DB RRsets': ["A",
                                "NS",
                                "CNAME",
                                "SOA",
                                "PTR",
                                "TXT",
                                "AAAA",
                                "DS",
                                "RRSIG",
                                "NSEC",
                                "DNSKEY",
                                "!A",
                                "!AAAA",
                                "!DS",
                                "NXDOMAIN",
                                ],
            'Incoming Requests': ["QUERY",
                                  "UPDATE",
                                  ],
            'Socket I/O Statistics': ["UDP/IPv4 sockets opened",
                                      "UDP/IPv6 sockets opened",
                                      "TCP/IPv4 sockets opened",
                                      "TCP/IPv6 sockets opened",
                                      "UDP/IPv4 sockets closed",
                                      "UDP/IPv6 sockets closed",
                                      "TCP/IPv4 sockets closed",
                                      "TCP/IPv6 sockets closed",
                                      "UDP/IPv4 socket bind failures",
                                      "UDP/IPv6 socket bind failures",
                                      "UDP/IPv4 connections established",
                                      "UDP/IPv6 connections established",
                                      "TCP/IPv4 connections established",
                                      "TCP/IPv6 connections established",
                                      "TCP/IPv4 connections accepted",
                                      "TCP/IPv6 connections accepted",
                                      "UDP/IPv6 recv errors",
                                      ],
            'Name Server Statistics': [
                                       "IPv4 requests received",
                                       "IPv6 requests received",
                                       "requests with EDNS(0) received",
                                       "TCP requests received",
                                       "update requests rejected",
                                       "truncated responses sent",
                                       "responses sent",
                                       "responses with EDNS(0) sent",
                                       "queries resulted in successful answer",
                                       "queries resulted in authoritative answer",
                                       "queries resulted in non authoritative answer",
                                       "queries resulted in nxrrset",
                                       "queries resulted in SERVFAIL",
                                       "queries resulted in NXDOMAIN",
                                       "queries caused recursion",
                                       "duplicate queries received",
                                       "queries dropped",
                                       "requested transfers completed",
                                       ]
            }


def get_last_stats():
    with open(STATSFILE) as f:
        stats = f.readlines()
    last_line = stats[-1]
    timestamp = last_line.split()[-1][1:-1]
    search_line = last_line.replace("---","+++")
    first_line_number = stats.index(search_line)
    return timestamp, stats[first_line_number:]


def build_dict(stats):
    section = None
    #key = None
    #value = None

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
        #line = line.split(maxsplit=1)
        line = line.split(" ", 1)
        key = line[1]
        value = line[0]
        main_dict[section][key] = value
    return main_dict


def rrd_create(section):
    keys = KEYINDEX[section]

    rrd_parameter = [section.replace(" ","_") + ".rrd", "--step", "60", "--start", '0']

    for key in keys:
        print(len(key),key)
	rrd_parameter.append("DS:" + key.replace(" ","_").replace("!","not") + ":COUNTER:90:U:U")
    rrd_parameter += [
                      "RRA:AVERAGE:0.5:1:780", # 1 min for 13 hours
                      "RRA:AVERAGE:0.5:5:600", # 5 min for 2 day 2 hours
                      "RRA:AVERAGE:0.5:30:600", # 30 min for 12.5 days
                      "RRA:AVERAGE:0.5:120:600", # 2 hours for 50 days
                      "RRA:AVERAGE:0.5:1440:4015", # 1 day for 732 days
                      "RRA:MAX:0.5:1:780", # 1 min for 13 hours
                      "RRA:MAX:0.5:5:600", # 5 min for 2 day 2 hours
                      "RRA:MAX:0.5:30:600", # 30 min for 12.5 days
                      "RRA:MAX:0.5:120:600", # 2 hours for 50 days
                      "RRA:MAX:0.5:1440:4015", # 1 day for 732 days
                      "RRA:MIN:0.5:1:780", # 1 min for 13 hours
                      "RRA:MIN:0.5:5:600", # 5 min for 2 day 2 hours
                      "RRA:MIN:0.5:30:600", # 30 min for 12.5 days
                      "RRA:MIN:0.5:120:600", # 2 hours for 50 days
                      "RRA:MIN:0.5:1440:4015", # 1 day for 732 days
                      ]
    rrdtool.create(*rrd_parameter)


def rrd_update(section, content, timestamp="N"):
    values = ':'.join(map(lambda x : content[x], KEYINDEX[section]))
    print values
    rrdtool.update(section.replace(" ","_") + ".rrd", timestamp + ":" + values)


def main():
    timestamp, stats = get_last_stats()
    print timestamp
    stats = map(lambda x: x.strip(), stats)

    stats_dict = build_dict(stats)

    for section in KEYINDEX:
        if section in ['Resolver Statistics', 'Name Server Statistics', 'Socket I/O Statistics']:
            continue
        print('#####', section)
	#rrd_create(section)
	content = stats_dict[section]
	rrd_update(section, content, timestamp)

#    for section in d:
#        print("###", section)
#        for key in d[section]:
#            print(key)


if __name__ == "__main__":
    main()
