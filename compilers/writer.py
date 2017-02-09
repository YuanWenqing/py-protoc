# coding: utf8

import os

class Writer:
  def __init__(self, out_dir, file_ext):
    self.out_dir = out_dir
    self.file_ext = file_ext
    self.outf = None

  def onProto(self, proto):
    pass

  def onDataDef(self, data_def):
    pass

  def done(self):
    self.close()
    pass

  def _open(self, path):
    self.close()
    d = os.path.dirname(path)
    if not os.path.exists(d):
      os.makedirs(d)
    self.outf = file(path, 'w')

  def _writeHeader(self, proto):
    if not proto:
      return
    self.outf.write('// generated from %s by py-protoc, NEVER CHANGE!!\n\n' % proto.proto_file)

  def writeline(self, line=None):
    if not line:
      return
    self.outf.write(line + '\n')

  def close(self):
    if self.outf:
      self.outf.close()

class SPPFWriter(Writer):
  '''每个proto一个文件'''

  def onProto(self, proto):
    subpath = os.path.splitext(proto.proto_file)[0] + self.file_ext
    path = os.path.join(self.out_dir, subpath)
    self.__open(path)
    self.__writeHeader(proto)

class SDPFWriter(Writer):
  '''每个data_def一个文件'''

  def onDataDef(self, data_def):
    path = os.path.join(self.out_dir, data_def.name) + self.file_ext
    self._open(path)
    self._writeHeader(data_def.proto)

