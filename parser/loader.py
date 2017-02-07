# coding: utf8

import os, sys
from optparse import OptionParser
from ply import lex, yacc
import logging

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

# import for ply(must)
from lexer import *
from grammar import *

def load(proto_dir, proto_file):
  if not proto_file.endswith('.proto'):
    raise Exception('file name must end with .proto')
  filepath = os.path.join(proto_dir, proto_file)
  with open(filepath) as pf:
    data = pf.read()
  logging.basicConfig(level=logging.ERROR)
  errlog = logging.getLogger()
  lexer = lex.lex(nowarn=True, debug=False)
  parser = yacc.yacc(debug=True, write_tables=0, errorlog=errlog)

  lexer.lineno = 1
  proto = parser.parse(data)
  proto.proto_file = proto_file
  proto.filepath = filepath
  return proto

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-r", "--root", dest="proto_dir", help="root proto dir", metavar="DIR")
  parser.add_option("-f", "--file", dest="proto_file", help="input proto file", metavar="FILE")

  options, args = parser.parse_args()

  if not options.proto_dir:
    parser.print_help()
    parser.error('no proto dir')
  if not options.proto_file:
    parser.print_help()
    parser.error('no proto file')

  proto = load(options.proto_dir, options.proto_file)
  print proto
