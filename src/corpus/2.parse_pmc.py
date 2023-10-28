#!/usr/bin/python

'''
takes as input:
- directory of downloaded xml files in full_xmls
outputs parsed text files in data/pmc/parsed_text
with title, abstract, section name, section
(new line separated, only outputs section names when it is different than previous)
'''

import os
import pubmed_parser as pp
import re

xml_dir = "../data/pmc/full_xmls/"

parsed_out_dir = "../data/pmc/parsed_text/"
os.makedirs(parsed_out_dir, exist_ok=True)

clean_pattern = "[ \t\n\r]+"

for xml_file in os.listdir(xml_dir):
    if xml_file.endswith('xml'):
        try:
            simp_info = pp.parse_pubmed_xml(xml_dir + xml_file)
        except:
            print("pubmed parse error: " + xml_file)
            continue

        pmc = 'PMC' + simp_info['pmc']

        all_out =  open(parsed_out_dir + pmc + ".txt", 'w')

        all_out.write(re.sub(clean_pattern, ' ', simp_info['full_title']) + '\n')
        all_out.write(re.sub(clean_pattern, ' ', simp_info['abstract']) + '\n')

        pmc_all_paras = pp.parse_pubmed_paragraph(xml_dir + xml_file, all_paragraph=True)
        if len(pmc_all_paras) == 0:
            print("No body: " + pmc + '\n')
        else:
            section = pmc_all_paras[0]['section']
            all_out.write(re.sub(clean_pattern, ' ', section) + '\n')

            for para in pmc_all_paras:
                if para['section'] != section:
                    section = para['section']
                    all_out.write(re.sub(clean_pattern, ' ', section) + '\n')
                
                all_out.write(re.sub(clean_pattern, ' ', para['text']) + '\n')

        all_out.close()