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

class CompileTask:
  def __init__(self, out_dir):
    self.out_dir = out_dir
    self.input_files = []
    self.skip_files = []

  def input(self, files):
    self.input_files.extend(files)
    return self

  def skip(self, files):
    self.skip_files.extend(files)
    return self

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
    files = self.__getAllFiles(section, 'input_proto')
    return [os.path.join(self.proto_dir, f) for f in files]

  def __getSkipProtos(self, section):
    return self.__getAllFiles(section, 'skip_proto')

  def __getAllFiles(self, section, base_opt):
    files = []
    if not self.cf.has_option(section, base_opt):
      return files
    files.extend(self.__parseFiles(self.cf.get(section, base_opt)))
    n = 2
    while True:
      opt = '%s.%d' % (base_opt, n)
      if self.cf.has_option(section, opt):
        files.extend(self.__parseFiles(self.cf.get(section, opt)))
        n += 1
      else:
        break
    return files

  def __parseFiles(self, text):
    files = []
    for f in text.split(','):
      f = f.strip()
      if len(f) == 0:
        continue
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
      task = CompileTask(out_dir)
      task.input(self.__getInputProtos(app))
      task.skip(self.__getSkipProtos(app))
      getattr(self, app)(task)

  def android(self, task):
    os.system('rm -r %s' % task.out_dir)
    resolver = AndroidResolver()
    writer = AndroidWriter(task.out_dir, '.java')
    compiler = AndroidCompiler(self.loader, writer, resolver)
    self.compilers.append((compiler, task))

  def ios(self, task):
    os.system('rm -r %s' % task.out_dir)
    resolver = IosResolver()
    writer = IosWriter(task.out_dir, '.h')
    compiler = IosHCompiler(self.loader, writer, resolver)
    self.compilers.append((compiler, task))
    writer = IosWriter(task.out_dir, '.m')
    compiler = IosMCompiler(self.loader, writer, resolver)
    self.compilers.append((compiler, task))

  def typescript(self, task):
    os.system('rm -r %s' % task.out_dir)
    resolver = TypeScriptResolver()
    writer = TypeScriptWriter(task.out_dir, '.ts')
    compiler = TypeScriptCompiler(self.loader, writer, resolver)
    self.compilers.append((compiler, task))
    # zh visual
    writer = TsEnumVisualWriter(task.out_dir, '.ts', 'Zh')
    compiler = TsEnumVisualCompiler(self.loader, writer, resolver, 'zh')
    self.compilers.append((compiler, task))
    # en visual
    writer = TsEnumVisualWriter(task.out_dir, '.ts', 'En')
    compiler = TsEnumVisualCompiler(self.loader, writer, resolver, 'en')
    self.compilers.append((compiler, task))

  def naming(self, task):
    resolver = NamingResolver()
    writer = NamingWriter(task.out_dir, '.java')
    compiler = NamingCompiler(self.loader, writer, resolver)
    self.compilers.append((compiler, task))

  def do(self):
    for compiler, task in self.compilers:
      print '> run %s' % compiler.__class__.__name__
      compiler.addSkip(task.skip_files)
      compiler.compile(task.input_files)

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
