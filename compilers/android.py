# coding: utf8

from base import *

class AndroidCompiler(Compiler):

  def compileMsg(self, msg, fields):
    self.beforeMsg(msg)
    for field in fields:
      self.compileMsgField(field)
    self.afterMsg(msg)

  def beforeMsg(self, msg):
    self.writer.writeline('package %s;' % msg.proto.getJavaPkg())
    self.writer.writeline()
    if msg.comment:
      self.writer.writeline('/**')
      self.writer.writeline(msg.comment)
      self.writer.writeline(' */')
    self.writer.writeline('public class %s {' % msg.name)

  def afterMsg(self, msg):
    self.writer.writeline('}')

  def compileMsgField(self, field):
    if field.comment:
      self.writer.writeline('  /**')
      self.writer.writeline(field.comment)
      self.writer.writeline('   */')
    field_type, default_value = self.type_resolver.resolveType(field)
    self.writer.writeline('  public %s %s = %s;' % (field_type, field.name, default_value))

  def compileEnum(self, enum, fields):
    self.beforeEnum(enum)
    for i, field in enumerate(fields):
      if field.comment:
        self.writer.writeline('  /**')
        self.writer.writeline(field.comment)
        self.writer.writeline('   */')
      s = '  %s(%d)' % (field.name, field.number)
      if i < len(fields) - 1:
        s += ','
      else:
        s += ';'
      self.writer.writeline(s)
    self.writer.writeline()
    self.writer.writeline('  public static final %s valueOf(int value) {' % enum.name)
    self.writer.writeline('    switch (value) {')
    for field in fields:
      self.writer.writeline('      case %d: return %s;' % (field.number, field.name))
    self.writer.writeline('      default: return null;')
    self.writer.writeline('    }')
    self.writer.writeline('  }')
    self.writer.writeline()
    self.afterEnum(enum)

  def beforeEnum(self, enum):
    self.writer.writeline('package %s;' % enum.proto.getJavaPkg())
    self.writer.writeline()
    if enum.comment:
      self.writer.writeline('/**')
      self.writer.writeline(enum.comment)
      self.writer.writeline(' */')
    self.writer.writeline('public enum %s {' % enum.name)

  def afterEnum(self, enum):
    self.writer.writeline('  private final int value = -1;')
    self.writer.writeline()
    self.writer.writeline('  public int getValue() { return this.value; }')
    self.writer.writeline()
    self.writer.writeline('  private %s(int value) { this.value = value; }' % enum.name)
    self.writer.writeline()
    self.writer.writeline('}')

class AndroidResolver(TypeResolver):
  BASE_TYPE_MAP = {
    'int64': ('long', '0L'),
    'int32': ('int', '0'),
    'string': ('String', '""'),
    'bool': ('boolean', 'false'),
    'float': ('float', '0F'),
    'double': ('double', '0')
  }
  BOX_Map = {
    'long': 'Long',
    'int': 'Integer',
    'String': 'String',
    'boolean': 'Boolean',
    'float': 'Float',
    'double': 'Double',
  }

  def resolveType(self, field):
    field_type = field.type
    if field_type.kind == TypeKind.BASE:
      field_type, default_value = self.resolveBaseType(field_type.name)
    else:
      data_def = field_type.ref
      if isinstance(data_def, Enum):
        field_type, default_value = self.resolveBaseType('int32')
      else:
        field_type = data_def.proto.getJavaPkg() + "." + data_def.name
        default_value = 'null'
    if field.isRepeated():
      field_type = 'java.util.List<%s>' % field_type
      default_value = 'null'
    return (field_type, default_value)

  def resolveBaseType(self, base_type):
    '''处理protobuf中的base type到指定语言的映射'''
    return AndroidResolver.BASE_TYPE_MAP[base_type]

class AndroidWriter(Writer):
  '''每个data_def一个文件'''

  def onDataDef(self, data_def):
    subpath = data_def.proto.getJavaPkg().replace('.', os.path.sep)
    path = os.path.join(self.out_dir, subpath, data_def.name + self.file_ext)
    self._prepare(path, data_def.proto)


