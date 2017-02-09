# coding: utf8

from base import *

class TsCompiler(Compiler):

  def compileMsg(self, msg, fields):
    self.beforeMsg(msg)
    for field in fields:
      self.compileMsgField(field)
    self.afterMsg(msg)

  def beforeMsg(self, msg):
    if msg.comment:
      self.writer.writeline('/**')
      self.writer.writeline(msg.comment)
      self.writer.writeline(' */')
    self.writer.writeline('export interface %s {' % msg.name)

  def afterMsg(self, msg):
    self.writer.writeline('}')
    self.writer.writeline()

  def compileMsgField(self, field):
    if field.comment:
      self.writer.writeline('  /**')
      self.writer.writeline(field.comment)
      self.writer.writeline('   */')
    field_type, default_value = self.type_resolver.resolveType(field)
    self.writer.writeline('  %s = %s;' % (field.name, field_type))

  def compileEnum(self, enum, fields):
    self.beforeEnum(enum)
    for field in fields:
      self.writer.writeline('  %s = %d;' % (field.name, field.number))
    self.afterEnum(enum)

  def beforeEnum(self, enum):
    if enum.comment:
      self.writer.writeline('/**')
      self.writer.writeline(enum.comment)
      self.writer.writeline(' */')
    self.writer.writeline('enum %s {' % enum.name)

  def afterEnum(self, enum):
    self.writer.writeline('}')
    self.writer.writeline()


class TsResolver(TypeResolver):
  BASE_TYPE_MAP = {
    'int64': ('number', '0'),
    'int32': ('number', '0'),
    'string': ('string', '""'),
    'bool': ('boolean', 'false'),
    'float': ('number', '0'),
    'double': ('number', '0')
  }

  def resolveType(self, field):
    field_type = field.type
    if field_type.kind == TypeKind.BASE:
      type_name, default_value = self.resolveBaseType(field_type.name)
    else:
      data_def = field_type.ref
      if isinstance(data_def, Enum):
        type_name, default_value = self.resolveBaseType('int32')
      else:
        type_name = canonical_name(data_def)
        default_value = 'null'
    if field.isRepeated():
      type_name = 'Array<%s>' % type_name
      default_value = 'null'
    return (type_name, default_value)

  def resolveBaseType(self, base_type):
    '''处理protobuf中的base type到指定语言的映射'''
    return TsResolver.BASE_TYPE_MAP[base_type]


class TsWriter(Writer):
  '''每个proto一个文件'''

  def onProto(self, proto):
    subpath = os.path.splitext(proto.proto_file)[0] + self.file_ext
    path = os.path.join(self.out_dir, subpath)
    self._prepare(path, proto)
