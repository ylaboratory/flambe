#!/usr/bin/python

'''
takes as input:
- list of scrnaseq_pmids.txt output from get_pmids.py
- output of download_pmc_ftp.sh
downloads and processes their xml files into data/pmc/full_xmls/
'''

import os
from urllib.request import urlopen
from io import BytesIO
import tarfile


pmc_ftp_url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/"


xml_out_dir = "../data/pmc/full_xmls/"
os.makedirs(xml_out_dir, exist_ok=True)

print("reading in list of pmids...")
want_pmids = set()
with open('../data/scrnaseq_pmids.txt') as f:
    for line in f:
        want_pmids.add(line.strip())

print("total pmcs wanted: ", len(want_pmids))

accessible_pmcs = set()
print("proccessing oa pmcs...")
with open('../data/pmc/oa_file_list.txt') as f:
    f.readline()
    for line in f:
        l = line.strip().split('\t')
        pmc = l[2]
        pmid = l[3].replace('PMID:', '')
        if pmid in want_pmids:
            accessible_pmcs.add(pmc)

            down_url = pmc_ftp_url + l[0]
            pmc_targz = urlopen(down_url)
            tar = tarfile.open(name=None, mode="r:gz", fileobj=BytesIO(pmc_targz.read()))
            xml_files = [name for name in tar.getnames() if name.endswith('nxml')]
            if len(xml_files) > 1:
                print("had multiple nxml files: ", pmc)
                tar.close()
                continue

            with open(xml_out_dir + pmc + '.nxml', 'wb') as out:
                out.write(tar.extractfile(xml_files[0]).read())
                tar.close()
print("total oa pmcs processed: ", len(accessible_pmcs))

print("reading in author manuscript lists...")
file_head = "../data/pmc/author_manu/author_manuscript_xml.PMC00"
file_tail = "xxxxxx.baseline.2022-12-16"
for i in range(1, 10):
    print(str(i) + "....")
    tar = tarfile.open(file_head + str(i) + file_tail + ".tar.gz", "r:gz") 
    with open(file_head + str(i) + file_tail + ".filelist.txt") as f:
        f.readline()
        
        for line in f:
            l = line.strip().split('\t')
            pmc = l[1]
            pmid = l[2]
            if pmid in want_pmids:
                accessible_pmcs.add(pmc)
                
                with open(xml_out_dir + pmc + '.xml', 'wb') as out:
                    out.write(tar.extractfile(l[0]).read())
    
    tar.close()


print("fully accessible pmcs:", str(len(accessible_pmcs)))
print("missing pmcs:", str(len(want_pmids) - len(accessible_pmcs)))