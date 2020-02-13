#!/usr/bin/env python

import sys
import os
import getopt
from glob import glob

import zipfile
from os.path import splitext, isfile
import gzip
import csv
import six.moves.cPickle

from gensim.models import Word2Vec

import embed_functions as emb

err = '%s\n-p <prefix of working files>\n-m <path of gensim model>\n-q <path to k-mers file to be embedded>\n-w <path of working directory\n-k <k-mer length>\n-v <number of lines to process before printing>' % (sys.argv[0])

try:
    opts, args = getopt.getopt(sys.argv[1:],'hp:m:q:w:k:v:',['help','prefix','modpath','qpath','wdir','k','verbose'])
except getopt.GetoptError:
    print(err)
    sys.exit()
if len(opts) == 0:
    print(err)
    sys.exit()

k = 0
model_fn = 0
for opt, arg in opts:
    if opt in ('-h','--help'):
        print(err)
        sys.exit()
    elif opt in ('-p','--prefix'):
        name = arg
    elif opt in ('-m','--modpath'):
        model_fn = arg
    elif opt in ('-q','--qpath'):
        kmers_fn = arg
    elif opt in ('-w','--wdir'):
        work_dir = arg
    elif opt in ('-k'):
        k = int(arg)
    elif opt in ('-v','--verbose'):
        v = int(arg)
if model_fn == 0:
    model_fn = [f for f in glob(work_dir + '/*') if 'model.pkl' in f]
    if len(model_fn) == 1:
        model_fn = model_fn[0]
    else:
        print('Multiple models in work dir and model not specific via -m')
        sys.exit()
    try:
        k = int(model_fn.split('_')[-8])
        print('k=%s extracted from kmer file filename' % (k))
        kmers_fn = os.path.join(work_dir,name + '_' + str(k) + '_kmers.csv.gz')
        print('Embedding %s' % (kmers_fn))
        ids_fn = os.path.join(work_dir,name + '_' + str(k) + '_ids' + '.pkl')
    except IndexError:
        pass
if k == 0:
    print('k not specified in kmer file filename via -i or via -k')
    sys.exit()

ids = six.moves.cPickle.load(open(ids_fn,'rb'))['ids']
model = Word2Vec.load(model_fn)

embeddings = emb.read2vec(kmers_fn,model,ids,k=k,v=v)
embed_fn = name + '_' + str(k) + '_' + 'kmerembed.pkl'

print('Saving ids and embeddings.')
six.moves.cPickle.dump({'ids':ids,'embeddings':embeddings},
        open(os.path.join(work_dir,embed_fn),'wb'),protocol=4)

