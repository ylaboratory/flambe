'''
handy functions for interacting with iob
files that are used across different ipynbs
'''
import json
from collections import defaultdict
from spacy.tokens import Doc
from spacy.vocab import Vocab
from spacy.training import biluo_tags_to_offsets
from spacy.training import iob_to_biluo


def process_tab_delim_iob(fn):
    '''
    takes as input a path to a file name
    relative to the BASE_DIR
    file has iob format tab delimited
    returns a format accepted by NERDA
    '''
    sent = []
    tags = []
    s = []
    t = []
    
    with open(fn, "r") as f:
        for line in f:
            words = line.strip().split("\t")
            if len(words) == 1:  # get rid of some IOB artifacts
                continue
            if words[1] == "begin":
                continue
            if words[1] == "end":
                continue
            s.append(words[0])
            t.append(words[1])
            if words[0] == ".":
                sent.append(s)
                tags.append(t)
                s = []
                t = []
            
    if len(s) > 0:
        sent.append(s)
        tags.append(t)
    return {"sentences": sent, "tags": tags}


def combine_tags(tset, tag_to_replace, replacement):
    '''
    takes a dictionary of sentences and tags
    and merges tag_to_replace with replacement
    under replacement as the unifying tag
    '''
    updated_tags = []
    for l in tset["tags"]:
        tmp = []
        for elm in l:
            tmp.append(elm.replace(tag_to_replace, replacement))
        updated_tags.append(tmp)
    return {"sentences": tset["sentences"], "tags": updated_tags}


def tag_stats(tset):
    '''
    takes a set of data and tallies the total number
    of tag types
    '''
    tally = {}
    
    for l in tset["tags"]:
        for elm in l:
            if elm in tally:
                tally[elm] += 1
            else:
                tally[elm] = 1
    
    return tally


def get_tag_totals(target_tag, iob):
    '''
    for a single tag (e.g., tissue, cell_type)
    tally up the number of appearances and return as
    a dictionary with keys as unique tag values (e.g., "heart")
    , and values as the totals 
    '''
    tally = defaultdict(int)
    prev = ""  # marker for multi word tissues / cell types
    for i, paper_tags in enumerate(iob["tags"]):
        for j, tag in enumerate(paper_tags):
            if target_tag == tag[2:]:
                prev += iob["sentences"][i][j] + " "
            else:
                prev = prev.strip().lower()
                if prev != "":
                    tally[prev] += 1
                prev = ""
        if prev != "":
            prev = prev.strip().lower()
            tally[prev] += 1
            prev = ""
    if prev != "":
        prev = prev.strip().lower()
        tally[prev] += 1
    
    return tally


def split_training(tset, per_split):
    '''
    takes a dictonary corresponding to a training set
    and a percentage split size for validation and returns
    a set for training and validation as tuple of dictionaries
    '''
    if per_split <= 0:
        print("WARNING: split size is equal to or less than 0 no split was performed")
        return (tset, {})
    n_valid = int(len(tset["tags"]) * per_split)

    valid = {"sentences": tset["sentences"][:n_valid], "tags": tset["tags"][:n_valid]}
    train = {"sentences": tset["sentences"][n_valid:], "tags": tset["tags"][n_valid:]}
    
    return(train, valid)


def split_training_n(tset, t_size):
    '''
    similiar to split_training() except it
    takes a number for the training size instead
    of a percentage
    as always returns a set for training and validation
    as tuple of dictionaries
    '''
    if t_size <= 0:
        print("WARNING: size of the training set is equal to or less than 0 no split was performed")
        return (tset, {})

    train = {"sentences": tset["sentences"][:t_size], "tags": tset["tags"][:t_size]}
    valid = {"sentences": tset["sentences"][t_size:], "tags": tset["tags"][t_size:]}
    
    return(train, valid)


