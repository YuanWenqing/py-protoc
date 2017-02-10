#!/usr/bin/python
# coding: utf8

import os, sys
rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from compilers.android import *
from parse.loader import *

if __name__ == '__main__':
  proto_dir = os.path.join(rootdir, 'example/proto')
  out_dir = os.path.join(rootdir, 'example/out/android')

  loader = Loader(proto_dir)
  writer = AndroidWriter(out_dir, '.java')
  resolver = AndroidResolver()
  compiler = AndroidCompiler(loader, writer, resolver)
  compiler.compileDir(proto_dir)