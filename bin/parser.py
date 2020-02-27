#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

# http://mikekneller.com/kb/python/libxml2python/part1

import re,sys,os,codecs
import argparse, argcomplete, io

from Perdy.eddo import *
from Perdy.parser import *
from Perdy.pretty import *

horizon = buildHorizon()

def argue():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-?',              action='help',       help='show this help')
    parser.add_argument('-v','--verbose',  action='store_true', help='show detailed output')
    parser.add_argument('-c','--colour',   action='store_true', help='show output in colour')
    parser.add_argument('-b','--bar',      action='store_true', help='put horizontal bar inbetween')
    parser.add_argument('-n','--nobak',    action='store_true', help='when processing inplace, dont backup file')
    parser.add_argument('-i','--inplace',  action='store_true', help='format xml inplace')
    parser.add_argument('-r','--root',     action='store_true', help='indent root attributes')
    parser.add_argument('-a','--attr',     action='store_true', help='indent all attributes')
    parser.add_argument('-t','--title',    action='store_true', help='show title of document')
    parser.add_argument('-p','--preserve', action='store_true', help='preserve line spacing')
    parser.add_argument('-s','--strip',    action='store_true', help='strip comments')
    parser.add_argument('-x','--omitdecl', action='store_true', help='omit xml declaration')
    parser.add_argument('-o','--output',   action='store',      help='output to xml file')
    parser.add_argument('-H','--html',     action='store',      help='output in HTML file')
    parser.add_argument('-e','--encoding', action='store',      choices=['UTF-8','UTF-16','ISO-8859-1','ASCII'])
    parser.add_argument('file',            action='store',      help='files to format', nargs='*')

    argcomplete.autocomplete(parser)
    return parser.parse_args()

def main():
    args = argue()
    
    colour = args.colour
    areturn = args.attr
    rformat = args.root

    output = sys.stdout

    foutput = args.output
    if foutput:
        colour = False
        print(foutput)
        output = codecs.open(foutput,'w',encoding=args.encoding)

    houtput = args.html
    if houtput:
        html = True
        print(houtput)
        output = codecs.open(houtput,'w',encoding=args.encoding)
    else:
        html = False
    
    inplace = args.inplace
    if inplace:
        foutput = None
        colour = False

    title = args.title

    preserve = args.preserve

    comments = not args.strip

    if args.file:
        for arg in args.file:
            f = arg
            b='%s.bak'%f

            if inplace:
                try:
                    os.remove(b)
                except:
                    None
                os.rename(f,b)
                output = codecs.open(f,'w',encoding=args.encoding)
                fp = codecs.open(b,encoding=args.encoding)
                print(f)
            else:
                if args.bar:
                    print(horizon)
                if title:
                    print(f)

                fp = codecs.open(arg,encoding=args.encoding)

            doParse(
                fp,
                output,
                colour=colour,
                areturn=areturn,
                rformat=rformat,
                html=html,
                preserve=preserve,
                comments=comments,
                fname=arg,
                encoding=args.encoding,
                omitdecl=args.omitdecl
            )

            fp.close()

            if inplace:
                output.close()
                if args.nobak:
                    os.unlink(b)

    else:
        fp = io.StringIO(sys.stdin.read())
        doParse(
            fp,
            output,
            colour=colour,
            areturn=areturn,
            rformat=rformat,
            html=html,
            preserve=preserve,
            comments=comments,
            fname='stdin',
            encoding=args.encoding,
            omitdecl=args.omitdecl
        )
        fp.close()
        
    if foutput:
        output.close()

    return
    
if __name__ == '__main__': main()


