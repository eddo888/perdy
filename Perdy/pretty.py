#!/usr/bin/env python3

import sys, os, re, arrow, json, yaml, xmltodict, collections

from io import StringIO
from datetime import datetime
from inspect import isfunction
from enum import Enum, unique

from Baubles.Colours import Colours
from Perdy.diff import diff


#================================================================
@unique
class Style(Enum):
    '''
    defines the output styles for the prettyPrint
    '''
    JSON = 1
    YAML = 2
    XML  = 3

#================================================================
class PrettyPrinter(object):
    '''
    print the target object in a pretty way
    '''
    def __init__(self, 
        output=sys.stdout, 
        colour=True, 
        html=False, 
        align=False, 
        sorted=False, 
        verbose=False,
        ignore=False, 
        style=Style.JSON
    ):
        self.output = output
        self.align = align
        self.style = style
        self.sorted = sorted
        self.verbose = verbose
        self.ignore = ignore
        self.colours = Colours(colour=colour, html=html)
        self.walked = []

    def __del__(self):
        self.colours.__del__()
        
    #____________________________________________________________
    def prettify(self, d, indent='', parent=None):
        t='%s'%type(d)
        
        name = '%s'%d.__class__.__name__
        if self.verbose:
            sys.stderr.write('<%s type="%s"/>\n'%(name,t))
                        
        #........................................................
        if d is None:
            if self.style == Style.YAML:
                self.output.write(' ')
            self.output.write(self.colours.Off)
            if not self.style == Style.XML:
                self.output.write('null')
            self.output.write(self.colours.Off)
            
        #........................................................
        elif \
            t == 'org.python.core.PyDictionary' \
            or \
            type(d) == dict \
            or \
            type(d) == collections.OrderedDict \
        :
            if self.style == Style.JSON:
                self.output.write(''.join([
                    self.colours.Purple,
                    '{',
                    self.colours.Off,
                    '\n',
                ]))
            
            if self.style == Style.XML:
                
                if not parent:
                    self.output.write(''.join([
                        '%s'%indent,
                        self.colours.Off,
                        '<',
                        self.colours.Teal,
                        'xml',
                        self.colours.Off,
                        '>\n',
                    ]))

            if len(d) > 0:
                width = max([len(str(x)) for x in list(d.keys())])
            else:
                width = 0
                
            first = True
            keys = list(d.keys())
            
            if self.sorted:
                keys = list(sorted(keys))
                
            for i in list(range(len(keys))):
                key = keys[i]

                if self.align:
                    padding = width-len(key)
                else:
                    padding = 0

                if self.ignore and d[key] is None:
                    continue
                                       
                if self.style == Style.JSON:
                    self.output.write('%s  '%indent)                    
                    self.output.write('"')
                if self.style == Style.XML:
                    # @ and # tokens
                    self.output.write(''.join([
                        self.colours.Off,
                        '%s  '%indent,
                        '<',
                        self.colours.Teal,
                        '%s'%key,
                        self.colours.Off,
                        '>',
                    ]))
                if self.style == Style.YAML:
                    if type(parent) == list and not first:
                        self.output.write('  ')
                    if type(parent) in [dict, collections.OrderedDict]:
                        if first:
                            self.output.write('\n')
                        self.output.write('%s'%indent)

                first = False

                if type(d[key]) in [dict, collections.OrderedDict]:
                    self.output.write(self.colours.Teal)
                else:
                    self.output.write(self.colours.Green)
                
                if self.style != Style.XML:
                    self.output.write('%s'%key)
                self.output.write(self.colours.Off)

                if self.style == Style.YAML:
                    self.output.write(':%s'%(' '*padding))
                if self.style == Style.JSON:
                    self.output.write('"%s : '%(' '*padding))

                self.prettify(d[key], indent='%s  '%indent, parent=d)
                                
                if self.style == Style.YAML:
                    if i < (len(keys)-1):
                        self.output.write('\n')
                        if type(parent) == list:
                            self.output.write(indent[:-2])
                if self.style == Style.XML:
                    self.output.write(''.join([
                        self.colours.Off,
                        '%s  '%indent,
                        '</',
                        self.colours.Teal,
                        '%s'%key,
                        self.colours.Off,
                        '>\n',
                    ]))
                if self.style == Style.JSON:
                    if i < (len(keys) - 1):
                        self.output.write(',')
                    self.output.write('\n')
                    
            if self.style == Style.JSON:
                self.output.write('%s'%indent)
                self.output.write(self.colours.Purple)
                self.output.write('}')
                self.output.write(self.colours.Off)
                
            if self.style == Style.XML:
                if not parent:
                    self.output.write(''.join([
                        '%s'%indent,
                        self.colours.Off,
                        '</',
                        self.colours.Teal,
                        'xml',
                        self.colours.Off,
                        '>\n',
                    ]))
                    
        #........................................................
        elif \
            t == 'org.python.core.PyList' \
            or \
            type(d) == list \
        :
            if len(self.walked) == 0:
                self.bracket(d,'[',']','Teal','%s  '%indent)
            else:
                self.bracket(d,'','','Teal','  %s'%indent)
                
        #........................................................
        elif \
            t == 'org.python.core.PyTuple' \
            or \
            type(d) == tuple \
        :
            if len(self.walked) == 0:
                self.bracket(d,'(',')','Orange','  %s'%indent)
            else:
                self.bracket(d,'','','Orange','  %s'%indent)
                
        #........................................................
        elif \
            t == 'org.python.core.PyString' \
            or \
            type(d) == str \
        :
            if len(self.walked) == 0:
                if self.style == Style.YAML:
                    self.output.write(' ')
                if self.style == Style.JSON:
                    self.output.write('"')
                self.output.write(self.colours.Red)
                _new = '%s'%d.replace('\r','\\r').replace('\n','\\n')
                
                if self.style == Style.JSON:
                    _new = _new.replace('"','\\"')
                
                self.output.write(_new)
                self.output.write(self.colours.Off)
                if self.style == Style.JSON and len(self.walked) == 0:
                        self.output.write('"')

        #........................................................
        elif \
            t == 'org.python.core.PyBoolean' \
            or \
            type(d) == bool \
        :
            if self.style == Style.YAML:
                self.output.write(' ')
            self.output.write(self.colours.Red)
            self.output.write('%s'%str(d).lower())
            self.output.write(self.colours.Off)

        #........................................................
        elif \
            type(d) == datetime \
        :
            if self.style == Style.YAML:
                self.output.write(' ')
            self.output.write(self.colours.Red)
            a = arrow.get(d).to('AEST').naive
            self.output.write('"%s"'%str(a).lower())
            self.output.write(self.colours.Off)

        #........................................................
        else:
            if self.style == Style.YAML:
                self.output.write(' ')
            self.output.write(self.colours.Red)
            self.output.write('%s'%d)
            self.output.write(self.colours.Off)

        return
        
    #____________________________________________________________
    def bracket(self, d, start, end, colour, indent):
        if self.style == Style.JSON:
            self.output.write(''.join([
                getattr(self.colours,colour),
                '%s'%start,
                self.colours.Off,
            ]))
        if self.style == Style.XML:
            self.output.write(''.join([
                self.colours.Off,
                '\n%s<'%indent,
                self.colours.Teal,
                'list',
                self.colours.Off,
                '>',
            ]))    
        self.output.write('\n')
        
        if self.style == Style.YAML and len(indent) == 0:
            indent = '  '
             
        for i in range(len(d)):

            if self.style == Style.YAML:
                self.output.write('%s-'%indent[:-2])
                if type(d[i]) in [dict,collections.OrderedDict]:
                    self.output.write(' ')
                self.prettify(d[i], indent='%s'%indent, parent=d)
                
            if self.style == Style.XML:
                self.output.write(''.join([
                    self.colours.Off,
                    '%s  '%indent,
                    '<',
                    self.colours.Teal,
                    'item',
                    self.colours.Off,
                    '>',
                ]))
                self.prettify(d[i], indent='%s  '%indent, parent=d)  
                
            if self.style == Style.JSON:
                self.output.write('%s'%indent)
                self.prettify(d[i], indent='%s'%indent, parent=d)
                
            if len(self.walked) == 0 and i < (len(d) - 1):
                if self.style == Style.JSON:
                    self.output.write(',')
                if self.style == Style.YAML:
                    self.output.write('\n')
            if self.style == Style.XML:
                self.output.write(''.join([
                    '%s'%indent[:-2],
                    self.colours.Off,
                    '</',
                    self.colours.Teal,
                    'item',
                    self.colours.Off,
                    '>\n',
                ]))   
                
            if self.style == Style.JSON:
                self.output.write('\n')
                
        if self.style == Style.JSON:
            self.output.write('%s'%indent[:-2])
            self.output.write(getattr(self.colours,colour))
            self.output.write('%s'%end)
            self.output.write(self.colours.Off)
            
        if self.style == Style.XML:
            self.output.write(''.join([
                '%s'%indent,
                self.colours.Off,
                '</',
                self.colours.Teal,
                'list',
                self.colours.Off,
                '>\n',
            ]))    
        return



