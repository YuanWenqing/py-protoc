# coding: utf8

from base import *

class IosCompiler(Compiler):
  def resolveImport(self, fields):
    imports = list()
    for field in fields:
      field_type = field.type
      if field_type.kind == TypeKind.REF:
        type_name = canonical_name(field_type.ref)
        if type_name not in imports:
          imports.append(type_name)
      elif field_type.kind == TypeKind.MAP:
        raise Exception('not support map')
    return imports

class IosHCompiler(IosCompiler):

  def compileMsg(self, msg, fields):
    imports = self.resolveImport(fields)
    self.beforeMsg(msg, imports)
    for field in fields:
      self.compileMsgField(field)
    self.afterMsg(msg)

  def beforeMsg(self, msg, imports):
    msg_name = canonical_name(msg)
    # import
    self.writer.writeline('#import "XG_BaseModel.h"')
    for type_name in imports:
      self.writer.writeline('@class %s;' % type_name)
    self.writer.writeline()
    # declare
    if msg.comment:
      self.writer.writeline('/**')
      self.writer.writeline(' * ' + msg.comment)
      self.writer.writeline(' */')
    self.writer.writeline('@interface %s : XG_BaseModel' % msg_name)

  def afterMsg(self, msg):
    self.writer.writeline('@end')
    self.writer.writeline()

  def compileMsgField(self, field):
    if field.comment:
      self.writer.writeline('/**')
      self.writer.writeline(' * ' + field.comment)
      self.writer.writeline(' */')
    type_name, ref = self.type_resolver.resolveType(field)
    self.writer.writeline('@property(nonatomic, %s) %s * %s;' % (ref, type_name, field.name))

  def compileEnum(self, enum, fields):
    self.beforeEnum(enum)
    for i, field in enumerate(fields):
      if field.comment:
        self.writer.writeline('  /**')
        self.writer.writeline('   * ' + field.comment)
        self.writer.writeline('   */')
      s = '  %s = %d' % (field.name, field.number)
      if i < len(fields) - 1:
        s += ','
      self.writer.writeline(s)
    self.afterEnum(enum)

  def beforeEnum(self, enum):
    self.writer.writeline('#import <Foundation/Foundation.h>')
    self.writer.writeline()
    if enum.comment:
      self.writer.writeline('/**')
      self.writer.writeline(' * ' + enum.comment)
      self.writer.writeline(' */')
    self.writer.writeline('typedef enum {')

  def afterEnum(self, enum):
    enum_name = canonical_name(enum)
    self.writer.writeline('} %s;' % enum_name)
    self.writer.writeline()
    self.writer.writeline('%s %sValueOf(NSString *text);' % (enum_name, enum_name))
    self.writer.writeline('NSString* %sDescription(%s value);' % (enum_name, enum_name))
    self.writer.writeline()

class IosMCompiler(IosCompiler):

  def compileMsg(self, msg, fields):
    imports = self.resolveImport(fields)
    self.beforeMsg(msg, imports)
    repeated_ref_fields = []
    for field in fields:
      if not field.isRepeated():
        continue
      if field.type.kind != TypeKind.REF:
        continue
      repeated_ref_fields.append(field)
    if len(repeated_ref_fields) > 0:
      self.writer.writeline("+ (NSDictionary *)modelContainerPropertyGenericClass {")
      self.writer.writeline("  return @{")
      for i, field in enumerate(repeated_ref_fields):
        type_name = canonical_name(field.type.ref)
        line = '''    @"%s" : [%s class]''' % (field.name, type_name)
        if i < len(repeated_ref_fields) - 1:
          line = line + ','
        self.writer.writeline(line)
      self.writer.writeline("  };")
      self.writer.writeline("}")
    self.afterMsg(msg)

  def beforeMsg(self, msg, imports):
    msg_name = canonical_name(msg)
    # import
    self.writer.writeline('#import "%s.h"' % msg_name)
    for type_name in imports:
      self.writer.writeline('#import "%s.h"' % type_name)
    self.writer.writeline()
    # declare
    if msg.comment:
      self.writer.writeline('/**')
      self.writer.writeline(' * ' + msg.comment)
      self.writer.writeline(' */')
    self.writer.writeline('@implementation %s' % msg_name)

  def afterMsg(self, msg):
    self.writer.writeline('@end')
    self.writer.writeline()

  def compileEnum(self, enum, fields):
    self.beforeEnum(enum)
    enum_name = canonical_name(enum)

    self.writer.writeline('%s %sValueOf(NSString *text) {' % (enum_name, enum_name))
    self.writer.writeline('  if (text) {')
    i = 0;
    for i, field in enumerate(fields):
      line = '    '
      if i > 0:
        line += 'else '
      line += 'if ([text isEqualToString:@"%s"])' % field.name
      self.writer.writeline(line)
      self.writer.writeline('      return %s;' % field.name)
    self.writer.writeline('  }')
    self.writer.writeline('  return -1;')
    self.writer.writeline('}\n')
    # description
    self.writer.writeline('NSString* %sDescription(%s value) {' % (enum_name, enum_name))
    self.writer.writeline('  switch (value) {')
    for field in fields:
      self.writer.writeline('    case %s:' % field.name)
      self.writer.writeline('      return @"%s";' % field.name)
    self.writer.writeline('  }')
    self.writer.writeline('  return @"";')
    self.writer.writeline('}')
    self.writer.writeline('')


  def beforeEnum(self, enum):
    enum_name = canonical_name(enum)
    self.writer.writeline('#import "%s.h"' % enum_name)
    self.writer.writeline()
    if enum.comment:
      self.writer.writeline('/**')
      self.writer.writeline(' * ' + enum.comment)
      self.writer.writeline(' */')

class IosResolver(TypeResolver):
  BASE_TYPE_MAP = {
    'int64': ('NSNumber', 'strong'),
    'int32': ('NSNumber', 'strong'),
    'string': ('NSString', 'strong'),
    'bool': ('NSNumber', 'strong'),
    'float': ('NSNumber', 'strong'),
    'double': ('NSNumber', 'strong')
  }

  def resolveType(self, field):
    '''处理field的type，返回`(type_text, ref)`'''
    field_type = field.type
    if field.isRepeated():
      type_name = 'NSMutableArray'
      ref = 'strong'
    elif field_type.kind == TypeKind.BASE:
      type_name, ref = self.resolveBaseType(field_type.name)
    elif field_type.kind == TypeKind.REF:
      data_def = field_type.ref
      type_name = canonical_name(data_def)
      if isinstance(data_def, Enum):
        ref = 'assign'
      else:
        ref = 'strong'
    elif field_type.kind == TypeKind.MAP:
      raise Exception('not support map')
    return type_name, ref

  def resolveBaseType(self, base_type):
    '''处理protobuf中的base type，返回`(type_text, ref)`'''
    return IosResolver.BASE_TYPE_MAP[base_type]


class IosWriter(Writer):
  '''每个data_def一个文件'''

  def beforeDataDef(self, data_def):
    filename = canonical_name(data_def)
    path = os.path.join(self.out_dir, filename + self.file_ext)
    self._prepare(path, data_def.proto)
