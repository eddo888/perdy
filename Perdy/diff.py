#!/usr/bin/env python3

import sys, os, re, json, argparse, time, pytz

from datetime import datetime, timedelta
from difflib import unified_diff, ndiff

from Baubles.Colours import Colours

#_____________________________________________________
def argue():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',   action='store_true')
    parser.add_argument('lhs')
    parser.add_argument('rhs')
    args = parser.parse_args()
    if args.verbose:
        json.dump(vars(args),sys.stderr,indent=4)
    return args

#_____________________________________________________
def sn(x):
    return '%s\n'%x

#_____________________________________________________
def modified(f):
    tzf = '%Y-%m-%d %H:%M:%S'
    if not f or not os.path.isfile(f):
        return datetime.now().strftime(tzf)
    lmt = os.path.getmtime(f)
    est = pytz.timezone('Australia/Sydney')
    gmt = pytz.timezone('GMT')
    gdt = datetime.utcfromtimestamp(lmt)
    gdt = gmt.localize(gdt)
    adt = est.normalize(gdt.astimezone(est))
    return adt.strftime(tzf)

#_____________________________________________________
def diff(lhs,rhs):

    if os.path.isfile(lhs):
        flhs = open(lhs).readlines()
    else:
        flhs = list(['%s\n'%x for x in lhs.split('\n')])
        lhs = '<'
        
    if os.path.isdir(rhs):
        rhs = '%s/%s'%(rhs,os.path.basename(lhs))
    if os.path.isfile(rhs):
        frhs = open(rhs).readlines()
    else:
        frhs = list(['%s\n'%x for x in rhs.split('\n')])
        rhs = '>'
        
    diffs = unified_diff(
            flhs,
            frhs,
            fromfile=lhs,
            tofile=rhs,
            fromfiledate=modified(lhs),
            tofiledate=modified(rhs)
    )

    colours = Colours()
    
    for line in list(diffs):
        if line.startswith('+'):
            sys.stdout.write(colours.Green)
        if line.startswith('-'):
            sys.stdout.write(colours.Red)
        sys.stdout.write(line)
        sys.stdout.write(colours.Off)
    return


#_____________________________________________________
def main():
    args = argue()
    diff(args.lhs.rstrip("/"), args.rhs.rstrip("/"))


#_____________________________________________________
def test():
    diff("one\ntwo\nthree","one\nthree\nfour")


#_____________________________________________________
if __name__ == '__main__': main()


