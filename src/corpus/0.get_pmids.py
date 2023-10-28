#!/usr/bin/python

'''
retrieve a set of pmids for a given
time interval for a specific topic
in this case single cell rnaseq
'''
from pathlib import Path
import requests
from requests.utils import requote_uri
from xml.etree import ElementTree as ET

BASE_DIR = str(Path(__file__).resolve().parent.parent)
URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term="
MAX_IDS = 999999999
topics = ["(scRNAseq)", "(single+cell+RNAseq)", "(single-cell+RNA-seq)", "(single-cell+RNA-sequencing)", "(single-cell+transcriptomics)", "(single-cell+transcriptome)"]
pub_types = ["(Classical+Article)", "(Clinical+Study)", "(Journal+Article)"]
date_range = ["2017", "2023"]

paperIds = set()

pub_type_filter = "[PT]+OR+".join(pub_types) + "[PT]"
for t in topics:
    q = "(" + t + "[TIAB]+AND+(" + pub_type_filter 
    q += "+AND+(free only pmc[Filter]))"
    q += "&mindate=" + date_range[0] + "&maxdate=" + date_range[1]
    # [TIAB] is for searching [Title/Abstract], if not included non-wanted with no relevance may be added
    s = URL + requote_uri(q) + '&retmax=' + str(MAX_IDS)
    print(s)
    fetch = requests.get(s)

    # parse the XML
    root = ET.fromstring(fetch.text)
    for elm in root.find('IdList'):
        paperIds.add(elm.text)

# write to file
out = open(BASE_DIR + "/data/scrnaseq_pmids.txt", "w")
for p in paperIds:
    out.write(p + "\n")
print("number of papers: " + str(len(paperIds)))
out.close()