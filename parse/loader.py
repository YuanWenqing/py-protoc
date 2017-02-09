# coding: utf8

import os, sys
from ply import lex, yacc
import logging

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from protodef.element import *
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
  proto.proto_dir = proto_dir
  proto.proto_file = proto_file
  return proto

def resolve(proto):
  '''处理import和field中的引用类型'''
  for item in proto.imports:
    import_proto = load(proto.proto_dir, item)
    resolve(import_proto)
    proto.datadefs.update(import_proto.datadefs)
    proto.imported_defs.update(import_proto.datadefs)
  for msg in proto.messages:
    for field in msg.fields:
      if field.type.kind == TypeKind.REF:
        if field.type.name not in proto.datadefs:
          raise Exception('Message %s: unresolved type %s in `%s`' % (msg.name, field.type.name, field))
        field.type.ref = proto.datadefs[field.type.name]
