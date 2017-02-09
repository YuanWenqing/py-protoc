# coding: utf8

import os, sys

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from parse.loader import *

class Compiler:
  '''所有编译writer的基类'''
  def __init__(self, proto_dir, writer, type_resolver):
    self.proto_dir = proto_dir
    self.writer = writer
    self.type_resolver = type_resolver

  def addLine(self, line):
    if line:
      self.output = self.output + line
    self.output += '\n'

  def compile(self, arr):
    for item in arr:
      path = os.path.join(self.proto_dir, item)
      if os.path.isdir(path):
        self.compileDir(item)
      else:
        self.compileFile(item)

  def compileDir(self, d):
    path = os.path.join(self.proto_dir, d)
    arr = []
    for f in os.listdir(path):
      arr.append(os.path.join(d, f))
    self.compile(arr)

  def compileFile(self, f):
    proto = load(self.proto_dir, f)
    resolve(proto)
    for msg in proto.messages:
      if msg.isDeprecated():
        continue
      self.writer.onDataDef(msg)
      self.compileMsg(msg, self.__filterValidFields(msg))
    for enum in proto.enums:
      if enum.isDeprecated():
        continue
      self.writer.onDataDef(enum)
      self.compileMsg(enum, self.__filterValidFields(enum))

  def __filterValidFields(self, data_def):
    fields = []
    for field in data_def.fields:
      if field.isDeprecated():
        continue
      fields.append(field)
    return fields

  def compileMsg(self, msg, fields):
    pass

  def compileEnum(self, enum, fields):
    pass

class TypeResolver:
  '''处理type的映射和默认值'''

  def resolveType(self, field):
    '''处理field的type，返回`(type_text, default_value_text)`'''
    pass

  def resolveBaseType(self, base_type):
    '''处理protobuf中的base type，返回`(type_text, default_value_text)`'''
    pass

