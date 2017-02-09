#!/usr/bin/python
# coding: utf8

import os, sys

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from compilers.ios import *

if __name__ == '__main__':
  proto_dir = os.path.join(rootdir, 'example/proto')
  out_dir = os.path.join(rootdir, 'example/out/ios')

  resolver = IosResolver()

  h_writer = IosWriter(out_dir, '.h')
  h_compiler = IosHCompiler(proto_dir, h_writer, resolver)
  h_compiler.compileDir('.')

  m_writer = IosWriter(out_dir, '.m')
  m_compiler = IosMCompiler(proto_dir, m_writer, resolver)
  m_compiler.compileDir('.')