def split_training_random(dataset, k):
    '''
    similiar to split_training() except it
    takes a number for the training size instead
    of a percentage and samples k random elements
    from the dataset and returns the remainder of items.
    as always returns a set for training and validation
    as tuple of dictionaries
    '''
    
    # since this function will directly modify the data
    # make sure to copy the dict by value
    tset = copy.deepcopy(dataset) 
    
    if k <= 0:
        print("WARNING: size of the sample is equal to or less than 0 no split was performed")
        return (tset, {})
    
    res = {"sentences": [], "tags": []}
    for i in range(k):
        ind = random.randint(0, len(tset))
        res['sentences'].append(tset['sentences'][ind])
        res['tags'].append(tset['tags'][ind])
        del tset['sentences'][ind]
        del tset['tags'][ind]
    
    return(res, tset)


def make_k_folds(tset, k):
    '''
    takes a dictonary corresponding to a training set
    and a number corresponding to the total number of folds
    then returns a list of tuples containing the training 
    and validation sets corresponding to the number of folds
    '''
    res = []
    if k <= 1:
        print("WARNING: split size is equal to or less than 1. no split was performed")
        return(res)
    
    split_size = int(len(tset["tags"]) / k)
    
    print("split size: " + str(split_size) + " total: " + str(len(tset["tags"])))
    for i in range(0, k):
        #print("i: " + str(i))
        if i == 0:
            train = {"sentences": tset["sentences"][split_size:len(tset["tags"])], "tags": tset["tags"][split_size:len(tset["tags"])]}
            valid = {"sentences": tset["sentences"][i*split_size:i*split_size + split_size], "tags": tset["tags"][i*split_size:i*split_size + split_size]}
            #print("train: " + str(split_size) + ":" + str(len(tset["tags"])))
            #print("test: " + str(i*split_size) + ":" + str(i*split_size + split_size))
        else:
            if i == k - 1:
                train = {"sentences": tset["sentences"][0:len(tset["tags"]) - split_size], "tags": tset["tags"][0:len(tset["tags"]) - split_size]}
                valid = {"sentences": tset["sentences"][len(tset["tags"]) - split_size:len(tset["tags"])], "tags": tset["tags"][len(tset["tags"]) - split_size:len(tset["tags"])]}
                #print("train: 0:" + str(len(tset["tags"]) - split_size))
                #print("test: " + str(len(tset["tags"]) - split_size) + ":" + str(len(tset["tags"])))
            else:
                train = {"sentences": tset["sentences"][0:i*split_size] + tset["sentences"][i*split_size + split_size:len(tset["tags"])],
                         "tags": tset["tags"][0:i*split_size] + tset["tags"][i*split_size + split_size:len(tset["tags"])]}
                valid = {"sentences": tset["sentences"][i*split_size:i*split_size + split_size], 
                         "tags": tset["tags"][i*split_size:i*split_size + split_size]}
                #print("train: 0:" + str(i*split_size)  + " and " + str(i*split_size + split_size) + ":" + str(len(tset["tags"])))
                #print("test: " + str(i*split_size) + ":" + str(i*split_size + split_size))
        res.append((train, valid))
    
    return(res)


def join_punct(seq, chars='.,;?!)-'):
    '''
    custom function to combine a list such that
    punctuation is combined with the preceeding
    element.
    
    inspired by: https://stackoverflow.com/questions/15950672/
    join-split-words-and-punctuation-with-punctuation-in-the-right-place
    '''
    chars = set(chars)
    seq = iter(seq)
    current = next(seq)

    for nxt in seq:
        if nxt in chars:
            current += nxt
        else:
            yield current
            current = nxt

    yield current
    
    
def join_punct_rear(seq, chars='(-'):
    '''
    custom function to combine a list such that
    punctuation is combined with the following
    element.
    '''
    chars = set(chars)
    seq = iter(seq)
    current = next(seq)

    for nxt in seq:
        if (current in chars) or (current[-1] in chars):
            current = current + nxt
        else:
            yield current
            current = nxt
    
    yield current
 

