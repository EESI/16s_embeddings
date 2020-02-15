#!/usr/bin/env python

from sys import stdout
import sys
import os
from os.path import splitext, isfile
from shutil import copyfile
import getopt
from glob import glob

import random
import logging
import gensim
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

err = '%s\n-k <k-mer size>\n-d <dim of neural net hidden layer>\n-s <window size>\n-n <number of negative samples>\n-f <k-mer downsampling frequency>\n-m <threshold to omit low frequency words>\n-w <path to working director for input and output files>\n-p <prefix for input and output files>\n-c <number of cores>\n-r <seed>' % (sys.argv[0])

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hk:d:s:n:f:m:e:w:p:c:r:',
            ['help','k','dim','win','negsamps','sampfreq','nmin','epochs','wdir','prefix','ncores','seed'])
except getopt.GetoptError:
    print(err)
    sys.exit()

seed = random.randint(1,9999999)
d = 64
w = 50
neg_samps = 10
samp_freq = 0.0001
n_min = 100
epochs = 3
n_cores = 1
k = 0
work_dir = 0
for opt, arg in opts:
    if opt in ('-h','--help'):
        print(err)
        sys.exit()
    elif opt in ('-d','--dim'):
        d = int(arg)
    elif opt in ('-s','--win'):
        w = int(arg)
    elif opt in ('-n','--negsamps'):
        neg_samps = int(arg)
    elif opt in ('-f','--sampfreq'):
        samp_freq = float(arg)
    elif opt in ('-m','--nmin'):
        n_min = int(arg)
    elif opt in ('-e','--epochs'):
        epochs = int(arg)
    elif opt in ('-p','--prefix'):
        prefix = arg
    elif opt in ('-w','--wdir'):
        work_dir = arg
    elif opt in ('-c','--ncores'):
        n_cores = int(arg)
    elif opt in ('-r','--seed'):
        seed = int(arg)

if work_dir != 0:
    kmers_path = [f for f in glob(work_dir + '/*kmers.csv.gz')]
    if len(kmers_path) > 1:
        print('More than one kmer file in working director with prefix')
        sys.exit()
    else:
        kmers_path = kmers_path[0]
    try:
        k = int(kmers_path.split('_')[-2])
        print('k=%s extracted from kmer filename' % (k))
        prefix = os.path.basename('_'.join(kmers_path.split('_')[:-2]))
        print('Prefix set as %s from kmer filename' % (prefix))
    except:
        pass

if k == 0:
    print('k not specified in kmer file filename via -i or via -k')
    sys.exit()

if not os.path.exists(work_dir):
    os.makedirs(work_dir)

model_fn = prefix + '_' + str(k) + '_' + str(d) + \
        '_' + str(epochs) + '_' + str(w) + '_' + \
        str(neg_samps).replace('0.','') + '_' + \
        str(samp_freq) + '_' + str(n_min) + '_model.pkl'
model_path = os.path.join(work_dir,model_fn)

if not os.path.exists(model_path):

    kmers_init = LineSentence(kmers_path,max_sentence_length=100000)

    model = Word2Vec(kmers_init,sg=1,size=d,window=w,min_count=n_min,negative=neg_samps,
            sample=samp_freq,iter=epochs,workers=n_cores,seed=seed)

    model.save(model_path)

else:

    print('%s exists' % model_path)
    sys.exit()
