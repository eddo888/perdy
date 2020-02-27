#!/usr/bin/env python3

import sys, re, os, unicodedata, xml.parsers.expat

from io import StringIO
from xml.dom import minidom

from Baubles.Colours import Colours
#from Perdy.pretty import *

tokens = [
	['&amp;' , '####amp####'],
	['&' , '&amp;'],
	['<' , '&lt;'],
	['>' , '&gt;'],
	['\"' , '&quot;'],
	#['\'' , '&apos;'],
	['####amp####' , '&amp;'],
]

def escapeData(data):
	for d in tokens:
		data = data.replace(d[0],d[1])
	return data

def doParse(
	input,
	output,
	colour=False,
	areturn=False,
	rformat=False,
	html=False,
	preserve=False,
	comments=False,
	fname=None,
	encoding=None,
	omitdecl=False
):
	myParser = MyParser(colour=colour, areturn=areturn, rformat=rformat, html=html, output=output, preserve=preserve, comments=comments, encoding=encoding, omitdecl=omitdecl)
	if True: #try:
		xml = input.read()
		myParser.parser.Parse(xml)
	if False: #except:
		printer = PrettyPrinter(colour=True, output=sys.stderr)
		sys.stderr.write('%s \n'%(fname or 'rendering as text '))
		printer.prettify(sys.exc_info())
		del printer
		if input != sys.stdin:
			input.seek(0)
		if output != sys.stdout:
			output.seek(0)
		output.write(input.read())
	del myParser
	return

def printXML(xml, colour=False, areturn=False, rformat=False,output=sys.stdout, encoding=None, omitdecl=False):
	myParser = MyParser(
		colour=colour, 
		rformat=rformat,
		areturn=areturn,
		output=output,
		encoding=encoding,
		omitdecl=omitdecl
	)
	myParser.parser.Parse(xml)
	del myParser
	return

class MyParser:
	indent = 0

	stateStartLast = 1
	stateEndLast = 2
	stateTextLast = 3
	stateCDataLast = 4
	stateCDataStart = 5
	stateCDataEnd = 6

	state = stateEndLast

	def __init__(self, colour=False, areturn=False, rformat=False, html=False, output=sys.stdout, preserve=False, comments=True, encoding=None, omitdecl=False):

		self.output = output
		self.lt='<'
		self.gt='>'
		self.amp='&'
		self.quot='\"'
		self.apos='\''
		self.lf='\n'
		self.indentChar = '	'
		self.preserve = preserve
		self.colours = Colours(colour=colour, html=html)
		self.encoding = encoding
		self.omitdecl = omitdecl
		
		if html:
			self.lt  ='&lt;'
			self.gt  ='&gt;'
			self.amp ='&amp;'
			self.quot='&quot;'
			self.apos='&apos;'
			self.lf  ='<br/>'
			self.indentChar = '&nbsp;&nbsp;&nbsp;&nbsp;'

		self.areturn = areturn
		self.rformat = rformat

		self.parser = xml.parsers.expat.ParserCreate(encoding=self.encoding)

		self.parser.StartElementHandler		  = self.startElementHandler
		self.parser.EndElementHandler			= self.endElementHandler
		self.parser.CharacterDataHandler		 = self.characterDataHandler
		self.parser.StartCdataSectionHandler	 = self.startCdataSectionHandler
		self.parser.EndCdataSectionHandler	   = self.endCdataSectionHandler
		self.parser.XmlDeclHandler			   = self.xmlDeclHandler
		self.parser.StartDoctypeDeclHandler	  = self.startDoctypeDeclHandler
		self.parser.EndDoctypeDeclHandler		= self.endDoctypeDeclHandler
		self.parser.ProcessingInstructionHandler = self.processingInstructionHandler

		if comments:
			self.parser.CommentHandler		   = self.commentHandler

		#		 Doctype => \&handle_doctype,
		#		 Proc => => \&handle_proc,

		self.leader = re.compile('(^\s+)')
		self.pattern = re.compile('(^\s+|\s+$)')
		self.lfCount = 0

		return

