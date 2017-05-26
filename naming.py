#!/usr/bin/python
# coding: utf8

import os, sys
from optparse import OptionParser

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from parse.loader import *
from compilers.naming import *

if __name__ == '__main__':
  optParser = OptionParser()
  optParser.add_option("-p", "--proto", dest="proto", help="proto dir path", metavar="DIR")
  optParser.add_option("-o", "--out", dest="out", help="out dir", metavar="DIR")
  optParser.add_option("-i", "--input", dest="input", action='append', help="input proto, dir or file, at least one", metavar="FILE")
  optParser.add_option("-s", "--skip", dest="skip", action='append', help="skip proto, dir or file", metavar="FILE")

  options, args = optParser.parse_args()

  if not options.proto:
    optParser.print_help()
    optParser.error('no proto dir')
  if not options.out:
    optParser.print_help()
    optParser.error('no out dir')
  if not options.input:
    optParser.print_help()
    optParser.error('no input')

  protoDir = os.path.abspath(options.proto)
  outDir = os.path.abspath(options.out)
  inputs = [os.path.abspath(f) for f in options.input]
  skips = []
  if options.skip:
    skips = [os.path.abspath(f) for f in options.skip]

  loader = Loader(protoDir)
  resolver = NamingResolver()
  writer = NamingWriter(outDir, '.java')
  compiler = NamingCompiler(loader, writer, resolver)
  compiler.addSkip(skips)
  compiler.compile(inputs)
