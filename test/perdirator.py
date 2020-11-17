#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, os, re, argparse, argcomplete, json, jsonpath, codecs, xmltodict

from datetime import datetime, date, time

sys.path.insert(0,'..')

from Perdy.pretty import prettyPrintLn, Style

xml = '''\
<root xmlns="myns">
	<child>child &amp; parent &lt;rocks&gt; forever</child>
</root>
'''

now = datetime.now()

source = xmltodict.parse(xml)

source['root']['datetime'] = now
source['root']['date'] = now.date()
source['root']['time'] = now.time()

for style in [ Style.JSON, Style.YAML, Style.XML]:
	prettyPrintLn(source, style=style)
	





