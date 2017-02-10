# -*- coding=utf8 -*-
"""语法解析"""
from error import ProtoGrammarError
from protodef.element import *

def p_error(p):
  if p is None:
    raise ProtoGrammarError('grammar error at EOF')
  raise ProtoGrammarError('grammar error: {} at line {}'.format(p.value, p.lineno))


def p_start(p):
  """start : header definition tail
          | header tail"""
  proto = Protobuf()
  for header in p[1]:
    proto.addHeader(header)
  for data_def in p[2]:
    data_def.proto = proto
    proto.addDataDef(data_def)
  # TODO: resolve import and check type ref
  p[0] = proto


def p_tail(p):
  '''tail : comment
          |'''
  p[0] = []


def p_comment(p):
  '''comment : SINGLE_COMMENT comment
        | SINGLE_COMMENT '''
  if len(p) == 1:
    p[0] = None
  elif len(p) == 2:
    p[0] = p[1]
  else:
    comment = concat_comment(p[1], p[2])
    comment = comment.strip()
    if len(comment) == 0:
      p[0] = None
    else:
      p[0] = comment

def p_header(p):
  """header : header header_unit_
        | header_unit_"""
  if len(p) == 1:
    p[0] = []
  elif len(p) == 2:
    p[0] = [p[1]]
  else:
    #p[0] = [p[1]] + p[2]
    p[0] = p[1] + [p[2]]


def p_header_unit_(p):
  """header_unit_ : comment header_unit LINE_END
        | header_unit LINE_END """
  if len(p) == 4:
    p[0] = p[2]
  else:
    p[0] = p[1]


def p_header_unit(p):
  """header_unit : syntax
           | package
           | import
           | option """
  p[0] = p[1]


def p_syntax(p):
  """syntax : SYNTAX '=' LITERAL"""
  if p[3] != 'proto3':
    raise ProtoGrammarError('grammar error at line {}: syntax must be proto3'.format(p.lineno))
  p[0] = Header(HeaderKind.SYNTAX, HeaderKind.SYNTAX, p[3])


def p_package(p):
  """package : PACKAGE IDENTIFIER"""
  p[0] = Header(HeaderKind.PACKAGE, HeaderKind.PACKAGE, p[2])

def p_import(p):
  """import : IMPORT LITERAL"""
  p[0] = Header(HeaderKind.IMPORT, p[2], p[2])

def p_option(p):
  """option : OPTION IDENTIFIER '=' LITERAL"""
  p[0] = Header(HeaderKind.OPTION, p[2], p[4])


def p_definition(p):
  """definition : definition definition_unit_
          | definition_unit_"""
  if len(p) == 1:
    p[0] = []
  elif len(p) == 2:
    p[0] = [p[1]]
  else:
    p[0] = p[1] + [p[2]]


def p_definition_unit_(p):
  """definition_unit_ : comment definition_unit
          | definition_unit"""
  if len(p) == 3:
    data_def = p[2]
    data_def.comment = p[1]
  else:
    data_def = p[1]
  p[0] = data_def


def p_definition_unit(p):
  """definition_unit : message
             | enum"""
  p[0] = p[1]


def p_message(p):
  """message : MESSAGE IDENTIFIER '{' msg_fields '}'"""
  message = Message(p[2])
  for index, field in enumerate(p[4]):
    field.index = index
    message.addField(field)
  p[0] = message


def p_msg_fields(p):
  """msg_fields : msg_field_ msg_fields
         | """
  if len(p) == 1:
    p[0] = []
  else:
    p[0] = [p[1]] + p[2]


def p_msg_field_(p):
  '''msg_field_ : comment msg_field LINE_END
          | msg_field LINE_END'''
  if len(p) == 4:
    field = p[2]
    field.comment = concat_comment(p[1], p[3])
  else:
    field = p[1]
    field.comment = p[2]
  p[0] = field


def p_msg_field(p):
  """msg_field : field_decoration field_type IDENTIFIER '=' INTCONSTANT"""
  field = MessageField(p[2], p[3], p[5])
  if p[1]:
    field.addDecoration(p[1])
  p[0] = field


def p_field_decoration(p):
  """field_decoration : OPTIONAL
         | REPEATED
         |"""
  if len(p) == 2 and p[1] == 'repeated':
    p[0] = 'repeated'
  else:
    p[0] = None


def p_field_type(p):
  """field_type : ref_type
          |  definition_type"""
  p[0] = p[1]


