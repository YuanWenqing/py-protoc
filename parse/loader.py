# coding: utf8

import os
import logging
from ply import lex, yacc

from protodef.element import *
# import for ply(must)
from lexer import *
from grammar import *

class Loader:
  def __init__(self, proto_dir):
    self.proto_dir = proto_dir
    self.loaded = {}
    logging.basicConfig(level=logging.ERROR)
    errlog = logging.getLogger()
    self.lexer = lex.lex(nowarn=True, debug=False)
    self.parser = yacc.yacc(debug=True, write_tables=0, errorlog=errlog)

  def loadAbspath(self, abs_path):
    rel_path = os.path.relpath(abs_path, self.proto_dir)
    return self.loadRelpath(rel_path)

  def loadRelpath(self, rel_path):
    if not rel_path.endswith('.proto'):
      raise Exception('file name must end with .proto: %s' % rel_path)
    if rel_path in self.loaded:
      return self.loaded[rel_path]
    # read
    filepath = os.path.join(self.proto_dir, rel_path)
    #print '. load %s' % filepath
    with open(filepath) as pf:
      data = pf.read()
    # parse
    self.lexer.lineno = 1
    proto = self.parser.parse(data)
    proto.proto_dir = self.proto_dir
    proto.proto_file = rel_path
    # resolve
    self.loaded[rel_path] = proto
    self.resolve(proto)

    return proto

  def resolve(self, proto):
    '''处理import和field中的引用类型'''
    for item in proto.imports:
      import_proto = self.loadRelpath(item)
      proto.datadefs.update(import_proto.datadefs)
      proto.imported_defs.update(import_proto.datadefs)
      proto.import_protos.append(import_proto)
    for msg in proto.messages:
      for field in msg.fields:
        if field.type.kind == TypeKind.REF:
          if field.type.name not in proto.datadefs:
            raise Exception('Message %s: unresolved type %s in `%s`' % (msg.name, field.type.name, field))
          field.type.ref = proto.datadefs[field.type.name]
