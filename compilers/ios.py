# coding: utf8

from base import *

class IosHCompiler(Compiler):
  pass

class IosMCompiler(Compiler):
  pass

class IosResolver(TypeResolver):
  pass


class SPPFWriter(Writer):
  '''每个proto一个文件'''

  def onProto(self, proto):
    subpath = os.path.splitext(proto.proto_file)[0] + self.file_ext
    path = os.path.join(self.out_dir, subpath)
    self._prepare(path, proto)
