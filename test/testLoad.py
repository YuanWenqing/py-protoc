#!/usr/bin/python
# coding: utf8

import os, sys
from optparse import OptionParser

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from parser import loader

if __name__ == '__main__':
  optParser = OptionParser()
  optParser.add_option("-r", "--root", dest="proto_dir", help="root proto dir", metavar="DIR")
  optParser.add_option("-f", "--file", dest="proto_file", help="input proto file", metavar="FILE")

  options, args = optParser.parse_args()

  if not options.proto_dir:
    optParser.print_help()
    optParser.error('no proto dir')
  if not options.proto_file:
    optParser.print_help()
    optParser.error('no proto file')

  proto = loader.load(options.proto_dir, options.proto_file)
  print proto
