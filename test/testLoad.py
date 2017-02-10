#!/usr/bin/python
# coding: utf8

import os, sys
rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from optparse import OptionParser

from parse.loader import *

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

  loader = Loader(options.proto_dir)
  proto = loader.loadRelpath(options.proto_file)
  print proto
  print 'imported:'
  for k in proto.imported_defs:
    print '%s: %s' % (k, proto.imported_defs[k])
