# coding: utf8
'''protobuf各个元素定义'''

class HeaderType(object):
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

class Field:
  '''field基类'''

  def __init__(self, name, number):
    self.name = name
    self.number = number
    self.comment = ''

  def isDeprecated(self):
    return self.comment != None and self.comment.find('@deprecated') >= 0

class MsgField(Field):
  '''message中的field定义'''

  def __init__(self, field_type, field_name, field_number):
    Field.__init__(self, field_name, field_number)
    self.type = field_type
    self.decorations = set()

  def addDecoration(self, decoration):
    self.decorations.add(decoration)

  def isRepeated(self):
    return 'repeated' in self.decorations

class EnumField(Field):
  '''enum中的field定义'''

  pass

class DataDef:
  '''数据结构基类'''
  def __init__(self, proto, name):
    self.proto = proto
    self.name = name
    self.fields = []
    self.comment = ''

  def isDeprecated(self):
    return self.comment != None and self.comment.find('@deprecated') >= 0

class Message(DataDef):
  '''protobuf中的message'''
  pass

class Enum(DataDef):
  '''protobuf中的enum'''
  pass

class Proto:
  '''proto文件'''
  def __init__(self, filepath):
    self.filepath = filepath
    self.headers = {}
    self.imports = {}
    self.options = {}

    self.messages = []
    self.enums = []
    self.datadefs = {}

  def addHeader(self, header):
    if header.type == HeaderType.IMPORT:
      self.imports[header.name] = header
    elif header.type == HeaderType.OPTION:
      self.options[header.name] = header
    else:
      self.headers[header.name] = header

  def getHeader(self, header_name):
    return self.headers[header_name]

  def getOption(self, option_name):
    return self.options[option_name]

  def addMsg(self, msg):
    self.messages.append(msg)
    self.datadefs[msg.name] = msg

  def addEnum(self, enum):
    self.enums.append(enum)
    self.datadefs[enum.name] = enum

  def getDataDef(self, data_name):
    return self.datadefs[data_name]
