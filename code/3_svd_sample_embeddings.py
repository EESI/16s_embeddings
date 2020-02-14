#!/usr/bin/env python

import sys
#from sys import argv
import os
#import zipfile
import getopt
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

from sklearn.decomposition import TruncatedSVD
#from gensim.models import Word2Vec
#from gensim.models.word2vec import LineSentence

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
if df.index.names[0] == 0:
    print('Renaming index column to SampleID.')
    df.index.names = ['SampleID']
    df.to_csv(m,compression='gzip')

mat = df.to_numpy().T
sampids = df.index
del df

print('Performing svd.')
sys.stdout.flush()
svd = TruncatedSVD(n_components=1, n_iter=7, random_state=0)
svd.fit(mat)
pc = svd.components_
mat -= mat.dot(pc.T) * pc

print('Saving nonraw.')
sys.stdout.flush()
df = pd.DataFrame(mat.T,index=sampids)
df.index.names = ['SampleID']
df.to_csv(m.replace('_raw',''),compression='gzip')
