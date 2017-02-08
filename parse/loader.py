# coding: utf8

import os, sys
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
  parser = yacc.yacc(debug=False, write_tables=0, errorlog=errlog)

  lexer.lineno = 1
  proto = parser.parse(data)
  proto.proto_file = proto_file
  proto.filepath = filepath
  return proto

