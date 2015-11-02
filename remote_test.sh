#!/bin/sh

scp bind_*.py ttb.shack: \
	&&  ssh ttb.shack /root/bind_graph.py \
	&& rm -v *.png || true  \
	&& scp ttb.shack:\*.png . \
	&& rm -v *.rrd || true  \
	&& scp ttb.shack:\*.rrd . \
	&& eog Incoming_Queries-6h.png
