#!/usr/bin/python

'''
optional step after parsing pmc files to
filter parsed pmc files for simplified original topic words
because pubmed search doesn't enforce exact match
'''
import os
import shutil

topics = ["scRNA", "single cell RNA", "single-cell RNA", "single-cell-RNA", "single cell transcriptom"]

parsed_dir = "../data/pmc/parsed_text/"
parsed_filt_dir = "../data/pmc/parsed_text_filtered/"
os.makedirs(parsed_filt_dir, exist_ok=True)

not_tiny_pmcs = set()
with open("../data/pmc/parsed_text_wrefs.txt") as f:
    f.readline()
    for line in f:
        l = line.strip().split('\t')
        if int(l[1]) > 10:
            not_tiny_pmcs.add(l[0] + '.txt')

for pmc in os.listdir(parsed_dir):
    if pmc in not_tiny_pmcs:
        with open(parsed_dir + pmc) as f:
            all_text = f.read()
            sc_in_f = False
            for topic in topics:
                if topic in all_text:
                    sc_in_f = True
            
            if sc_in_f: 
                shutil.copy(parsed_dir + pmc, parsed_filt_dir + pmc)