#================================================================
def prettyPrint(
    object, 
    output=sys.stdout, 
    colour=True, 
    align=False, 
    html=False, 
    sorted=False, 
    verbose=False, 
    ignore=False,
    style=Style.JSON
):
    printer = PrettyPrinter(
        output=output, 
        colour=colour, 
        align=align,
        html=html, 
        sorted=sorted, 
        verbose=verbose,
        ignore=ignore, 
        style=style
    )
    printer.prettify(object)
    printer.__del__()
    return

def prettyPrintLn(
    object, 
    output=sys.stdout, 
    colour=True, 
    align=False, 
    html=False, 
    sorted=False, 
    verbose=False,
    ignore=False, 
    style=Style.JSON
):
    prettyPrint(
        object, 
        output=output, 
        colour=colour, 
        align=align, 
        html=html, 
        sorted=sorted, 
        verbose=verbose,
        ignore=ignore, 
        style=style
    )
    output.write('\n')
    return
    
def test(prettyPyson):
    assert prettyPyson["hello"] == "th\"ere"
    assert prettyPyson["you"] in [0, '0'] 
    #assert type(prettyPyson["you"]) == int
    assert prettyPyson["object"]["isfalse"] in [False,'false']
    assert prettyPyson["object"]["istrue"] in [True,'true']
    assert prettyPyson["array"][0] == "one"
    assert prettyPyson["array"][1] in [2,'2']
    assert prettyPyson["array"][2] in [3.4,'3.4']
    assert prettyPyson["array"][3]["a"] == "A"
    assert prettyPyson["array"][3]["b"] == "B"
    return
    
