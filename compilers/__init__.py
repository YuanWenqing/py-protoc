# coding: utf8

'''
ios、android、web、naming等编译器
'''

import os, sys

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if rootdir not in sys.path:
  sys.path.append(rootdir)
