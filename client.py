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
from compilers.naming import *

class ClientCompiler:
  def __init__(self, conf_file):
    self.conf_file = conf_file
    self.path_root = os.path.dirname(os.path.abspath(conf_file))
    self.cf = ConfigParser.ConfigParser()
    self.cf.read(conf_file)
    self.proto_dir = self.cf.get('proto', 'proto_dir')
    self.proto_dir = os.path.join(self.path_root, self.proto_dir)
    self.loader = Loader(self.proto_dir)
    self.out_root = self.cf.get('proto', 'out_root')
    self.out_root = os.path.join(self.path_root, self.out_root)
    self.apps = self.cf.get('proto', 'app').split(',')

    self.compilers = []

  def __getInputProtos(self, section):
    files = []
    for f in self.cf.get(section, 'input_proto').split(','):
      f = f.strip()
      if len(f) == 0:
        continue
      f = os.path.join(self.proto_dir, f)
      if f not in files:
        files.append(f)
    return files

  def config(self):
    for app in self.apps:
      if self.cf.has_option(app, 'out_dir'):
        out_dir = self.cf.get(app, 'out_dir')
        out_dir = os.path.join(self.path_root, out_dir)
      else:
        out_dir = os.path.join(self.out_root, app)
      files = self.__getInputProtos(app)
      getattr(self, app)(out_dir, files)

  def android(self, out_dir, files):
    os.system('rm -r %s' % out_dir)
    resolver = AndroidResolver()
    writer = AndroidWriter(out_dir, '.java')
    compiler = AndroidCompiler(self.loader, writer, resolver)
    self.compilers.append((compiler, files))

  def ios(self, out_dir, files):
    os.system('rm -r %s' % out_dir)
    resolver = IosResolver()
    writer = IosWriter(out_dir, '.h')
    compiler = IosHCompiler(self.loader, writer, resolver)
    self.compilers.append((compiler, files))
    writer = IosWriter(out_dir, '.m')
    compiler = IosMCompiler(self.loader, writer, resolver)
    self.compilers.append((compiler, files))

  def typescript(self, out_dir, files):
    os.system('rm -r %s' % out_dir)
    resolver = TypeScriptResolver()
    writer = TypeScriptWriter(out_dir, '.ts')
    compiler = TypeScriptCompiler(self.loader, writer, resolver)
    self.compilers.append((compiler, files))
    # zh visual
    writer = TsEnumVisualWriter(out_dir, '.ts', 'Zh')
    compiler = TsEnumVisualCompiler(self.loader, writer, resolver, 'zh')
    self.compilers.append((compiler, files))
    # en visual
    writer = TsEnumVisualWriter(out_dir, '.ts', 'En')
    compiler = TsEnumVisualCompiler(self.loader, writer, resolver, 'en')
    self.compilers.append((compiler, files))

  def naming(self, out_dir, files):
    resolver = NamingResolver()
    writer = NamingWriter(out_dir, '.java')
    compiler = NamingCompiler(self.loader, writer, resolver)
    self.compilers.append((compiler, files))

  def do(self):
    for compiler, files in self.compilers:
      print '> run %s' % compiler.__class__.__name__
      compiler.compile(files)

if __name__ == '__main__':
  optParser = OptionParser()
  optParser.add_option("-c", "--conf", dest="conf_file", help="conf file", metavar="FILE")

  options, args = optParser.parse_args()

  if not options.conf_file:
    optParser.print_help()
    optParser.error('no conf file')

  cc = ClientCompiler(options.conf_file)
  cc.config()
  cc.do()
