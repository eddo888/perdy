#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, os, re, argparse, argcomplete, json, jsonpath, codecs, xmltodict

sys.path.insert(0,'..')

from Perdy.pretty import prettyPrintLn, Style

xml = '''\
<root>
	<child>child &amp; parent &lt;rocks&gt; forever</child>
</root>
'''

source = xmltodict.parse(xml)



for style in [ Style.JSON, Style.YAML, Style.XML]:
	prettyPrintLn(source, style=style)
	





