#!/usr/bin/env python2

import rrdtool
import colorsys

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


def rainbow(n):
    colors = []
    for i in xrange(n):
        rgb = colorsys.hsv_to_rgb(float(i)/n, 1, 1)
        rgb = map(lambda x: int(x*255), rgb)
        rgb = "#{:02x}{:02x}{:02x}".format(*rgb)
	colors.append(rgb.upper()) 
    return colors
        

def rrd_graph(section):
    keys = KEYINDEX[section]

    from datetime import datetime
    rrd_parameter = [section.replace(" ","_") + ".png", "--start", "-2h", "-w 800", "-h 300", "--title", section, "--watermark", str(datetime.now()) ]

    colors = rainbow(len(keys))
    for key in keys:
	rrd_parameter.append("DEF:_" + key.replace(" ","_").replace("!","not") + "=" + section.replace(" ","_") + ".rrd:" + key.replace(" ","_").replace("!","not") + ":AVERAGE")

    for i in xrange(len(keys)):
        key = keys[i]
        rrd_parameter.append("LINE1:_" + key.replace(" ","_").replace("!","not") + colors[i] + ':' + key + '\\t')
	rrd_parameter.append("GPRINT:_" + key.replace(" ","_").replace("!","not") + ":LAST:Cur\: %6.2lf\\t")
	rrd_parameter.append("GPRINT:_" + key.replace(" ","_").replace("!","not") + ":AVERAGE:Avg\: %6.2lf\\t")
	rrd_parameter.append("GPRINT:_" + key.replace(" ","_").replace("!","not") + ":MAX:Max\: %6.2lf\\n")

    rrdtool.graph(*rrd_parameter)

def main():
    for section in KEYINDEX:
        if section in ['Resolver Statistics', 'Name Server Statistics', 'Socket I/O Statistics']:
            continue
        print('#####', section)
	#rrd_create(section)
	#content = stats_dict[section]
	#rrd_update(section, content)
	rrd_graph(section)

#    for section in d:
#        print("###", section)
#        for key in d[section]:
#            print(key)


if __name__ == "__main__":
    main()