# TODO speed this up
def convert_int_to_iob(ds, tagname):
    '''
    Takes an NER dataset (ds) from HuggingFace
    and converts into an IOB file stored in a similar
    manner as ones that are compatible with the NERDA
    models. The tagname parameter is used in the IOB
    creation for the type of field being tagged.
    '''
    sent = []
    tags = []
    
    for i in ds['id']:
        sent.append(ds['tokens'][int(i)])
        tmp = []
        for t in ds['ner_tags'][int(i)]:
            if t == 0:
                tmp.append('O')
            elif t == 1:
                tmp.append('B-' + tagname)
            elif t == 2:
                tmp.append('I-' + tagname)
            else:
                print("Strange tag detected: " + str(t))
        tags.append(tmp)
    
    return ({"sentences": sent, "tags": tags})


def save_iob_to_file (iob, fn):
    out = open(fn, "w")
    for sent_i in range(len(iob[0])):
        for i, txt in enumerate(iob[0][sent_i]):
            out.write(txt + "\t" + iob[1][sent_i][i] + "\n")
    out.close()
    

def flatten_iob(iob):
    '''
    removes the sentences level lists
    '''
    flat = {'sentences':[], 'tags': []}
    for i, l in enumerate(iob[0]):
        for j, tok in enumerate(iob[0][i]):
            flat['sentences'].append(tok)
            flat['tags'].append(iob[1][i][j])
    return flat


def flatten_text(iob):
    '''
    collapses the sentences in the 
    iob
    '''
    flat = ""
    start = True
    for i, l in enumerate(iob[0]):
        for j, tok in enumerate(iob[0][i]):
            if start: 
                flat = tok
                start = False
            else:
                flat += " " + (tok)
    return flat


def get_offsets(iob):
    '''
    returns a list of spans in a passage of text
    given an iob
    '''
    flat = flatten_iob(iob)
    doc = Doc(Vocab(), words=flat['sentences'])
    tags = iob_to_biluo(flat['tags'])
    offsets = biluo_tags_to_offsets(doc, tags)
    
    res = []
    for o in offsets:
        res.append({'start': o[0], 'end': o[1], 'label': o[2]})
    
    return res


def json_wrap(iob, pmid):
    '''
    given the original set of text and a set of iob
    tags corresponding to the orig text return a json
    format that can be read into prodigy
    '''
    offsets = get_offsets(iob)
    
    return {'text': flatten_text(iob), 'spans': offsets,  "meta": {"source": pmid}}


def json_wrap_two_iobs(iob1, iob2, pmid):
    '''
    given the original set of text and two sets of iob
    tags corresponding to the orig text return a json
    format that can be read into prodigy
    '''
    offsets1 = get_offsets(iob1)
    offsets2 = get_offsets(iob2)
    
    return {'text': flatten_text(iob1), 'spans': offsets1 + offsets2,  "meta": {"source": pmid}}


def parse_perfs(p, names):
    '''
    take a list of performance outputs and 
    and parses into a list of dictionary objects
    and a reorganized pandas df
    '''
    res = []
    tmprows = []
    for i, elm in enumerate(p):
        obj = {}
        for idx, row in elm.iterrows():
            obj[row["Level"]] = {'f1': float(row["F1-Score"]), 'prec': float(row["Precision"]), 'recall': float(row["Recall"])}
            if ("ACRONYM" not in row["Level"]) and ("MICRO" not in row["Level"]):
                tmprows.append({'method': names[i], 'tag': row["Level"], 'f1': float(row["F1-Score"]), 'prec': float(row["Precision"]), 'recall': float(row["Recall"])})
        res.append({names[i]: obj})
            
    newdf = pd.DataFrame(tmprows)
    return (res, newdf)


def remove_tag(tset, tag_to_reset):
    '''
    takes a dictionary of sentences and tags
    and removes a tag from the annotations
    '''
    updated_tags = []
    for l in tset["tags"]:
        tmp = []
        for elm in l:
            if tag_to_reset in elm:
                tmp.append('O')
            else:
                tmp.append(elm)
        updated_tags.append(tmp)
    return {"sentences": tset["sentences"], "tags": updated_tags}


def save_iob_to_file (iob, fn):
    out = open(fn, "w")
    for sent_i in range(len(iob[0])):
        for i, txt in enumerate(iob[0][sent_i]):
            out.write(txt + "\t" + iob[1][sent_i][i] + "\n")
    out.close()