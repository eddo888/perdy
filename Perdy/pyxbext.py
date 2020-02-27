#!/usr/bin/env python3

import os,re,sys

from Baubles.Colours import Colours

colours = Colours(colour=True)
        
def directory(node):
    sys.stdout.write(''.join([
        colours.Orange,
        str(node),
        colours.Off,
        '\n'
    ]))
        
    for d in dir(node):
        if d.startswith('_'):
            continue
        v = getattr(node,d,None)
        
        if str(v).startswith('<bound method'):
            colour = colours.Purple
        else:
            colour = colours.Green
            
        sys.stdout.write(''.join([
            '\t',
            colours.Red,
            d,
            colours.Off,
            '=',
            colour,
            str(v),
            colours.Off,
            '\n'
        ]))

if __name__ == '__main__':
    class Teste(object):
        a = 'Aye'
        def b(self): return 'Bee'
    directory(Teste())
    #directory(colours)
    
colours.__del__()
