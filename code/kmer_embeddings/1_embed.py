#!/usr/bin/env python

from sys import argv
import os
import getopt

import zipfile
from os.path import splitext, isfile
import gzip
import csv
import six.moves.cPickle
import collections
from shutil import copyfile

import matplotlib.pyplot as plt
from matplotlib.pyplot import cm

import numpy as np
import pandas as pd
from itertools import product
from operator import itemgetter
from sklearn.manifold import TSNE
import random
import math
from scipy import sparse

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

import embed_functions as emb
import embed_params as p


pts, args = getopt.getopt(sys.argv[1:],'hk:i:q:m:o:p:',['help','idir','k','query','modpath','odir','prefix'])
except getopt.GetoptError:
        print(err)
        sys.exit()
if len(opts) == 0:
    print(err)
    sys.exit()

v = 100
k = 0

for opt, arg in opts:
    if opt in ('-h','--help'):
        print('%s\n-k <k-mer size, int>\n-v <number of lines to print, int>\n-m <gensim model path>\n-i <input file type in fasta.gz format>\n-o <output file dir>\n-p <prefix for output files>' % (sys.argv[0]))
        sys.exit()
    elif opt in ('-m','--modpath'):
        mod_path = arg
        try:
            k = int(kmers_fn.split('_')[-2])
            print('k=%s extracted from kmer file filename' % (k))
    elif opt in ('-k'):
        k = int(arg)
    elif opt in ('-q','--query'):
        v = int(arg)
    elif opt in ('-o','--odir'):
        data_dir = arg
    elif opt in ('-p','--prefix'):
        name = arg

if k == 0:
    print('k not specified in kmer file filename via -i or via -k')
	sys.exit()



embed_fn = name + '_' + model_fn
k = int(model_fn.split('_')[1])

embed_dir = os.path.expanduser('~/embedding/embeddings')

kmers_fn_in = name + '_' + str(k) + '_kmers.csv.gz'
kmers_fn = name + '_' + str(k) + '_kmers_' + str(fn_row) + '.csv.gz'

ids_fn = name + '_' + str(k) + '_ids' + '.pkl'

if not os.path.exists(os.path.join(embed_dir,embed_fn)):

    ids = six.moves.cPickle.load(open(ids_fn,'rb'))['ids']

    model = Word2Vec.load(model_fn)
    
    embeddings = emb.read2vec(kmers_fn,model,ids,k=k)

    print('Saving ids and embeddings.')
    six.moves.cPickle.dump({'ids':ids,'embeddings':embeddings},
            open(os.path.join(embed_dir,embed_fn),'wb'),protocol=4)

else:

    print(embed_fn + ' exists')
