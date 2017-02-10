# coding: utf8

from base import *

class NamingCompiler(Compiler):

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
    self.__recurse(msg, '', '')
    self.afterMsg(msg)

  def beforeMsg(self, msg):
    self.writer.writeline('  interface %sNaming {' % msg.name)

  def afterMsg(self, msg):
    self.writer.writeline('  }')
    self.writer.writeline()

  def __recurse(self, msg, k_pre, v_pre):
    for field in msg.fields:
      self.__recurseField(field, k_pre, v_pre)

  def __recurseField(self, field, k_pre, v_pre):
    key = k_pre + field.name.upper()
    value = v_pre + field.name
    if field.comment:
      self.writer.writeline('    /**')
      self.writer.writeline('     * ' + field.comment)
      self.writer.writeline('     */')
    self.writer.writeline('    String %s = "%s";' % (key, value))
    if field.type.kind == TypeKind.REF and isinstance(field.type.ref, Message):
      self.__recurse(field.type.ref, key + '_DOT_', value + '.')

  def compileEnum(self, enum, fields):
    pass

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
