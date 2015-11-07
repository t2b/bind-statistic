#!/usr/bin/env python2

import rrdtool
import colorsys
from datetime import datetime
from os import path
import config
import re

KEYINDEX = {
    'Incoming Queries': [
        "A",
        "NS",
        "CNAME",
        "SOA",
        "NULL",
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
        "NULL",
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
        "MX",
        "TXT",
        "AAAA",
        "SRV",
        "DS",
        "DNSKEY",
        "ANY",
        "RRSIG",
        "NSEC",
        "!A",
        "!NS",
        "!CNAME",
        "!SOA",
        "!NULL",
        "!PTR",
        "!MX",
        "!TXT",
        "!AAAA",
        "!SRV",
        "!DS",
        "!DNSKEY",
        "!ANY",
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
        "UDP/IPv4 recv errors",
        "UDP/IPv6 recv errors",
        "TCP/IPv4 recv errors",
        "TCP/IPv6 recv errors",
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

DSNAME = {
    'A': 'A',
    'AAAA': 'AAAA',
    '!AAAA': 'notAAAA',
    '!A': 'notA',
    'ANY': 'ANY',
    '!ANY': 'notANY',
    'AXFR': 'AXFR',
    'CNAME': 'CNAME',
    '!CNAME': 'notCNAME',
    'DNSKEY': 'DNSKEY',
    '!DNSKEY': 'notDNSKEY',
    'DNSSEC NX validation succeeded': 'DNSSEC_NX_vali_succ',
    'DNSSEC validation attempted': 'DNSSEC_vali_attemp',
    'DNSSEC validation failed': 'DNSSEC_vali_fail',
    'DNSSEC validation succeeded': 'DNSSEC_vali_succ',
    'DS': 'DS',
    '!DS': 'notDS',
    'duplicate queries received': 'dupl_qry_rec',
    'EDNS(0) query failures': 'EDNS_query_fail',
    'FORMERR received': 'FORMERR_rec',
    'IPv4 notifies sent': 'v4_notifies_sent',
    'IPv4 NS address fetches': 'v4_NS_addr_fet',
    'IPv4 NS address fetch failed': 'v4_NS_addr_fet_fail',
    'IPv4 queries sent': 'v4_qry_sent',
    'IPv4 requests received': 'v4_req_rec',
    'IPv4 responses received': 'v4_resp_rec',
    'IPv6 notifies sent': 'v6_notifies_sent',
    'IPv6 NS address fetches': 'v6_NS_addr_fet',
    'IPv6 NS address fetch failed': 'v6_NS_addr_fet_fail',
    'IPv6 queries sent': 'v6_qry_sent',
    'IPv6 requests received': 'v6_req_rec',
    'IPv6 responses received': 'v6_resp_rec',
    'IXFR': 'IXFR',
    'lame delegations received': 'lame_deleg_rec',
    'MX': 'MX',
    '!MX': 'notMX',
    'NSEC': 'NSEC',
    'NS': 'NS',
    '!NS': 'notNS',
    '!NULL': 'notNULL',
    'NXDOMAIN': 'NXDOMAIN',
    'NXDOMAIN received': 'NXDOMAIN_rec',
    'other errors received': 'other_errors_rec',
    'PTR': 'PTR',
    '!PTR': 'notPTR',
    'queries caused recursion': 'qry_caused_recur',
    'queries dropped': 'qry_dropped',
    'queries resulted in authoritative answer': 'qry_res_in_auth',
    'queries resulted in non authoritative answer': 'qry_res_in_non_auth',
    'queries resulted in NXDOMAIN': 'qry_res_in_NXDOMAIN',
    'queries resulted in nxrrset': 'qry_res_in_nxrrset',
    'queries resulted in SERVFAIL': 'qry_res_in_SERVFAIL',
    'queries resulted in successful answer': 'qry_res_in_succ_ans',
    'queries with RTT 100-500ms': 'qry_with_RTT_100ms',
    'queries with RTT 10-100ms': 'qry_with_RTT_10ms',
    'queries with RTT < 10ms': 'qry_with_RTT_0ms',
    'queries with RTT > 1600ms': 'qry_with_RTT_1600ms',
    'queries with RTT 500-800ms': 'qry_with_RTT_500ms',
    'queries with RTT 800-1600ms': 'qry_with_RTT_800ms',
    'QUERY': 'QUERY',
    'query retries': 'query_retries',
    'query timeouts': 'query_timeouts',
    'requested transfers completed': 'reque_trans_compl',
    'requests with EDNS(0) received': 'req_with_EDNS_rec',
    'responses sent': 'resp_sent',
    'responses with EDNS(0) sent': 'resp_with_EDNS_sent',
    'RRSIG': 'RRSIG',
    'SERVFAIL received': 'SERVFAIL_rec',
    'SOA': 'SOA',
    '!SOA': 'notSOA',
    'SRV': 'SRV',
    '!SRV': 'notSRV',
    'TCP/IPv4 connections accepted': 'TCP4_con_accepted',
    'TCP/IPv4 connections established': 'TCP4_con_establ',
    'TCP/IPv4 recv errors': 'TCP4_recv_errors',
    'TCP/IPv4 sockets closed': 'TCP4_socks_closed',
    'TCP/IPv4 sockets opened': 'TCP4_socks_opened',
    'TCP/IPv6 connections accepted': 'TCP6_con_accepted',
    'TCP/IPv6 connections established': 'TCP6_con_establ',
    'TCP/IPv6 recv errors': 'TCP6_recv_errors',
    'TCP/IPv6 sockets closed': 'TCP6_socks_closed',
    'TCP/IPv6 sockets opened': 'TCP6_socks_opened',
    'TCP requests received': 'TCP_req_rec',
    'truncated responses received': 'truncated_resp_rec',
    'truncated responses sent': 'truncated_resp_sent',
    'TXT': 'TXT',
    '!TXT': 'notTXT',
    'UDP/IPv4 connections established': 'UDP4_con_establ',
    'UDP/IPv4 recv errors': 'UDP4_recv_errors',
    'UDP/IPv4 socket bind failures': 'UDP4_sock_bind_fail',
    'UDP/IPv4 sockets closed': 'UDP4_socks_closed',
    'UDP/IPv4 sockets opened': 'UDP4_socks_opened',
    'UDP/IPv6 connections established': 'UDP6_con_establ',
    'UDP/IPv6 recv errors': 'UDP6_recv_errors',
    'UDP/IPv6 socket bind failures': 'UDP6_sock_bind_fail',
    'UDP/IPv6 sockets closed': 'UDP6_socks_closed',
    'UDP/IPv6 sockets opened': 'UDP6_socks_opened',
    'update requests rejected': 'update_req_rejected',
    'UPDATE': 'UPDATE',
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
    name = name.replace("/", "_")
    if extension is not None:
        name = "{}.{}".format(name, extension)
    return path.join(directory, name)


def get_DSname(name):
    if name in DSNAME:
        return DSNAME[name]
    return name


def rrd_create(section, target_directory=None):
    if target_directory is None:
        target_directory = config.rrd_directory
    keys = KEYINDEX[section]

    rrd_parameter = [get_filename(section, target_directory, "rrd"),
                     "--step", "60",
                     "--start", '0']

    DStype = "COUNTER"
    if section == "Cache DB RRsets":
        DStype = "ABSOLUTE"

    for key in keys:
        DSname = get_DSname(key)
        rrd_parameter.append(
            "DS:{DSname}:{DStype}:90:U:U".format(DSname=DSname, DStype=DStype))

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


def rrd_update(section, content, timestamp="N", rrd_directory=None):
    if rrd_directory is None:
        rrd_directory = config.rrd_directory
    rrdfile = get_filename(section, rrd_directory, "rrd")
    if not path.isfile(rrdfile):
        rrd_create(section, rrd_directory)
    keys = list(set(content.keys()) & set(KEYINDEX[section]))
    missing_keys = set(content.keys()) - set(KEYINDEX[section])
    if missing_keys:
        print "missing keys in {}: {}".format(section, missing_keys)
    template = ":".join(map(lambda x: get_DSname(x), keys))
    values = ':'.join(map(lambda x: content[x], keys))

    rrdtool.update(rrdfile,
                   "--template", template,
                   "{timestamp}:{values}".format(timestamp=timestamp,
                                                 values=values))


def rrd_graph(section, duration="6h", width=800, height=300,
              target_directory=None):
    if target_directory is None:
        target_directory = config.graph_directory
    keys = KEYINDEX[section]

    outputfile = get_filename("{}-{}.png".format(section, duration),
                              target_directory)

    rrd_parameter = [outputfile,
                     "--start", "-{}".format(duration),
                     "--end", "now",
                     "-w", str(width),
                     "-h", str(height),
                     "-a", "PNG",
                     "--slope-mode",
                     "--title", "{} - {} - {}".format(config.servername,
                                                      section, duration),
                     "--watermark", str(datetime.now()),
                     "--vertical-label", "requests/s"]

    colors = rainbow(len(keys))
    for key in keys:
        DSname = get_DSname(key)
        rrdfile = get_filename(section, directory=config.rrd_directory,
                               extension="rrd")
        rrd_line = "DEF:{DSname}_{type}={rrdfile}:{DSname}:{type}"
        rrd_parameter.append(rrd_line.format(DSname=DSname,
                                             rrdfile=rrdfile,
                                             type="AVERAGE"))
        # rrd_parameter.append(rrd_line.format(DSname=DSname,
        #                                      rrdfile=rrdfile,
        #                                      type="MIN"))
        # rrd_parameter.append(rrd_line.format(DSname=DSname,
        #                                      rrdfile=rrdfile,
        #                                      type="MAX"))

    max_lable_length = max(map(len, keys))
    for i in xrange(len(keys)):
        key = keys[i]
        DSname = get_DSname(key)
        lable = "{lable:<{lablelength}}".format(lable=key,
                                                lablelength=max_lable_length)

        rrd_line1 = "LINE1:{DSname}_AVERAGE{color}:{lable}\\t"
        rrd_parameter.append(rrd_line1.format(DSname=DSname,
                                              color=colors[i],
                                              lable=lable))

        rrd_grpint = "GPRINT:{DSname}_AVERAGE:{type}:{lable}\: %7.2lf{space}"
        rrd_parameter.append(rrd_grpint.format(DSname=DSname,
                                               type="LAST",
                                               lable="Cur",
                                               space="\\t"))
        rrd_parameter.append(rrd_grpint.format(DSname=DSname,
                                               type="AVERAGE",
                                               lable="Avg",
                                               space="\\t"))
        rrd_parameter.append(rrd_grpint.format(DSname=DSname,
                                               type="MIN",
                                               lable="Min",
                                               space="\\t"))
        rrd_parameter.append(rrd_grpint.format(DSname=DSname,
                                               type="MAX",
                                               lable="Max",
                                               space="\\n"))
    rrdtool.graph(*rrd_parameter)


def rrd_info(section, target_directory=None):
    info = rrdtool.info(get_filename(section, config.rrd_directory, "rrd"))
    DS = []

    re1 = '(ds)'      # Word 1
    re2 = '(\\[)'     # Any Single Character 1
    re3 = '((?:[a-z][a-z0-9_]*))'     # Variable Name 1
    re4 = '(\\])'     # Any Single Character 2
    re5 = '(\\.)'     # Any Single Character 3
    re6 = '(index)'   # Word 2

    rg = re.compile(re1 + re2 + re3 + re4 + re5 + re6, re.IGNORECASE | re.DOTALL)
    for key in info.keys():
        m = rg.search(key)
        if m:
            # word1 = m.group(1)
            # c1 = m.group(2)
            var1 = m.group(3)
            # c2 = m.group(4)
            # c3 = m.group(5)
            # word2 = m.group(6)

            DS.append(var1)
    return DS


def rrd_tune(section, target_directory=None):
    if target_directory is None:
        target_directory = config.rrd_directory

    DSlist_rrdfile = set(rrd_info(section))
    DSlist_lib = set(map(get_DSname, KEYINDEX[section]))

    missingDS = DSlist_lib - DSlist_rrdfile

    rrd_parameter = [get_filename(section, target_directory, "rrd")]

    DStype = "COUNTER"
    if section == "Cache DB RRsets":
        DStype = "ABSOLUTE"


    for DSname in missingDS:
        rrd_parameter.append(
            "DS:{DSname}:{DStype}:90:U:U".format(DSname=DSname, DStype=DStype))

    for line in rrd_parameter:
        print line

    rrdtool.tune(*rrd_parameter)
