#!/usr/bin/env python

import sys
import os
import getopt
from glob import glob
#from os.path import splitext, isfile
#import gzip
#import csv
import six.moves.cPickle

import r2v_functions as r2v


err = '%s\n-p <prefix of working files>\n-m <path of gensim model>\n-q <path to k-mers file to be embedded>\n-w <path of working directory>\n-k <k-mer length>\n-a <amount of k-mer downweighting>\n-n <logical whether to normalize by read>\n-v <number of lines to process before printing>' % (sys.argv[0])

try:
    opts, args = getopt.getopt(sys.argv[1:],'hp:m:q:w:k:a:v:n:',['help','prefix','modpath','qpath','wdir','k','a','verbose','nr'])
except getopt.GetoptError:
    print(err)
    sys.exit()
if len(opts) == 0:
    print(err)
    sys.exit()

a = 1e-05
k = 0
v = 1000
path_model = 0
for opt, arg in opts:
    if opt in ('-h','--help'):
        print(err)
        sys.exit()
    elif opt in ('-p','--prefix'):
        name = arg
    elif opt in ('-m','--modpath'):
        path_model = arg
    elif opt in ('-q','--qpath'):
        path_reads = arg
    elif opt in ('-w','--wdir'):
        work_dir = arg
    elif opt in ('-k'):
        k = int(arg)
    elif opt in ('-v','--verbose'):
        v = int(arg)
    elif opt in ('-n','--normread'):
        if arg == '1' or arg == '0':
            nr = bool(int(arg))
        elif arg == 'True':
            nr = True
        elif arg == 'False':
            nr = False
        else:
            print('-n must be 0, 1, False, or True')
            sys.exit()
if path_model == 0:
    path_model = [f for f in glob(work_dir + '/*') if 'model.pkl' in f]
    if len(path_model) == 1:
        path_model = path_model[0]
    else:
        print('Multiple models in work dir and model not specific via -m')
        sys.exit()
    try:
        k = int(path_model.split('_')[-8])
        print('k=%s extracted from kmer file filename' % (k))
    except IndexError:
        pass
if k == 0:
    print('k not specified in kmer file filename via -i or via -k')
    sys.exit()

fn_totalkmers = '%s_%s_totalkmers.pkl' % (name,str(k))
path_totalkmers = os.path.join(work_dir,fn_totalkmers)

if not os.path.exists(work_dir):
    os.makedirs(work_dir)

if os.path.exists(fn_totalkmers):
    print('%s already exists' % (fn_totalkmers))
    sys.exit()

print('Calculating kmer totals for %s using model %s.' % (path_reads,path_model))
total_kmers = r2v.calc_total_kmers(path_reads,path_model,k,verbose=True,v=v)

print('Dump total kmers to %s' % (path_totalkmers))
six.moves.cPickle.dump(total_kmers,open(path_totalkmers,'wb'),protocol=4)

r2v.embed_reads(path_reads,path_totalkmers,path_model,work_dir,
        normread=nr,k=k,a=a,verbose=True,v=v)
