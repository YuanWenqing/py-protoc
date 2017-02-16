# coding: utf8
'''protobuf各个元素定义'''

class HeaderKind(object):
  """header类型"""
  SYNTAX = 'syntax'
  PACKAGE = 'package'
  IMPORT = 'import'
  OPTION = 'option'

class Header:
  def __init__(self, header_type, header_name, header_value):
    self.type = header_type
    self.name = header_name
    self.value = header_value

  def __str__(self):
    return '%s: %s=%s' % (self.type, self.name, self.value)

class Field:
  '''field基类'''

  def __init__(self, name, number):
    self.name = name
    self.number = number
    self.comment = None
    self.index = None
    self.data_def = None

  def isDeprecated(self):
    return self.comment != None and self.comment.find('@deprecated') >= 0

  def __str__(self):
    s = '%d: %s=%d' % (self.index, self.name, self.number)
    if self.comment:
      s = '%s #%s' % (s, self.comment.replace('\n', '\\n'))
    return s

class TypeKind:
  '''field type的类型'''

  BASE = 'base' # protobuf基本类型
  REF = 'ref' # 自定义的引用类型
  MAP = 'map' # map

class FieldType:
  '''field的type'''

  def __init__(self, type_kind, type_name, key_type=None, value_type=None):
    self.kind = type_kind
    self.name = type_name
    self.key_type = key_type
    self.value_type = value_type

    self.ref = None

  def __str__(self):
    if self.kind == TypeKind.BASE:
      return self.name
    elif self.kind == TypeKind.REF:
      return self.ref.whole_name
    elif self.kind == TypeKind.MAP:
      return 'map<%s, %s>' % (self.key_type, self.value_type)

class MessageField(Field):
  '''message中的field定义'''

  def __init__(self, field_type, field_name, field_number):
    Field.__init__(self, field_name, field_number)
    self.type = field_type
    self.decorations = list()

  def addDecoration(self, decoration):
    self.decorations.append(decoration)

  def isRepeated(self):
    return 'repeated' in self.decorations

  def __str__(self):
    s = '%d:' % self.index
    if len(self.decorations) > 0:
      for dw in self.decorations:
        s = s + ' ' + dw
    s = s + (' %s %s=%d' % (self.type, self.name, self.number))
    if self.comment:
      s = s + (' #%s' % self.comment.replace('\n', '\\n'))
    return s

class EnumField(Field):
  '''enum中的field定义'''

  pass

class DataDef:
  '''数据结构基类'''
  def __init__(self, name):
    self.proto = None
    self.name = name
    self.fields = []
    self.comment = None
    self.whole_name = None

  def addField(self, field):
    self.fields.append(field)
    field.data_def = self

  def isDeprecated(self):
    return self.comment != None and self.comment.find('@deprecated') >= 0

  def __str__(self):
    if self.comment:
      s = '%s %s(#%s) {' % (self.__class__.__name__, self.name, self.comment.replace('\n', '\\n'))
    else:
      s = '%s %s {' % (self.__class__.__name__, self.name)
    first = True
    for field in self.fields:
      if first:
        first = False
      else:
        s = s + ', '
      s = s + field.__str__()
    s = s + '}'
    return s

class Message(DataDef):
  '''protobuf中的message'''
  pass

class Enum(DataDef):
  '''protobuf中的enum'''
  pass

class Protobuf:
  '''proto文件'''
  def __init__(self):
    self.proto_dir = None
    self.proto_file = None
    self.proto_pkg = None

    self.headers = {}
    self.imports = []
    self.options = {}

    self.messages = []
    self.enums = []
    self.import_protos = []
    self.datadefs = {}
    self.imported_defs = {}

  def addHeader(self, header):
    if header.type == HeaderKind.IMPORT:
      self.imports.append(header.name)
    elif header.type == HeaderKind.OPTION:
      self.options[header.name] = header
    else:
      self.headers[header.name] = header
      if header.name == HeaderKind.PACKAGE:
        self.proto_pkg = header.value

  def getHeader(self, header_name):
    return self.headers[header_name]

  def getOption(self, option_name):
    return self.options[option_name]

  def getJavaPkg(self):
    return self.getOption('java_package').value

  def addDataDef(self, data_def):
    data_def.whole_name = self.proto_pkg + '.' + data_def.name
    self.datadefs[data_def.whole_name] = data_def
    if isinstance(data_def, Message):
      for field in data_def.fields:
        self.__completeName(field.type)
      self.messages.append(data_def)
    else:
      self.enums.append(data_def)

  def __completeName(self, field_type):
    if field_type.kind == TypeKind.REF:
      if '.' not in field_type.name:
        field_type.name = self.proto_pkg + '.' + field_type.name
    elif field_type.kind == TypeKind.MAP:
      self.__completeName(field_type.key_type)
      self.__completeName(field_type.value_type)

  def getDataDef(self, data_name):
    return self.datadefs[data_name]

  def __str__(self):
    s = '%s in %s' % (self.proto_file, self.proto_dir)
    if len(self.headers) > 0:
      s = '%s\n>>>>> Header <<<<<\n%s' % (s, self.__arr2str(self.headers.values()))
    if len(self.imports) > 0:
      s = '%s\n>>>>> Import <<<<<\n%s' % (s, self.__arr2str(self.imports))
    if len(self.options) > 0:
      s = '%s\n>>>>> Option <<<<<\n%s' % (s, self.__arr2str(self.options.values()))
    if len(self.messages) > 0:
      s = '%s\n>>>>> Message <<<<<\n%s' % (s, self.__arr2str(self.messages))
    if len(self.enums) > 0:
      s = '%s\n>>>>> Enum <<<<<\n%s' % (s, self.__arr2str(self.enums))
    return s

  def __arr2str(self, arr):
    s = '['
    first = True
    for item in arr:
      if first:
        first = False
      else:
        s = s + ', '
      s = s + '\n  ' + item.__str__()
    s = s + '\n]'
    return s

def concat_comment(c1, c2):
  if not c1:
    return c2
  if not c2:
    return c1
  return '%s\n%s' % (c1, c2)
