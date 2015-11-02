#!/bin/sh

scp bind_*.py ttb.shack: \
	&&  ssh ttb.shack /root/bind_graph.py \
	&& scp ttb.shack:\*.png . \
	&& eog Incoming_Queries.png
