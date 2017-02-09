#!/usr/bin/python
# coding: utf8

import os, sys

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from compilers.ios import *

if __name__ == '__main__':
  proto_dir = os.path.join(rootdir, 'example/proto')
  proto_file = 'a.proto'
  out_dir = os.path.join(rootdir, 'example/out/ios')

  writer = IosWriter(out_dir, '.h')
  resolver = IosResolver()
  h_compiler = IosHCompiler(proto_dir, writer, resolver)
  h_compiler.compileDir('.')