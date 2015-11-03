#!/usr/bin/env python2

import rrdtool
import colorsys
from datetime import datetime
from os import path

KEYINDEX = {
    'Incoming Queries': [
        "NS",
        "A",
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
    "Outgoing Queries": [
        "A",
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
    "Zone Maintenance Statistics": [
        "IPv4 notifies sent",
        "IPv6 notifies sent",
        ],
    'Resolver Statistics': [
        "IPv4 queries sent",
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
    'Cache DB RRsets': [
        "A",
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
    'Incoming Requests': [
        "QUERY",
        "UPDATE",
        ],
    'Socket I/O Statistics': [
        "UDP/IPv4 sockets opened",
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


def get_filename(name, directory="", extension=None):
    name = name.replace(" ", "_")
    if extension is not None:
        name = "{}.{}".format(name, extension)
    return path.join(directory, name)


def get_DSname(name):
    return name.replace(" ", "_").replace("!", "not")


def rrd_create(section, target_directory=""):
    keys = KEYINDEX[section]

    rrd_parameter = [get_filename(section, target_directory, "rrd"),
                     "--step", "60",
                     "--start", '0']

    for key in keys:
        rrd_parameter.append("DS:" + get_DSname(key) + ":COUNTER:90:U:U")

    rrd_parameter += ["RRA:AVERAGE:0.5:1:3000",  # 1 min for 30 hours
                      "RRA:AVERAGE:0.5:5:4320",  # 5 min for 15 days
                      "RRA:AVERAGE:0.5:30:3360",  # 30 min for 70 days
                      "RRA:AVERAGE:0.5:120:4800",  # 2 hours for 400 days
                      "RRA:AVERAGE:0.5:1440:4015",  # 1 day for 11 years
                      "RRA:MIN:0.5:1:3000",  # 1 min for 30 hours
                      "RRA:MIN:0.5:5:4320",  # 5 min for 15 days
                      "RRA:MIN:0.5:30:3360",  # 30 min for 70 days
                      "RRA:MIN:0.5:120:4800",  # 2 hours for 400 days
                      "RRA:MIN:0.5:1440:4015",  # 1 day for 11 years
                      "RRA:MAX:0.5:1:3000",  # 1 min for 30 hours
                      "RRA:MAX:0.5:5:4320",  # 5 min for 15 days
                      "RRA:MAX:0.5:30:3360",  # 30 min for 70 days
                      "RRA:MAX:0.5:120:4800",  # 2 hours for 400 days
                      "RRA:MAX:0.5:1440:4015",  # 1 day for 11 years
                      ]
    rrdtool.create(*rrd_parameter)


def rrd_update(section, content, timestamp="N", target_directory=""):
    rrdfile = get_filename(section, target_directory, "rrd")
    if not path.isfile(rrdfile):
        rrd_create(section, target_directory)
    keys = KEYINDEX[section]
    template = ":".join(map(lambda x: get_DSname(x), keys))
    values = ':'.join(map(lambda x: content[x], keys))

    rrdtool.update(rrdfile,
                   "--template", template,
                   timestamp + ":" + values)


def rrd_graph(section, duration="6h", width=800, height=300,
              target_directory=""):
    keys = KEYINDEX[section]

    outputfile = get_filename("{}-{}.png".format(section, duration),
                              target_directory)

    rrd_parameter = [outputfile,
                     "--start", "-{}".format(duration),
                     "--end", "now",
                     "-w", str(width),
                     "-h", str(height),
                     "-a", "PNG",
                     "--title", section + " - " + duration,
                     "--watermark", str(datetime.now()),
                     "--vertical-label", "requests/s"]

    colors = rainbow(len(keys))
    for key in keys:
        DSname = get_DSname(key)
        rrdfile = get_filename(section + ".rrd")
        rrd_parameter.append("DEF:_" + DSname + "=" + rrdfile + ":" + DSname +
                             ":AVERAGE")

    for i in xrange(len(keys)):
        key = keys[i]
        DSname = "_" + get_DSname(key)
        rrd_parameter.append("LINE1:" + DSname + colors[i] + ':' + key + '\\t')
        rrd_parameter.append("GPRINT:" + DSname + ":LAST:Cur\: %6.2lf\\t")
        rrd_parameter.append("GPRINT:" + DSname + ":AVERAGE:Avg\: %6.2lf\\t")
        rrd_parameter.append("GPRINT:" + DSname + ":MIN:MIN\: %6.2lf\\t")
        rrd_parameter.append("GPRINT:" + DSname + ":MAX:Max\: %6.2lf\\n")

    rrdtool.graph(*rrd_parameter)
