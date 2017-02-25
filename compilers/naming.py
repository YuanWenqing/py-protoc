# coding: utf8

from base import *

class NamingCompiler(Compiler):

  def skip(self, proto):
    if len(proto.messages) == 0:
      return True
    return False

  def compileHeader(self, proto):
    javaPkg = convertPkg(proto.getJavaPkg())
    self.writer.writeline('package %s;' % javaPkg)
    self.writer.writeline()
    self.writer.writeline('public interface %sNaming {' % proto.getOption('java_outer_classname').value)

  def compileTail(self, proto):
    self.writer.writeline('}')
    self.writer.writeline()

  def compileMsg(self, msg, fields):
    self.beforeMsg(msg)
    self.__recurse(msg, RecurseContext())
    self.afterMsg(msg)

  def beforeMsg(self, msg):
    self.writer.writeline('  interface %sNaming {' % msg.name)

  def afterMsg(self, msg):
    self.writer.writeline('  }')
    self.writer.writeline()

  def __recurse(self, msg, ctx):
    if ctx.hasVisited(msg):
      return
    ctx.begVisit(msg)
    for field in msg.fields:
      self.__recurseField(field, ctx)
    ctx.endVisit()

  def __recurseField(self, field, ctx):
    key = ctx.k_pre + field.name.upper()
    value = ctx.v_pre + field.name
    if field.comment:
      self.writer.writeline('    /**')
      self.writer.writeline('     * ' + field.comment)
      self.writer.writeline('     */')
    self.writer.writeline('    String %s = "%s";' % (key, value))
    if field.type.kind == TypeKind.REF and isinstance(field.type.ref, Message):
      ctx.push(key + '_DOT_', value + '.')
      self.__recurse(field.type.ref, ctx)
      ctx.pop()

  def compileEnum(self, enum, fields):
    pass

class RecurseContext:
  def __init__(self):
    self.msg_path = []
    self.pre_path = [('', '')]
    self.k_pre = ''
    self.v_pre = ''

  def hasVisited(self, msg):
    return msg.full_name in self.msg_path

  def begVisit(self, msg):
    self.msg_path.append(msg.full_name)

  def endVisit(self):
    self.msg_path.pop()

  def push(self, k, v):
    self.pre_path.append((k, v))
    self.k_pre = k
    self.v_pre = v

  def pop(self):
    self.pre_path.pop()
    self.k_pre, self.v_pre = self.pre_path[-1]

class NamingResolver(TypeResolver):
  pass

class NamingWriter(Writer):
  '''每个proto一个文件'''

  def beforeProto(self, proto, compiler):
    javaClass = proto.getOption('java_outer_classname').value
    javaClass += 'Naming'
    javaPkg = proto.getJavaPkg()
    javaPkg = convertPkg(javaPkg)
    subpath = javaPkg.replace('.', os.path.sep)
    path = os.path.join(self.out_dir, subpath, javaClass + self.file_ext)
    self._prepare(path, proto)
    compiler.compileHeader(proto)

  def afterProto(self, proto, compiler):
    compiler.compileTail(proto)

def convertPkg(pkg):
  return pkg.replace('proto.data', 'proto.naming')