#================================================================
def main():
        
    js = """\
{
  "array" : [
    "one",
    2,
    3.4,
    {
      "a" : "A",
      "b" : "B"
    },
    {
      "c" : "C"
    },
    {
      "d" : [
        "all",
        "for",
        "one"
      ]
    }
  ],
  "hello" : "th\\"ere",
  "nothing" : null,
  "object" : {
    "isfalse" : false,
    "istrue" : true
  },
  "you" : 0
}"""

    ym="""\
array:
  - one
  - 2
  - 3.4
  - a: A
    b: B
  - c: C
  - d:
      - all
      - for
      - one
hello: th"ere
nothing: null
object:
  isfalse: false
  istrue: true
you: 0"""

    nn='''{
  "child" : {
    "notNull" : "i am not null"
  },
  "children" : [
    {
      "notNull" : "i am not null"
    }
  ],
  "notNull" : "i am not null"
}'''


    xml="""
"""

    pyson = json.loads(js)
    #print pyson
    #print
    
    so = StringIO()
    printer = PrettyPrinter(output=so, colour=False, sorted=True)
    printer.prettify(pyson)
    prettyJson = so.getvalue()
    #print prettyJson 
    printer.__del__()

    diff(js, prettyJson)
    assert prettyJson == js
        
    prettyPyson = json.loads(prettyJson)
    test(prettyPyson)
    
    if True: 
        prettyPrint(prettyPyson)
        print()
        print()
        
        prettyPrint(prettyPyson, verbose=False, style=Style.YAML)
        print()
        print()
    
    so = StringIO()
    printer = PrettyPrinter(output=so, colour=False, sorted=True, style=Style.YAML)
    printer.prettify(pyson)
    prettyYaml = so.getvalue()
    #print prettyYaml

    prettyPyson = yaml.load(prettyYaml)
    diff(ym, prettyYaml)
    assert prettyYaml == ym
    test(prettyPyson)
    
    so = StringIO()
    printer = PrettyPrinter(output=so, colour=False, style=Style.XML)
    printer.prettify(pyson)
    prettyXml = so.getvalue()
    #printXML(prettyXml)
    
    prettyPyson = xmltodict.parse(prettyXml)['xml']
    #prettyPrint(prettyPyson)
    #diff(ym, prettyYa)
    #assert prettyYaml == ym
    #test(prettyPyson)
    
    withNulls = dict(
        notNull='i am not null',
        isNull=None,
        child=dict(
            notNull='i am not null',
            isNull=None,
        ),
        children=[
            dict(
                notNull='i am not null',
                isNull=None,
            ),
        ],
    )
    
    so = StringIO()
    notNullPrinter = PrettyPrinter(output=so, colour=False, ignore=True, style=Style.JSON)
    notNullPrinter.prettify(withNulls)
    prettyNotNull = so.getvalue()
    print(prettyNotNull)
    #assert(prettyNotNull==nn)
    
    if False:
        print()
        prettyPrint(pyson, verbose=False, style=Style.XML, colour=True)
        
   
    if False:
        print()
        print()
        dad = TestPrettyObject()
        dad.name = 'Dad'
    
        mum = TestPrettyObject(name='Mum')
        mum.partner = dad
        dad.partner = mum
        
        son = TestPrettyObject(name='Son')
        sis = TestPrettyObject(name='Sis')
    
        dad.children = [son]    
        dad.children.append(sis)
        
        mum.children.append(son)
        mum.children.append(sis)
    
        printer = PrettyPrinter(colour=True,verbose=False)
        printer.prettify(dad)
        printer.__del__()
        
    return

#================================================================
if __name__ == '__main__': main()

