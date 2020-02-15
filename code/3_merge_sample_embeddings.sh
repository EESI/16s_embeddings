#!/bin/bash

OPTIND=1

while getopts "h?w:p:" opt; do
    case "$opt" in
        w)  work_dir=$OPTARG
            ;;
        p)  prefix=$OPTARG
            ;;
        h)  echo "$(basename $0) -w <path to working directory> -p <prefix for output files>"
            exit 1
            ;;
        *)  echo "$(basename $0) -w <path to working directory> -p <prefix for output files>"
            exit 1
            ;;
    esac
done
shift "$((OPTIND -1))"

echo "Merging samples."
embeddings=($(ls ${work_dir}/*remb_raw.csv.gz))
out="${work_dir}/${prefix}_remb_raw_merged.csv"
rm $out
i=0
n=1
echo -ne "[$n]\t"
for e in ${embeddings[@]}
do
    zcat $e >> $out
    echo -ne "."
    ((i++))
    [ $i -eq 100 ] && { ((n+=100)); echo -ne "\n[$n]\t" ; i=0; }
done
echo -ne "\nCompressing\n"
gzip -f $out

exit 0
