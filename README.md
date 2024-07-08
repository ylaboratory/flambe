# FlaMBe: flow annotations for multiverse biological entities

This repository contains datasets for tissue and tool named entity recognition,
annotation files for biological workflow extraction, disambiguation files,
and code used for curation, and the model use cases.

## Citation

> [Into the Single Cell Multiverse: an End-to-End Dataset for 
Procedural Knowledge Extraction in Biomedical Texts.](https://openreview.net/forum?id=6iRH9SITva)
Dannenfelser R, Zhong J, Zhang R, Yao V. NeurIPS 2024 Datasets and Benchmarks Spotlight.

## Organization

This repo is organized into several sections part of which is stored on [zenodo](https://zenodo.org/records/10050681).

- `data`: contains processed datasets for BioNLP tasks (on [zenodo](https://zenodo.org/records/10050681))
- `src`: contains the code used to extract data from PMC, build BERT models, and all related tasks to assemble a collection of data for manual curation
- `models`: fine-tuned PubmedBERT models for tissue and cell type tagging (on [zenodo](https://zenodo.org/records/10050681))

The data section is further divided into sections depending on downstream use cases:

- `corpus`: the text for 55 full papers from PubMed and PMC
- `disambiguation`: all files used for downstream disambiguation of tissue, cell type, and software terms
- `sentiment`: files for tool context prediction (similar to sentiment classification)
- `tags`: contains IOB and CoNLL tag files for fine-tuning BERT-based models for tissue
and cell type tagging, as well as software tagging.
- `workflow`: 3 files of curated tuples for various tool and workflow extraction tasks

## Annotation file formats

In this section, we describe in detail the various file formats of the accessory files and
main annotation files: IOB, CoNLL, disambiguation, and workflow files.

#### IOB files

Files ending in `.iob` follow the 
[Inside-outside-beginning](https://en.wikipedia.org/wiki/Insideâ€“outsideâ€“beginning_(tagging)) 
tagging format. These files are tab-delimited text files made with the SpaCy english tokenizer
having one token per line followed by a tag signifying a named entity. Unlike traditional IOB files,
we include additional lines that mark the start and end of papers or abstracts. These lines contain
the PMID or PMC identifier in the token column and the words `begin` or `end` in the tag column.

Note: `iob_functions.py` in the `src` folder has a set of useful functions for interacting with these
iob files.

#### CoNLL files

CoNLL files, like the IOB files have tokenized text for both full text and abstracts, but are
augmented with additional information such as disambiguated terms and identifiers.
Unlike the IOB files, which cover the entire abstract and full text corpus, we release one
CoNLL per paper.

#### Licensing files

Each paper has its own license and usage agreements. We keep track of these licenses for our
collection of full text and abstract papers. Each file is indexed either by PubMed Central (pmc) 
identifiers (in the case of full text), or PubMed ids (pmid). These files can be found in
the `data` directory ending in `_licenses.txt`.

#### Disambiguation files

Tissues and cell types are disambiguated to the 
[NCI Thesaurus](https://www.ebi.ac.uk/ols/ontologies/ncit). In the 
`tissue_ned_table.txt` file we take tokens that were present in the full text 
and abstract files and map them to NCIT identifiers. An additional file
`NCI_thesaurus_info.txt` contains the relevant identifiers, names, aliases,
and descriptions for the `tissue`, `organ`, `body part`, `fluid`, and `cell type`
branches of the ontology.

Tools are manually disambiguated to a standardized name or acronym taken
from their initial paper or acronym. In `tool_ned_table.txt` we map tokens
present in the full text and abstract files to these standardized names.
The file `tools_info.txt` maps these standardized names to project websites
(personal or GitHub links) and to the original publication.

The `uns_method_ned.txt` is a tab delimited file that maps tokens present
in the full text and abstract files to standardized method names.
Where applicable we link the method to a wikipedia or library page (e.g., scikit-learn).

#### Workflow files

Workflow files are presented as three tab delimited files of tuples.

- `sample` file links any experimental assay (e.g., RNA-seq, single cell RNA-seq, ChIP-seq) with tissue and cell type annotations
- `tools_applied` file joins samples, tools, and the tool context
- `sequence` file captures pairs of applied tools

Each of the three files start each new line with PMC identifiers linking defined annotations with relevant papers. Furthermore, the `sample` and `tools_applied` files have sequential id numbers within each PMC for the extraction of unambiguous sample workflows. When one sample in the `sample` file can be described with multiple tissue and cell type annotations we tie it back to the same sequential sample identifier.

We constrain the set of tool contexts to the following list of actions:

```
Alignment, Alternative Splicing, Batch Correction, Classification, CNV calling, Clustering, Deconvolution, Differential Expression, Dimensionality Reduction, Gene Enrichment / Gene set analysis, Integration, Imputation, Marker Genes / Feature Selection, Networks, Normalization, Quality Control, Quantification, Rare Cell Identification, Simulation, TCR, Tree Inference, Visualization, Variable Genes
```

## Running the scripts

We recommend using conda for installing all necessary packages. Once conda is installed 
get started by creating and activating the virtual environment.

 ```bash
 conda env create -f env.yml
 conda activate flambe
 ```

The jupyter notebooks can be used to fine-tune different BERT models hosted on HuggingFace.
The various python scripts can be used to download and assemble full text and biomedical abstracts
from PubMed and PubMedCentral.
