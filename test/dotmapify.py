#!/usr/bin/env python3

import os, re, sys, json

from dotmap import DotMap

sys.path.insert(0, '..')
from Perdy.pretty import prettyPrintLn

doc = DotMap(dict(root='opml', nodes=[]))

prettyPrintLn(doc)

