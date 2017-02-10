#!/usr/bin/python
# coding: utf8

import os, sys
from optparse import OptionParser
import ConfigParser

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)

from parse.loader import *
from compilers.android import *
from compilers.ios import *
from compilers.typescript import *

def config(conf_file):
  path_root = os.path.dirname(os.path.abspath(conf_file))
  cf = ConfigParser.ConfigParser()
  cf.read(conf_file)
  proto_dir = cf.get('proto', 'proto_dir')
  proto_dir = os.path.join(path_root, proto_dir)
  loader = Loader(proto_dir)
  out_root = cf.get('proto', 'out_root')
  out_root = os.path.join(path_root, out_root)

  compilers = []

  # android
  out_dir = os.path.join(out_root, 'android')
  files = []
  for f in cf.get('android', 'input_proto').split(','):
    f = os.path.join(path_root, proto_dir)
    files.append(f)
  resolver = AndroidResolver()
  writer = AndroidWriter(out_dir, '.java')
  compiler = AndroidCompiler(loader, writer, resolver)
  compilers.append((compiler, files))
  # ios
  out_dir = os.path.join(out_root, 'ios')
  files = []
  for f in cf.get('ios', 'input_proto').split(','):
    f = os.path.join(path_root, proto_dir)
    files.append(f)
  resolver = IosResolver()
  writer = IosWriter(out_dir, '.h')
  compiler = IosHCompiler(loader, writer, resolver)
  compilers.append((compiler, files))
  writer = IosWriter(out_dir, '.m')
  compiler = IosMCompiler(loader, writer, resolver)
  compilers.append((compiler, files))
  # typescript
  out_dir = os.path.join(out_root, 'typescript')
  files = []
  for f in cf.get('typescript', 'input_proto').split(','):
    f = os.path.join(path_root, proto_dir)
    files.append(f)
  resolver = TypeScriptResolver()
  writer = TypeScriptWriter(out_dir, '.ts')
  compiler = TypeScriptCompiler(loader, writer, resolver)
  compilers.append((compiler, files))

  return compilers

if __name__ == '__main__':
  optParser = OptionParser()
  optParser.add_option("-c", "--conf", dest="conf_file", help="conf file", metavar="FILE")

  options, args = optParser.parse_args()

  if not options.conf_file:
    optParser.print_help()
    optParser.error('no conf file')

  compilers = config(options.conf_file)
  for compiler, files in compilers:
    print '> run %s' % compiler.__class__.__name__
    compiler.compile(files)
