#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

'''
An XPath for JSON
 
A port of the Perl, and JavaScript versions of JSONPath
see http://goessner.net/articles/JsonPath/
 
Based on on JavaScript version by Stefan Goessner at:
        http://code.google.com/p/jsonpath/
and Perl version by Kate Rhodes at:
        http://github.com/masukomi/jsonpath-perl/tree/master
'''

import sys, os, re, argparse, argcomplete, json, jsonpath, codecs

from Perdy.eddo import *
from Perdy.pretty import *

horizon = buildHorizon()

parser = argparse.ArgumentParser()

parser.add_argument('-v','--verbose', action='store_true', help='show detailed output')
parser.add_argument('-a','--align',   action='store_true', help='align attributes')
parser.add_argument('-b','--bar',     action='store_true', help='bar between files')
parser.add_argument('-i','--inplace', action='store_true', help='format xml inplace')
parser.add_argument('-c','--colour',  action='store_true', help='show colour output')
parser.add_argument('-t','--text',    action='store_true', help='eval result as text')
parser.add_argument('-n','--name',    action='store_true', help='show file title')
parser.add_argument('-f','--flat',    action='store_true', help='output flat with no indent')
parser.add_argument('-s','--sort',    action='store_true', help='sort array lists')
parser.add_argument('-o','--output',  action='store',      help='output file')
parser.add_argument('-p','--path',    action='store',      help='evaluate comma seperated jsonpath')
parser.add_argument('file',           action='store',      help='file to parse', nargs='*')

argcomplete.autocomplete(parser)
args = parser.parse_args()

if args.verbose:
    prettyPrint(vars(args), colour=True, output=sys.stderr)

colour = args.colour

inplace = args.inplace
if inplace:
    colour = False
        
def dump(obj,output,colour):
    if args.text:
        if type(obj) == dict:
            for row in range(len(obj[list(obj.keys())[0]])):
                output.write('%s\n'%','.join([obj[x][row] or '' for x in list(obj.keys())]))
        elif type(obj) == list:
            output.write('\n'.join([str(x) for x in obj]))
        else:
            output.write('%s\n'%obj)
    elif args.flat:
        json.dump(obj,output,sort_keys=args.sort)
    elif colour:
        prettyPrint(obj,colour=colour,output=output,align=args.align,sorted=args.sort)
    else:
        json.dump(obj,output,indent=4,sort_keys=args.sort)
    return

def sort(object):
    if type(object) == dict:
        for key in list(object.keys()):
            if type(object[key]) == list:
                object[key] = sorted(object[key])
            else:
                sort(object[key])
    return

def parse(object,paths):
    results = dict()
    for path in paths:
        result = jsonpath.jsonpath(object,path)
        if result and type(result) == list and len(result) > 0:
            results[path] = result
    if len(paths) == 1:
        return results[paths[0]]
    return results

def main():
    global colour, inplace

    if args.output:
        output = codecs.open(args.output,'a',encoding='utf8')
    else:
        output = sys.stdout

    if args.file and len(args.file) > 0:
        
        for f in args.file:
            b='%s.bak'%f

            if inplace:
                sys.stderr.write('%s\n'%f)
                try:
                    os.remove(b)
                except:
                    None
                os.rename(f,b)
                fp = codecs.open(b,encoding='utf8')
            else:
                if args.bar:  sys.stderr.write('%s\n'%horizon)
                if args.name: sys.stderr.write('%s\n'%f)
                fp = codecs.open(f,encoding='utf8')

            obj = None
            try:
                obj = json.load(fp)
                if args.sort:
                    sort(obj)
                if args.path:
                    obj = parse(obj,args.path.split(','))
            except: 
                sys.stderr.write('%s\n'%sys.exc_info()[1])
                    
            fp.close()

            if inplace:
                fo = codecs.open(f,'w',encoding='utf8')
            elif args.output:
                fo = output
            else:
                fo = sys.stdout
            
            dump(obj,fo,colour)

            if inplace:
                fo.close()
    else:
        
        try:
            obj = json.load(sys.stdin)
            if args.sort:
                sort(obj)
            if args.path:
                obj = parse(obj,args.path.split(','))
            dump(obj,output,colour)
        except:
            sys.stderr.write('%s\n'%sys.exc_info()[1])

    if args.output:
        output.close()
        
    return

if __name__ == '__main__':main()




