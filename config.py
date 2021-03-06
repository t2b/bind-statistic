#!/usr/bin/env python2


named_stats = "named.stats"

rrd_directory = "./"

graph_directory = "./"

timespans = ["6h", "12h", "1d"]
timespans_hourly = ["7d", "30d"]
timespans_daily = ["180d", "1y"]

servername = "dns.shack"

sectionorder = [
    "Incoming Queries",
    "Outgoing Queries",
    "Name Server Statistics",
    "Incoming Requests",
    "Resolver Statistics",
    "Socket I/O Statistics",
    "Zone Maintenance Statistics",
    "Cache DB RRsets",
]
