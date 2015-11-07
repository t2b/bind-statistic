#!/usr/bin/env python2

import jinja2
import config
from rrdlib import rrdlib
from collections import namedtuple


sectionhtmltemplate = """<!DOCTYPE html>
<head>
<title>{{servername}} Bind9 stats - {{ section }}</title>
</head>
<body>
<h1><a href="index.html">{{servername}} Bind9 stats</a></h1>
{% for sec in sectionnames %} <a href="{{sec.filename}}">{{sec.name}}</a> {% endfor %}
{% for graph in graphs %}
<h2>{{section}} - {{graph.duration}}</h2>
<img src="{{graph.file}}">
{% endfor %}
</body>
</html>"""


indexhtmltemplate = """<!DOCTYPE html>
<head>
<title>{{servername}} Bind9 stats</title>
</head>
<body>
<h1>{{servername}} Bind9 stats</h1>
{% for sec in sectionnames %} <a href="{{sec.filename}}">{{sec.name}}</a> {% endfor %}
{% for sec in sectionnames %}
<h2>{{sec.name}}</h2>
<a href="{{sec.filename}}"><img src="{{sec.graph}}"></a>
{% endfor %}
</body>
</html>"""


def generate_index_html(duration="6h"):
    sectionnames = []
    Sectionname = namedtuple("Sectionname", ["name", "filename", "graph"])
    for sectionname in config.sectionorder:
        name = sectionname
        filename = rrdlib.get_filename(sectionname, extension="html")
        graph = rrdlib.get_filename("{}-{}.png".format(sectionname, duration))
        sectionnames.append(Sectionname(name=name, filename=filename,
                                        graph=graph))

    templ = jinja2.Template(indexhtmltemplate)
    return templ.render(servername=config.servername, sectionnames=sectionnames)


def generate_section_html(section):
    sectionnames = []
    Sectionname = namedtuple("Sectionname", ["name", "filename"])
    for sectionname in config.sectionorder:
        sectionnames.append(Sectionname(sectionname,
                                        rrdlib.get_filename(sectionname,
                                                            extension="html")))

    graphs = []
    Graph = namedtuple("Graph", ["duration", "file"])
    for duration in config.timespans \
            + config.timespans_hourly \
            + config.timespans_daily:
        graphs.append(Graph(duration,
                            rrdlib.get_filename("{}-{}.png".format(section,
                                                                   duration))))

    templ = jinja2.Template(sectionhtmltemplate)
    return templ.render(servername=config.servername, section=section,
                        sectionnames=sectionnames, graphs=graphs)


def main():
    with open(rrdlib.get_filename("index.html",
                                  directory=config.graph_directory), "w") as f:
        f.write(generate_index_html("1d"))

    for section in rrdlib.KEYINDEX:
        filename = rrdlib.get_filename(section,
                                       directory=config.graph_directory,
                                       extension="html")
        with open(filename, "w") as f:
            f.write(generate_section_html(section))


if __name__ == "__main__":
    main()
