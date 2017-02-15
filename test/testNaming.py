#!/usr/bin/python
# coding: utf8

import os, sys
rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from compilers.naming import *
from parse.loader import *

if __name__ == '__main__':
  proto_dir = os.path.join(rootdir, 'example/proto')
  out_dir = os.path.join(rootdir, 'example/out/naming')

  loader = Loader(proto_dir)
  writer = NamingWriter(out_dir, '.java')
  resolver = NamingResolver()
  compiler = NamingCompiler(loader, writer, resolver)
  compiler.compileDir(proto_dir)