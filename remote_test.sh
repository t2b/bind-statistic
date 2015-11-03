#!/bin/sh

set -e

scp bind_*.py ttb.shack:
scp rrdlib/*.py ttb.shack:rrdlib/
ssh ttb.shack rm \*.png || true
ssh ttb.shack time /root/bind_graph.py
rm -v *.png || true
scp -C ttb.shack:\*.png .
rm -v *.rrd || true
scp -C ttb.shack:\*.rrd .
scp -C ttb.shack:named.stats .
eog Incoming_Queries-6h.png
