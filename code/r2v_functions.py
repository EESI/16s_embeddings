#!/usr/bin/env python

import sys
#from sys import argv
import os
#import zipfile
from os.path import splitext, isfile
import gzip
import csv
import six.moves.cPickle
from glob import glob

import numpy as np
import pandas as pd
#from itertools import product
#from operator import itemgetter
#from sklearn.manifold import TSNE
import random
import math
import time

from sklearn.decomposition import TruncatedSVD
from gensim.models import Word2Vec
#from gensim.models.word2vec import LineSentence

import embed_functions as emb


def open_file_method_decode(path):
    ext = splitext(path)[1]
    if (ext == '.gz'):
        def open_file(path):
            return gzip.open(path)
        def read_line(line):
            return line.decode('utf-8').strip('\n')
    else:
        def open_file(path):
            return open(path,'r')
        def read_line(line):
            return line
    return open_file, read_line

def generate_kmers(line,k,alphabet={'A':'A','C':'C','G':'G','T':'T'}):
    read = ''
    l = line.strip('\n')
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
            yield kmer

def embed_reads(path_sample,path_totalkmers,path_model,path_out,k=None,
        normread=True,to_sample=False,a=1e-5,n_components=1,
        delim=None,svm=True,verbose=True,v=1000):
    
    sample_id = os.path.basename(os.path.normpath(path_sample)).split('.')[0]

    fn_sample_base = path_model.split('/')[-1]
    fn_sample_base = '_'.join(fn_sample_base.split('_')[1:-1]) + '_' + str(a) 

    if verbose:
        print('Loading total kmers.')
    total_kmers = six.moves.cPickle.load(open(path_totalkmers,'rb'))
    
    if verbose:
        print('Loading model.')
    model = Word2Vec.load(path_model)
    d = model.trainables.layer1_size
    model = model.wv

    open_file, read_line = open_file_method_decode(path_sample)
    
    total_reads = sum([1 for i in open_file(path_sample)])//2
    if verbose:
        print('Total reads in sample %s: %s.' % (sample_id,total_reads))

    if normread:
        print('Normalizing each read by total number of kmers in that read.')
    else:
        print('Normalizing each read by total number of kmers in the sample.')

    file = open_file(path_sample)

    i = 0
    read_ids = []
    n_kmer = 0
    reads = np.zeros((d,total_reads),dtype='float64')
    for line in file:
        line = read_line(line)
        if line[0] == '>':
            if delim is None:
                read_id = line[1:-1]
            else:
                read_id = line[1:line.find(delim)]
            read_ids.append(read_id)
            if verbose:
                if i % v == 0:
                    print('Processing %s: %s/%s.' % (read_id,i,total_reads))
        else:
            r = np.zeros(d,dtype='float64')
            kmers = generate_kmers(line,k)
            for kmer in kmers:
                try:
                    r += model[kmer] * a/(a + total_kmers[kmer])
                    n_kmer += 1
                except KeyError:
                    continue
            reads[:,i] = r
            if normread:
                reads[:,i] /= n_kmer
                n_kmer = 0
            i += 1

    if not normread:
        reads /= n_kmer

    fn_sample = '%s_%s_remb_raw.csv.gz' % (sample_id,fn_sample_base) 
    path_out2 = os.path.join(path_out,fn_sample)
    if verbose:
        print('Saving reads to %s.' % (path_out2))

    if to_sample:
        df = pd.DataFrame(np.sum(reads.T,axis=0).reshape(1,-1),index=[sample_id])
        df.to_csv(path_out2,compression='gzip',header=False)
    else:
        df = pd.DataFrame(reads.T,index=read_ids)
        df.to_csv(path_out2,compression='gzip')

    if svm:
        if verbose:
            print('Performing SVD: (%s,%s).' % (d,total_reads))
        svd = TruncatedSVD(n_components=n_components, n_iter=7, random_state=0)
        svd.fit(reads)
        pc = svd.components_
        reads -= reads.dot(pc.T) * pc

        fn_sample = '%s_%s_remb.csv.gz' % (sample_id,fn_sample_base) 
        path_out2 = os.path.join(path_out,fn_sample)
        if verbose:
            print('Saving reads to %s.' % (path_out2))
        if to_sample:
            df = pd.DataFrame(np.sum(reads.T,axis=0).reshape(1,-1),index=[sample_id])
            df.to_csv(path_out2,compression='gzip',header=False)
        else:
            df = pd.DataFrame(reads.T,index=read_ids)
            df.to_csv(path_out2,compression='gzip')

def calc_total_kmers(path_reads,path_model,k,verbose=True,v=10000):
    
    model = Word2Vec.load(path_model)
    model_wv = model.wv
    del model
    
    kmer_counter = {kmer:0 for kmer in model_wv.vocab}

    open_file, read_line = open_file_method_decode(path_reads)
    file = open_file(path_reads)

    v_counter = 0
    t_total = 0
    t1 = time.time()
    for line in file:
        line = read_line(line)
        if line[0] == '>':
            continue
        else:
            if verbose:
                if v_counter % v == 0:
                    t2 = time.time()
                    t_diff = (t2-t1)/60
                    t_total += t_diff
                    print('Processing read %s. Last batch: %.3f minutes. Total time: %.3f hours.' % (v_counter, t_diff, t_total/60))
                    t1 = time.time()
                v_counter += 1
            kmers = generate_kmers(line,k)
            for kmer in kmers:
                if kmer in model_wv:
                    kmer_counter[kmer] += 1

    total_kmers = np.sum([count for count in kmer_counter.values()])
    kmer_counter = {kmer:count/total_kmers for kmer,count in kmer_counter.items()}

    return kmer_counter

def calc_total_kmers_split(samp_dir,path_model,k,verbose=True,v=10000):
    
    model = Word2Vec.load(path_model)
    model_wv = model.wv
    del model
    
    kmer_counter = {kmer:0 for kmer in model_wv.vocab}

    for f in glob(samp_dir + '/*'):

        print('Processing file %s' % (f))

        open_file, read_line = open_file_method_decode(f)
        file = open_file(f)

        v_counter = 0
        t_total = 0
        t1 = time.time()
        for line in file:
            line = read_line(line)
            if line[0] == '>':
                continue
            else:
                if verbose:
                    if v_counter % v == 0:
                        t2 = time.time()
                        t_diff = (t2-t1)/60
                        t_total += t_diff
                        print('Processing read %s. Last batch: %.3f minutes. Total time: %.3f hours.' % (v_counter, t_diff, t_total/60))
                        t1 = time.time()
                    v_counter += 1
                kmers = generate_kmers(line,k)
                for kmer in kmers:
                    if kmer in model_wv:
                        kmer_counter[kmer] += 1

    total_kmers = np.sum([count for count in kmer_counter.values()])
    kmer_counter = {kmer:count/total_kmers for kmer,count in kmer_counter.items()}

    return kmer_counter
