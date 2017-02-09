#!/usr/bin/python
# coding: utf8

import os, sys

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from compilers.typescript import *

if __name__ == '__main__':
  proto_dir = os.path.join(rootdir, 'example/proto')
  out_dir = os.path.join(rootdir, 'example/out/typescript')

  writer = TsWriter(out_dir, '.ts')
  resolver = TsResolver()
  compiler = TsCompiler(proto_dir, writer, resolver)
  compiler.compileDir('.')