def p_ref_type(p):
  """ref_type : IDENTIFIER
          |  IDENTIFIER '.' IDENTIFIER """
  if len(p) == 2:
    p[0] = FieldType(TypeKind.REF, p[1])
  else:
    p[0] = FieldType(TypeKind.REF, p[1] + '.' + p[3])


def p_definition_type(p):
  """definition_type : base_type"""
             # | container_type"""
  p[0] = p[1]


def p_base_type(p):
  """base_type : BOOL
         | STRING
         | BYTES
         | DOUBLE
         | FLOAT
         | INT32
         | INT64
         | UINT32
         | UINT64
         | SINT32
         | SINT64
         | FIXED32
         | FIXED64
         | SFIXED32
         | SFIXED64"""
  p[0] = FieldType(TypeKind.BASE, p[1])


# def p_container_type(p):
#   """container_type : map_type"""
#   p[0] = p[1]


# def p_map_type(p):
#   """map_type : MAP '<' base_type ',' base_type '>'
#          | MAP '<' base_type ',' ref_type '>'"""
#   if p[3] == 'bytes':
#     raise ProtoGrammarError(
#       'grammar error at line {}: key type cannot be bytes'.format(p.lineno))
#   p[0] = FieldType(TypeKind.MAP, p[1], p[3], p[5])


def p_enum(p):
  """enum : ENUM IDENTIFIER '{' enum_fields '}'"""
  enum = Enum(p[2])
  for index, field in enumerate(p[4]):
    field.index = index
    enum.addField(field)
  p[0] = enum


def p_enum_fields(p):
  """enum_fields : enum_field_ enum_fields
         | """
  if len(p) == 1:
    p[0] = []
  else:
    p[0] = [p[1]] + p[2]


def p_enum_field_(p):
  '''enum_field_ : comment enum_field LINE_END
          | enum_field LINE_END'''
  if len(p) == 4:
    field = p[2]
    field.comment = concat_comment(p[1], p[3])
  else:
    field = p[1]
    field.comment = p[2]
  p[0] = field

def p_enum_field(p):
  """enum_field : IDENTIFIER '=' INTCONSTANT"""
  p[0] = EnumField(p[1], p[3])


# def p_service(p):
#   """service : SERVICE IDENTIFIER '{' func_seq '}'"""
#   service = Service(p[2])
#   for method in p[4]:
#     if method.name in service.methods:
#       raise ProtoGrammarError(
#         'grammar error: method {} is already defined at line {}'.format(
#           method.name, p.lineno))
#     service.methods[method.name] = method
#   p[0] = service


# def p_func_seq(p):
#   """func_seq : func func_seq
#         | func ';' func_seq
#         |"""
#   p_len = len(p)
#   if p_len == 1:
#     p[0] = []
#   elif p_len == 3:
#     p[0] = [p[1]] + p[2]
#   else:
#     p[0] = [p[1]] + p[3]


# def p_func(p):
#   """func : RPC IDENTIFIER '(' IDENTIFIER ')' RETURNS '(' IDENTIFIER ')' '{' '}'"""
#   p[0] = ServiceMethod(p[2], p[4], p[8])


# def _check_methods(proto):
#   """检查serivce中定义方法的传参能否解析

#   Args:
#     proto (Protobuf): 解析得到的对象
#   """
#   for _, service in proto.services.iteritems():
#     for method_name, method in service.methods.iteritems():
#       if method.request_type in proto.messages and \
#               method.response_type in proto.messages:
#         continue
#       raise ProtoGrammarError(
#         'grammar error: {} params not defined'.format(method_name,))


# def _update_fields(proto):
#   """更新map中的自定义类型以及检查嵌套message类型是否存在

#   Args:
#     proto (Protobuf): 解析得到的对象
#   """
#   for _, message in proto.messages.iteritems():
#     for field_name, field in message.fields.iteritems():
#       if isinstance(field, MessageField):
#         if field_name not in proto.messages:
#           raise ProtoGrammarError(
#             'grammar error: {} not defined'.format(field_name))

#         field.message_type = proto.messages[field_name]
#       elif isinstance(field, MapField):
#         key_type, key_name = field.key_type
#         val_type, val_name = field.value_type

#         if val_type == FieldType.REF:
#           if val_name not in proto.messages:
#             raise ProtoGrammarError(
#               'grammar error: {} not defined'.format(field_name))

#           field.value_type = MessageField(
#             val_name, 1, 1, 1, proto.messages[val_name])
#         else:
#           class_ = field_map[val_name]
#           field.value_type = class_('value', 1, 1, 1)

#         class_ = field_map[key_name]
#         field.key_type = class_('key', 0, 0, 1)