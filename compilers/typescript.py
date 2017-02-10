# coding: utf8

from base import *

class TypeScriptCompiler(Compiler):

  def compileHeader(self, proto):
    for proto_file in proto.imports:
      ts_path = os.path.relpath(proto_file, os.path.dirname(proto.proto_file))
      ts_path = self.writer.convertExt(ts_path)
      ts_path = './' + ts_path
      self.writer.writeline('/// <refrence path="%s" />' % ts_path)
    self.writer.writeline()
    self.writer.writeline('namespace %s {' % proto.proto_pkg)

  def compileTail(self, proto):
    self.writer.writeline('}')
    self.writer.writeline()

  def compileMsg(self, msg, fields):
    self.beforeMsg(msg)
    for field in fields:
      self.compileMsgField(field)
    self.afterMsg(msg)

  def beforeMsg(self, msg):
    if msg.comment:
      self.writer.writeline('  /**')
      self.writer.writeline('  ' + msg.comment)
      self.writer.writeline('   */')
    self.writer.writeline('  export interface %s {' % msg.name)

  def afterMsg(self, msg):
    self.writer.writeline('  }')
    self.writer.writeline()

  def compileMsgField(self, field):
    if field.comment:
      self.writer.writeline('    /**')
      self.writer.writeline('    ' + field.comment)
      self.writer.writeline('     */')
    field_type, default_value = self.type_resolver.resolveType(field)
    self.writer.writeline('    %s : %s;' % (field.name, field_type))

  def compileEnum(self, enum, fields):
    self.beforeEnum(enum)
    for field in fields:
      self.writer.writeline('    %s = %d;' % (field.name, field.number))
    self.afterEnum(enum)

  def beforeEnum(self, enum):
    if enum.comment:
      self.writer.writeline('  /**')
      self.writer.writeline(enum.comment)
      self.writer.writeline('   */')
    self.writer.writeline('  enum %s {' % enum.name)

  def afterEnum(self, enum):
    self.writer.writeline('  }')
    self.writer.writeline()


class TypeScriptResolver(TypeResolver):
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
    elif field_type.kind == TypeKind.REF:
      type_name = field_type.ref.proto.proto_pkg + '.' + field_type.ref.name
      default_value = 'null'
    if field.isRepeated():
      if field_type.kind == TypeKind.REF and isinstance(field_type.ref, Enum):
        type_name = 'number'
      type_name = 'Array<%s>' % type_name
      default_value = 'null'
    return (type_name, default_value)

  def resolveBaseType(self, base_type):
    '''处理protobuf中的base type到指定语言的映射'''
    return TypeScriptResolver.BASE_TYPE_MAP[base_type]


class TypeScriptWriter(Writer):
  '''每个proto一个文件'''

  def beforeProto(self, proto, compiler):
    subpath = self.convertExt(proto.proto_file)
    path = os.path.join(self.out_dir, subpath)
    self._prepare(path, proto)
    compiler.compileHeader(proto)

  def afterProto(self, proto, compiler):
    compiler.compileTail(proto)

  def convertExt(self, filepath):
    return os.path.splitext(filepath)[0] + self.file_ext