##parser.ElementDeclHandler(name, model)
##parser.AttlistDeclHandler(elname, attname, type, default, required)
##parser.UnparsedEntityDeclHandler(entityName, base, systemId, publicId, notationName)
##parser.EntityDeclHandler(entityName, is_parameter_entity, value, base, systemId, publicId, notationName)
##parser.NotationDeclHandler(notationName, base, systemId, publicId)
##parser.StartNamespaceDeclHandler(prefix, uri)
##parser.EndNamespaceDeclHandler(prefix)
##parser.DefaultHandler(data)
##parser.DefaultHandlerExpand(data)
##parser.NotStandaloneHandler()
##parser.ExternalEntityRefHandler(context, base, systemId, publicId)

	def close(self):
		if self.parser:
			self.parser.Parse('',1)
			del self.parser
		return
		
	def startElementHandler(self, name, attrs):
		if self.rformat:
			self.areturn = True

		if self.state == self.stateStartLast:
			self.output.write(''.join([
				self.colours.White,
				self.gt,
				self.colours.Off,
				self.lf
			]))
			self.output.flush()
			
		if self.preserve and self.lfCount > 2 and self.state == self.stateEndLast:
			self.output.write(self.lf)
			
		self.lfCount =0

		if ':' in name:
			(pre,ele) = tuple(name.split(':'))
		else:
			(pre,ele) = ('',name)
		
		self.output.write(''.join([
			(self.indent) * self.indentChar,
			self.colours.White,
			self.lt,
			self.colours.Teal,
			pre,
			self.colours.Off,
			':' if len(pre) else '',
			self.colours.Teal,
			ele,
			self.colours.Off
		]))
		self.output.flush()
		
		for attr in sorted(attrs.keys()):
			if self.areturn:
				self.output.write(''.join([
					self.lf,
					(self.indent+1) * self.indentChar,
				]))
			else:
				self.output.write(' ')
			self.output.write(''.join([
				self.colours.Green ,
				attr ,
				self.colours.Off ,
				self.colours.White ,
				'=' ,
				self.colours.Off ,
				self.quot ,
				self.colours.Purple ,
				escapeData(attrs[attr]) ,
				self.colours.Off ,
				self.quot ,
			]))
			self.output.flush()
			
		if len(attrs) > 0 and self.areturn:
			self.output.write(''.join([
				self.lf,
				(self.indent) * self.indentChar,
			]))
		self.indent += 1
		self.state = self.stateStartLast
		if self.rformat:
			self.rformat = False
			self.areturn = False
		return
			
	def endElementHandler(self, name):
		if ':' in name:
			(pre,ele) = tuple(name.split(':'))
		else:
			(pre,ele) = ('',name)

		self.indent -= 1
		if self.state == self.stateCDataEnd:
			if self.lfCount > 1:
				self.output.write(self.lf)
				self.lfCount = 0
				
		if self.state == self.stateStartLast:
			self.output.write(''.join([
				self.colours.White ,
				'/' ,
				self.gt ,
				self.colours.Off ,
				self.lf ,
			]))
			self.output.flush()
		elif self.state != self.stateTextLast and self.state != self.stateCDataEnd:
			self.output.write(''.join([
				(self.indent) * self.indentChar,
				self.colours.White ,
				self.lt ,
				self.colours.Off ,
				self.colours.White ,
				'/' ,
				self.colours.Teal,
				pre,
				self.colours.Off,
				':' if len(pre) else '',
				self.colours.Teal,
				ele ,
				self.colours.Off ,
				self.colours.White ,
				self.gt ,
				self.colours.Off ,
				self.lf ,
			]))
			self.output.flush()
		else:
			self.output.write(''.join([
				self.colours.White ,
				self.lt ,
				self.colours.Off ,
				self.colours.White ,
				'/' ,
				self.colours.Teal,
				pre,
				self.colours.Off,
				':' if len(pre) else '',
				self.colours.Teal,
				ele ,
				self.colours.Off ,
				self.colours.White ,
				self.gt ,
				self.colours.Off ,
				self.lf ,
			]))
			self.output.flush()
		self.state = self.stateEndLast
		return
		
	def characterDataHandler(self, data):
		data = str(unicodedata.normalize('NFKD', data).encode('ascii','ignore'))
		
		if not self.state == self.stateCDataStart and not self.state == self.stateCDataLast:
			data = escapeData(data)

		leader = ''
		match = self.leader.match(data)
		if match:
			leader = match.group(1)

		self.lfCount = self.lfCount + data.count('\n')
		if not self.state == self.stateTextLast and not self.state == self.stateCDataLast:
			data = self.leader.sub('', data)
		if len(data) == 0:
			return
		_data = '%s%s%s'%(
			self.colours.Red,
			data,
			self.colours.Off
		)
		if self.state == self.stateStartLast:
			self.output.write(''.join([
				self.colours.White,
				self.gt,
				self.colours.Off,
			]))
			if self.lfCount > 1:
				self.output.write(leader)
				self.output.write(self.lf)
			self.output.write(_data)
			self.state = self.stateTextLast
		elif self.state == self.stateCDataStart:
			if self.lfCount > 0:
				self.output.write(leader)
				self.output.write(self.lf)
			self.output.write(_data)
			self.state = self.stateCDataLast
		elif self.state == self.stateCDataLast:
			self.output.write(_data)
		elif self.state == self.stateTextLast:
			self.output.write(_data)
		elif self.state != self.stateEndLast:
			self.output.write(_data)

		return
	
	def commentHandler(self, data):
		if self.state == self.stateStartLast:
			self.output.write(''.join([
				self.colours.White ,
				self.gt ,
				self.colours.Off ,
				self.lf ,
			]))
			self.output.flush()
		self.output.write(''.join([
			(self.indent) * self.indentChar,
			self.colours.Orange ,
			self.lt ,
			'!--' ,
			data ,
			'--' ,
			self.gt ,
			self.colours.Off ,
			self.lf ,
		]))
		self.output.flush()
		self.state = self.stateEndLast
		return
		
	def startCdataSectionHandler(self):
		if not self.state == self.stateStartLast:
			self.output.write((self.indent) * self.indentChar)
		if self.state == self.stateStartLast:
			self.output.write(''.join([
				self.colours.White ,
				self.gt ,
				self.colours.Off ,
			]))
			self.output.flush()
		self.output.write(''.join([
			self.colours.White ,
			self.lt ,
			'![',
			self.colours.Green,
			'CDATA',
			self.colours.White,
			'[' ,
			self.colours.Off ,
		]))
		self.output.flush()
		self.state = self.stateCDataStart
		return
	
	def endCdataSectionHandler(self):
		self.output.write(''.join([
			self.colours.White ,
			']]' ,
			self.gt ,
			self.colours.Off ,
		]))
		self.output.flush()
		self.state = self.stateCDataEnd
		return
	
	def xmlDeclHandler(self, version, encoding, standalone):
		if self.omitdecl: return
		
		self.output.write(''.join([
			(self.indent) * self.indentChar,
			self.colours.White,
			self.lt ,
			'?',
			self.colours.Orange,
			'xml ' ,
			self.colours.Off ,
			self.colours.Green ,
			'version' ,
			self.colours.Off ,
			self.colours.White ,
			'=' ,
			self.quot ,
			self.colours.Off ,
			self.colours.Purple ,
			version ,
			self.colours.Off ,
			self.colours.White ,
			self.quot ,
			self.colours.Off ,
		]))
		self.output.flush()
		if encoding:
			self.output.write(''.join([
				self.colours.Green ,
				' encoding' ,
				self.colours.Off ,
				self.colours.White ,
				'=' ,
				self.colours.Off ,
				self.quot ,
				self.colours.Purple ,
				encoding ,
				self.colours.Off ,
				self.quot ,
			]))
			self.output.flush()
		self.output.write(''.join([
			self.colours.White ,
			'?' ,
			self.gt ,
			self.colours.Off ,
			self.lf ,
		]))
		self.output.flush()
		return
		
	def startDoctypeDeclHandler(self, doctypeName, systemId, publicId, has_internal_subset):
		if self.omitdecl: return
		
		self.output.write((self.indent) * self.indentChar)
		if not publicId:
			self.output.write(''.join([
				self.colours.White ,
				self.lt ,
				'!DOCTYPE ' ,
				self.colours.Off ,
				self.colours.White ,
				doctypeName ,
				self.colours.Off ,
				self.colours.White ,
				' SYSTEM ' ,
				self.quot ,
				self.colours.Off ,
				self.colours.Green ,
				systemId ,
				self.colours.Off ,
				self.colours.White ,
				self.quot ,
				self.quot ,
				self.gt ,
				self.colours.Off ,
				self.lf ,
			]))
			self.output.flush()
		else:
			self.output.write(''.join([
				self.colours.White ,
				self.lt ,
				'!DOCTYPE ' ,
				self.colours.Off ,
				self.colours.White ,
				doctypeName ,
				self.colours.Off ,
				self.colours.White ,
				' PUBLIC ' ,
				self.quot ,
				self.colours.Off ,
				self.colours.Green ,
				publicId ,
				self.colours.Off ,
				self.quot ,
				' ' ,
				self.quot ,
				self.colours.Green ,
				systemId ,
				self.colours.Off ,
				self.colours.White ,
				self.quot,
				self.gt ,
				self.colours.Off ,
				self.lf ,
			]))
			self.output.flush()
		return
		
	def endDoctypeDeclHandler(self):
		return
		
	def processingInstructionHandler(self, target, data):
		self.output.write(''.join([
			(self.indent) * self.indentChar,
			self.colours.White ,
			self.lt ,
			'?' ,
			target ,
			self.colours.Off ,
		]))
		self.output.flush()
		pn = re.compile('\s*(\S+)=[\'"]([^\'"]*)[\'"]\s*')
		b = pn.split(data)
		while '' in b: b.remove('')
		for i in range(len(b)/2):
			self.output.write(''.join([
				self.colours.Red ,
				b[2*i] ,
				self.colours.Off ,
				self.colours.White ,
				'=' ,
				self.colours.Off ,
				self.quot ,
				self.colours.Green ,
				b[2*i],
				self.colours.Off ,
				self.quot ,
			]))
			self.output.flush()
		self.output.write(''.join([
			self.colours.White ,
			'?' ,
			self.gt ,
			self.colours.Off ,
			self.lf ,
		]))
		self.output.flush()
		return

def main():
	
	xml=open('../test/Sample.xml').read()
	print(xml)
	print()
	
	sio = StringIO(xml)
	doParse(sio, sys.stdout, colour=True, rformat=True)
		
if __name__ == '__main__': main()


