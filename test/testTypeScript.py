#!/usr/bin/python
# coding: utf8

import os, sys
rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from compilers.typescript import *
from parse.loader import *

if __name__ == '__main__':
  proto_dir = os.path.join(rootdir, 'example/proto')
  out_dir = os.path.join(rootdir, 'example/out/typescript')

  loader = Loader(proto_dir)
  writer = TypeScriptWriter(out_dir, '.ts')
  resolver = TypeScriptResolver()
  compiler = TypeScriptCompiler(loader, writer, resolver)
  compiler.compileDir(proto_dir)