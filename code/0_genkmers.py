#!/usr/bin/env python

import sys
import time
import getopt
import os
import gzip
import six.moves.cPickle
from smart_open import smart_open
import gensim
from embed_functions import open_file_method

err = '%s\n-k <k-mer size>\n-v <number of kmers before print>\n-i <input file path>\n-o <output file dir>\n-p <output file prefix>' % (sys.argv[0])

try:
    opts, args = getopt.getopt(sys.argv[1:],'hk:v:i:o:p:',['help','k','verbose','ipath','odir','prefix'])
except getopt.GetoptError:
        print(err)
        sys.exit()
if len(opts) == 0:
    print(err)
    sys.exit()

v = 100

for opt, arg in opts:
    if opt in ('-h','--help'):
        print(err)
        sys.exit()
    elif opt in ('-k'):
        k = int(arg)
    elif opt in ('-v','--verbose'):
        v = int(arg)
    elif opt in ('-i','--ipath'):
        reads_fn = arg
    elif opt in ('-o','--odir'):
        data_dir = arg
    elif opt in ('-p','--prefix'):
        name = arg

print('\nGenerating kmers.')

ids_fn = os.path.join(data_dir,name + '_' + str(k) + '_ids.pkl')
kmers_fn = os.path.join(data_dir,name + '_' + str(k) + '_kmers.csv.gz')

if os.path.exists(ids_fn):
    print('%s already exists' % (ids_fn))
    sys.exit()
if os.path.exists(kmers_fn):
    print('%s already exists' % (kmers_fn))
    sys.exit()

alphabet = {'A':'A','C':'C','G':'G','T':'T'}

print(name + ':\tLoading reads.')

open_file = open_file_method(reads_fn)
in_file = open_file(reads_fn)

out_kmers = gzip.open(kmers_fn,'w')

ids = []
read_idx = 0
t1 = time.time()

for line in in_file:
  l = line.decode('utf-8').strip('\n')
  if l[0] == '>':
    ids.append(l.strip('>'))
    read_idx += 1
    if read_idx % v == 0:
      t_diff = str(round((time.time() - t1)/60,1)) + ' min.'
      print(name + ':\tProcessed ' + str(read_idx) + ' reads in ' + t_diff)
  else:
    read = ''
    M = len(l) - k + 1
    for n in range(M):
      l = list(l)
      nts = l[n:n+k]
      kmer = ''
      for nt in nts:
        try:
          kmer += alphabet[nt]
        except:
          continue
      if len(kmer) == k:
          read = read + kmer + ' '
    read += '\n'
    out_kmers.write(read.encode())
out_kmers.close()

print(name + ':\tDumping ids.')
six.moves.cPickle.dump({'ids':ids},open(ids_fn,'wb'))
