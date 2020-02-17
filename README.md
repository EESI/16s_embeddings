## DNA Read and Sample Embeddings

This work involves first encoding ("embedding") each sequence into a dense, 
low-dimensional, numeric vector space. We use Skip-Gram word2vec to embed 
k-mers, obtained from 16S rRNA amplicon surveys, and then leverage an 
existing sentence embedding technique to embed all sequences belonging to 
specific samples. Our work demonstrated that these representations are 
meaningful, and hence the embedding space can be exploited as a form of 
feature extraction for exploratory analysis. We showed that sequence 
embeddings preserve relevant information about the sequencing data such as 
k-mer context, sequence taxonomy, and sample class. In addition, embeddings 
are versatile features that can be used for many downstream tasks, such as 
taxonomic and sample classification. 

[Stephen Woloszynek, Zhengqiao Zhao, Jian Chen, and Gail L. Rosen. 16S rRNA 
sequence embeddings: Meaningful numeric feature representations of 
nucleotide sequences that are convenient for downstream analyses. 2019. PLOS
Computational Biology. 15(2). doi: 10.1371/journal.pcbi.1006721](https://doi.org/10.1371/journal.pcbi.1006721)

## Examples

# Train Embedding 

We first need to train our k-mer embeddings. We need to use a set of
reference sequences to train our k-mer embeddings. We used GreenGenes 16-5
in our manuscript. We will use a small set of kegg reference sequences 
here (/examples/kegg\subset.fasta.gz).

We need to specify the k-mer length *k*, the path of the reference 
sequences in fasta format, the output directory that will act as the location
for all subsequent input and output, and a prefix that will be used to name
all output files.

```bash
./0_genkmers.py -k 10 -i examples/kegg_subset.fasta.gz -o testing/ -p ex
```

This results in a .pkl file containing the ids of reads and a .csv.gz file
with all reads in proper format with headers removed. Next, we train
word2vec to obtain our k-mer embeddings. Here, we only need to specify the
working director, which is the output director from the previous script.
Other word2vec parameters can be passed, but we will go with mostly defaults
for now.

```bash
./1_train.py -w testing/ -s 123 -e 2
```

There will now be a \*\_model.pkl file in the working director, which we
will use to embed our reads and samples.

# Read Embeddings

For our read embedding, we will use a subset of reads from the Human
Microbiome Project (/examples/hmp\_subset.fasta.gz). This will embed each 
individual read into its own numeric vector. Similar to before, 
we only need to pass a couple arguments, the location of the working 
directory that contains the model we just trained, a prefix, and the HMP 
sequences. Because we subsetted the query sequences to so few, the total 
count for many of the k-mers will be 0. The approach requires us to 
normalize each embedding by the total number of reads. As we iterate 
through kmers, we divide the embedding by the total number of the given 
kmer, which will be 0 in this case. Thus, we will turn off the 
normalization for now. In a realistic example, the kmer count will not be 
0.

```bash
./2_embed_reads.py -n 0 -w testing/ -q examples/hmp_subset.fasta.gz -p exread
```

# Sample Embeddings

For sample embeddings, we start with individual fasta files for each
sample (/examples/samples/). Many software packages exist that can split a 
single fasta file in this way. One example is QIIME. Once we have these 
fasta files, we can calculate the total kmers for each sample and obtain 
their embeddings. Similar to before, we need to specify the working 
directory that contains the trained model, a prefix, and the location of 
the sample fasta files. For our sample fasta files, we are using subsets 
of reads from 10 samples from the American Gut data set.

```bash
./2_embed_samples.py -p exsamp -w testing/ -s samples/
```

The result will be a .pkl file containing the total kmers across all
samples and 10 individual .csv.gz files with the raw kmer embeddings.
The denoising has yet to occur. Next, merge, row-wise, all of the csv.gz
files. We specify the working directory and the prefix.

```bash
./3_merge_sample_embeddings.sh -w testing/ -p exsamp
```

Now we have exsamp\_remb\_raw\_merged.csv.gz. We'll run a script to
check the table for NaNs and drop any rows that contain them.

```bash
./3_check_sample_embeddings.py -w testing/
```

And lastly, we'll run a script to perform the denoising.

```bash
./3_svd_sample_embeddings.py -w testing/
```

The final file are the denoised sample embeddings: 
exsamp\_remb\_merged.csv.gz

## Datasets

Complete datasets mentioned here and used in the aforementioned 
manuscript can be found here: .
