#!/usr/bin/env python

import sys
#from sys import argv
import getopt
import os
import zipfile
from os.path import splitext, isfile
import gzip
import csv
import six.moves.cPickle
#import collections
#from shutil import copyfile

import numpy as np
#from collections import defaultdict
import pandas as pd
#from itertools import product
#from operator import itemgetter
#from sklearn.manifold import TSNE
import random
import math
#import time

#from sklearn.decomposition import TruncatedSVD

#import embed_functions as emb
from glob import glob


err = '%s\n-w <path of working directory>' % (sys.argv[0])

try:
    opts, args = getopt.getopt(sys.argv[1:],'hw:',['help','wdir'])
except getopt.GetoptError:
    print(err)
    sys.exit()
if len(opts) == 0:
    print(err)
    sys.exit()

for opt, arg in opts:
    if opt in ('-h','--help'):
        print(err)
        sys.exit()
    elif opt in ('-w','--wdir'):
        work_dir = arg

fns = [f for f in glob(work_dir + '/*remb_raw_merged.csv.gz')]
if len(fns) > 1:
    print('Multiple merged embeddings in working directory.')
    sys.exit()
else:
    m = fns[0]


print('Reading raw.')
sys.stdout.flush()
df = pd.read_csv(m,index_col=0,header=None)
s = 0
c = 0 
nan_list = []
for idx, row_idx in enumerate(df.iterrows()):
   _, row = row_idx
   k = row.isnull().values.any()
   s += k
   c += 1
   if k > 0:
       nan_list.append(idx)

if s > 0:
    print(m, flush = True)
    print(df.shape, c, flush = True)
    df.drop(df.index[nan_list], inplace=True)
    print(df.shape, flush = True)

    df.to_csv(m, compression='gzip', header = False)
if s > 0:
    df = pd.read_csv(m, compression='gzip')
    s = 0
    c = 0
    for idx, row_idx in enumerate(df.iterrows()):
        _, row = row_idx
        k = row.isnull().values.any()
        s += k
        c += 1
    print(s, c, flush = True)

