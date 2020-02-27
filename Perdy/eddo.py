#!/usr/bin/env python3

# $Date$
# $Revision$
# $Author$
# $HeadURL$
# $Id$


import sys,os

replacements = {
  '\n' : '\\n',
  '\\"'  : '&quot;',
  '"'  : '\\"',
  '&quot;' : '\\"'
}

def getColumns():
  if 'COLUMNS' in os.environ:
    return int(os.environ['COLUMNS'])
  return 80
  
def buildHorizon(char='-'):
  return getColumns() * char

def fixString(dirty):
  clean = dirty
  for replacement in list(replacements.keys()):
    clean = clean.replace(replacement,replacements[replacement])
  return clean


