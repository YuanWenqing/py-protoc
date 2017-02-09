#!/usr/bin/python
# coding: utf8

import os, sys

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from compilers.android import *

if __name__ == '__main__':
  proto_dir = os.path.join(rootdir, 'example/proto')
  proto_file = 'a.proto'
  out_dir = os.path.join(rootdir, 'example/out/android')

  writer = AndroidWriter(out_dir, '.java')
  resolver = AndroidResolver()
  compiler = AndroidCompiler(proto_dir, writer, resolver)
  compiler.compileDir('.')