#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, sys, re, operator, argparse, argcomplete

from Baubles.Colours import Colours
from Perdy.eddo import *
from Perdy.pretty import prettyPrint

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--verbose', action='store_true' )
parser.add_argument('-H', '--html',    action='store',            help='output as html to file')
parser.add_argument('-o', '--orange',  action='store', nargs='*', help='pattern')
parser.add_argument('-g', '--green',   action='store', nargs='*', help='pattern')
parser.add_argument('-b', '--blue',    action='store', nargs='*', help='pattern')
parser.add_argument('-t', '--teal',    action='store', nargs='*', help='pattern')
parser.add_argument('-p', '--purple',  action='store', nargs='*', help='pattern')
parser.add_argument('-r', '--red',     action='store', nargs='*', help='pattern')
parser.add_argument('file',            action='store', nargs='*', help='files or stdin')

argcomplete.autocomplete(parser)
args = parser.parse_args()

if args.verbose:
    prettyPrint(vars(args),colour=True)

replacements = []

mycolours = Colours(colour=True, html=args.html)

def replace(colour,patterns):
    global replacements
    if not patterns:
        return
    for pattern in patterns:
        matched = re.compile(pattern)
        matcher = re.compile('(.*)(%s)(.*)'%pattern)
        colour = getattr(mycolours,colour)
        replacements.append((matched,matcher,colour))
    return

def colourize(input):
    global replacements
    while True:
        line = input.readline()
        if not line:
            break
        for (matched,matcher,colour) in replacements:
            match = matcher.match(line)
            if match:
                last = len(match.groups())
                leader = match.group(1)
                value = match.group(2)
                tailer = match.group(last)
                submatch = matched.match(value)
                
                if submatch and len(submatch.groups()) > 0:
                    subvalue = submatch.group(1)
                    value = value.replace(subvalue,'%s%s%s'%(colour,subvalue,mycolours.Off))
                else:
                    value = '%s%s%s'%(colour,value,mycolours.Off)
                line = '%s%s%s\n'%(
                    leader,
                    value,
                    tailer
                )

        if args.html:
            line = '%s<br/>'%line

        output.write(line)
    return

def main():
    global replacements,output
    replace('Orange', args.orange)
    replace('Green', args.green)
    replace('Blue', args.blue)
    replace('Teal', args.teal)
    replace('Purple', args.purple)
    replace('Red', args.red)

    if args.verbose:
        sys.stderr.write('%s\n'%replacements)

    output = sys.stdout
    if args.html:
        output = open(args.html,'w')
        output.write('<html><body>\n')

    if args.file:
        for file in args.file:
            if args.html:
                output.write('<hr/>\n')
                output.write('<h1>%s</h1>\n'%file)
            fp = open(file)
            colourize(fp)
            fp.close()
    else:
        colourize(sys.stdin)

    if args.html:
        output.write('</body></html>\n')
        output.close()

    return

if __name__ == '__main__': main()
