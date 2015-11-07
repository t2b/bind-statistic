#!/bin/sh

# set -e

scp *.py ttb.shack:
scp rrdlib/*.py ttb.shack:rrdlib/
ssh ttb.shack rm \*.png || true
ssh ttb.shack time /root/bind_graph.py
ssh ttb.shack time /root/bind_graph_hourly.py
ssh ttb.shack time /root/bind_graph_daily.py
rm *.png || true
scp -C ttb.shack:\*.png .
rm *.rrd || true
scp -C ttb.shack:\*.rrd .
scp -C ttb.shack:named.stats .
eog Incoming_Queries-6h.png
