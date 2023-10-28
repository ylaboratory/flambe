#!/bin/bash
# downloads manifest for oa files
# and both filelist and tarballs for author manuscripts

src_dir=$(dirname "$0")
data_dir=$(cd "$src_dir"/../data || exit; pwd)

pmc_dir="$data_dir/pmc"
author_dir="$data_dir/pmc/author_manu"

mkdir -p "$author_dir"

pmc_oa_file="https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.txt"

if ! [[ -f "$pmc_dir/oa_file_list.txt" ]]; then
	echo "[$(date +%H:%M:%S)]: downloading GO obo file"
	wget -P "$pmc_dir" "$pmc_oa_file"
fi

pmc_author_batch_url="https://ftp.ncbi.nlm.nih.gov/pub/pmc/manuscript/xml/"
pmc_author_batch_file_head="author_manuscript_xml.PMC00"
pmc_author_batch_file_tail="xxxxxx.baseline.2022-12-16"

for i in $(seq 1 9);
do
    file_name="${pmc_author_batch_file_head}${i}${pmc_author_batch_file_tail}"
    if ! [[ -f "$author_dir/${file_name}.filelist.txt" ]]; then
        wget -P "$author_dir" "${pmc_author_batch_url}/${file_name}.filelist.txt"
    fi
    if ! [[ -f "$author_dir/${file_name}.tar.gz" ]]; then
        wget -P "$author_dir" "${pmc_author_batch_url}/${file_name}.tar.gz"
    fi
done
