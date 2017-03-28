# coding: utf8

from base import *
import re

class TypeScriptCompiler(Compiler):

  def compileHeader(self, proto):
    self.type_resolver.alias_map.clear()
    self.type_resolver.alias_map[proto.proto_file] = None
    for i, import_proto in enumerate(proto.import_protos):
      ts_path = os.path.relpath(import_proto.proto_file, os.path.dirname(proto.proto_file))
      ts_path = os.path.splitext(ts_path)[0]
      ts_path = './' + ts_path
      alias = import_proto.proto_pkg + str(i)
      self.type_resolver.alias_map[import_proto.proto_file] = alias
      self.writer.writeline('import * as %s from "%s";' % (alias, ts_path))
    self.writer.writeline()
    # self.writer.writeline('namespace %s {' % proto.proto_pkg)

  def compileTail(self, proto):
    # self.writer.writeline('}')
    self.writer.writeline()

  def compileMsg(self, msg, fields):
    self.beforeMsg(msg)
    for field in fields:
      self.compileMsgField(field)
    self.afterMsg(msg)

  def beforeMsg(self, msg):
    if msg.comment:
      self.writer.writeline('/**')
      self.writer.writeline(' * ' + msg.comment)
      self.writer.writeline(' */')
    self.writer.writeline('export interface %s {' % msg.name)

  def afterMsg(self, msg):
    self.writer.writeline('}')
    self.writer.writeline()

  def compileMsgField(self, field):
    if field.comment:
      self.writer.writeline('  /**')
      self.writer.writeline('   * ' + field.comment)
      self.writer.writeline('   */')
    field_type, default_value = self.type_resolver.resolveField(field)
    self.writer.writeline('  %s ?: %s;' % (field.name, field_type))

  def compileEnum(self, enum, fields):
    self.beforeEnum(enum)
    for field in fields:
      self.writer.writeline('  %s = %d,' % (field.name, field.number))
    self.afterEnum(enum)

  def beforeEnum(self, enum):
    if enum.comment:
      self.writer.writeline('/**')
      self.writer.writeline(' * ' + enum.comment)
      self.writer.writeline(' */')
    self.writer.writeline('export enum %s {' % enum.name)

  def afterEnum(self, enum):
    self.writer.writeline('}')
    self.writer.writeline()


class TypeScriptResolver(TypeResolver):
  BASE_TYPE_MAP = {
    'int64': ('number', '0'),
    'int32': ('number', '0'),
    'string': ('string', '""'),
    'bool': ('boolean', 'false'),
    'float': ('number', '0'),
    'double': ('number', '0'),
    'bytes': ('string', '""')
  }

  def __init__(self):
    self.alias_map = dict()

  def resolveField(self, field):
    if field.isRepeated():
      type_name, default_value = self.resolveType(field.type)
      if field.type.kind == TypeKind.REF and isinstance(field.type.ref, Enum):
        type_name = 'number'
      type_name = 'Array<%s>' % type_name
      default_value = 'null'
    else:
      type_name, default_value = self.resolveType(field.type)
    return (type_name, default_value)

  def resolveType(self, field_type):
    if field_type.kind == TypeKind.BASE:
      type_name, default_value = self.resolveBaseType(field_type.name)
    elif field_type.kind == TypeKind.REF:
      type_name = field_type.ref.name
      prefix = self.alias_map[field_type.ref.proto.proto_file]
      if prefix:
        type_name = prefix + '.' + type_name
      default_value = 'null'
    elif field_type.kind == TypeKind.MAP:
      key_type = self.resolveType(field_type.key_type)[0]
      value_type = self.resolveType(field_type.value_type)[0]
      type_name = 'Map<%s, %s>' % (key_type, value_type)
      default_value = 'null'
    return type_name, default_value

  def resolveBaseType(self, base_type):
    '''处理protobuf中的base type到指定语言的映射'''
    return TypeScriptResolver.BASE_TYPE_MAP[base_type]


class TypeScriptWriter(Writer):
  '''每个proto一个文件'''

  def beforeProto(self, proto, compiler):
    subpath = self.convertFilename(proto.proto_file) + self.file_ext
    path = os.path.join(self.out_dir, subpath)
    self._prepare(path, proto)
    compiler.compileHeader(proto)

  def afterProto(self, proto, compiler):
    compiler.compileTail(proto)

  def convertFilename(self, filepath):
    return os.path.splitext(filepath)[0]

class TsEnumVisualCompiler(TypeScriptCompiler):
  def __init__(self, loader, writer, type_resolver, annotation):
    TypeScriptCompiler.__init__(self, loader, writer, type_resolver)
    self.annotation = annotation
    self.pattern = '.*@%s\(([^\)]+)\).*' % annotation

  def skipProto(self, proto):
    if len(proto.enums) == 0:
      return True
    return Compiler.skipProto(self, proto)

  def compileMsgs(self, messages):
    # not compile msgs
    pass

  def compileEnum(self, enum, fields):
    l = []
    for field in fields:
      if not field.comment:
        continue
      for line in field.comment.split('\n'):
        m = re.match(self.pattern, line, re.IGNORECASE)
        if m:
          name = m.group(1)
          l.append((name, field.number))
          break
    if len(l) == 0:
      return
    self.beforeEnum(enum)
    for k, v in l:
      self.writer.writeline('  "%s" = %d,' % (k, v))
    self.afterEnum(enum)

  def beforeEnum(self, enum):
    if enum.comment:
      self.writer.writeline('/**')
      self.writer.writeline(' * ' + enum.comment)
      self.writer.writeline(' */')
    self.writer.writeline('export enum %s {' % enum.name)

  def afterEnum(self, enum):
    self.writer.writeline('}')
    self.writer.writeline()

class TsEnumVisualWriter(TypeScriptWriter):
  def __init__(self, out_dir, file_ext, lang):
    TypeScriptWriter.__init__(self, out_dir, file_ext)
    self.lang = lang

  def convertFilename(self, filepath):
    return TypeScriptWriter.convertFilename(self, filepath) + '_'+ self.lang.lower()
