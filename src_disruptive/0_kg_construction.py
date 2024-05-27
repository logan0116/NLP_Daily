import json
import os
from tqdm import tqdm
from collections import defaultdict

import logging

logging.basicConfig(level=logging.INFO)

"""
Field Name  Field Type  Description Example
id	string	paper ID	453e997ddb7602d9701fd3ad7
title   string  paper title Rewrite-Based Satisfiability Procedures for Recursive Data Structures
authors.name    string  author name Maria Paola Bonacina
author.org  string  author affiliation  Dipartimento di Informatica|Universit a degli Studi di Verona
author.id   string  author ID   53f47275dabfaee43ed25965    
venue.raw   string  paper venue name    Electronic Notes in Theoretical Computer Science(ENTCS) 
year    int published year  2007    
keywords    list of strings keywords    ["theorem-proving strategy","rewrite-based approach"... 
fos.name	string	paper fields of study	Data structure
fos.w	float	fields of study weight	0.48341
references	list of strings	paper references	["53e9a31fb7602d9702c2c61e","53e997f1b7602d9701fef4d1"...
n_citation  int citation number 19  
page_start  string  page start  "55"    
page_end    string  page end    "70"    
doc_type    string  paper type:journal,conference   Journal 
lang    string  detected language   en  
volume  string  volume  "174"   
issue   string  issue   "8" 
issn    string  issn    "Electronic Notes in Theoretical Computer Science"  
isbn    string  isbn    ""  
doi string  doi 10.1016/j.entcs.2006.11.039 
url list    external links  [https: 
abstract    string  abstract    Our ability to generate...  
indexed_abstract	dict	indexed abstract	'''IndexLength''':116,'''InvertedIndex'':{""data"":[49],'
v12_id  int v12 paper id    2027211529  
v12_authors.name    string  
v12 author name Maria Paola Bonacina    
v12_authors.org string  v12 author affiliation  Dipartimento di Informatica,Università degli Studi di Verona,Italy#TAB# 
v12_authors.id  int v12 author ID   669130765
"""


def data_cut():
    with open('dblp_v14.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 每500,000拆分成一个文件。
    for i in range(0, len(data), 500000):
        with open(f'data/dblp_v14_{i}.json', 'w', encoding='utf-8') as f:
            json.dump(data[i:i + 500000], f, ensure_ascii=False, indent=4)
    print('done')


def get_node_paper():
    """
    从dblp_v14.json中提取paper的信息，包括：
        title, abstract, year, keywords, doi
    :return:
    """
    dblp_file_path = 'data'
    dblp_file_list = os.listdir(dblp_file_path)

    paper_id2info = dict()

    for file in tqdm(dblp_file_list):
        with open(f'{dblp_file_path}/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for paper in data:
            paper_id = paper['id']
            title = paper['title']
            year = paper['year']
            # abstract = paper['abstract']
            # keywords = paper['keywords']
            doi = paper['doi']
            paper_id2info[paper_id] = {'title': title,
                                       'year': year,
                                       # 'abstract': abstract,
                                       # 'keywords': keywords,
                                       'doi': doi}

    # save
    with open('graph/node/paper_id2info.json', 'w', encoding='utf-8') as f:
        json.dump(paper_id2info, f, ensure_ascii=False, indent=4)


def get_node_author():
    """
    从dblp_v14.json中提取author的信息，包括：
        name
    :return:
    """
    dblp_file_path = 'data'
    dblp_file_list = os.listdir(dblp_file_path)

    author_id2info = dict()
    org_name2index = dict()
    org_index = 0

    for file in tqdm(dblp_file_list):
        with open(f'{dblp_file_path}/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for paper in data:
            authors = paper['authors']
            for author in authors:
                author_id = author['id']
                if author_id == '':
                    continue
                name = author['name']
                org_name = author['org']
                author_id2info[author_id] = {'name': name}
                if org_name != '' and org_name not in org_name2index:
                    org_name2index[org_name] = org_index
                    org_index += 1

    # save
    with open('graph/node/author_id2info.json', 'w', encoding='utf-8') as f:
        json.dump(author_id2info, f, ensure_ascii=False, indent=4)
    with open('graph/node/org_name2index.json', 'w', encoding='utf-8') as f:
        json.dump(org_name2index, f, ensure_ascii=False, indent=4)


def get_node_venue_fos():
    """
    从dblp_v14.json中提取venue和fos的信息，包括：
        venue, fos
    :return:
    """
    dblp_file_path = 'data'
    dblp_file_list = os.listdir(dblp_file_path)

    venue_name2index = dict()
    venue_index = 0
    fos_name2index = dict()
    fos_index = 0

    for file in tqdm(dblp_file_list):
        with open(f'{dblp_file_path}/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for paper in data:
            try:
                venue = paper['venue']['raw']
                if venue not in venue_name2index:
                    venue_name2index[venue] = venue_index
                    venue_index += 1
            except KeyError:
                pass

            try:
                fos_list = paper['fos']
                for fos in fos_list:
                    fos_name = fos['name']
                    if fos_name not in fos_name2index:
                        fos_name2index[fos_name] = fos_index
                        fos_index += 1
            except KeyError:
                pass

    # save
    with open('graph/node/venue_name2index.json', 'w', encoding='utf-8') as f:
        json.dump(venue_name2index, f, ensure_ascii=False, indent=4)
    with open('graph/node/fos_name2index.json', 'w', encoding='utf-8') as f:
        json.dump(fos_name2index, f, ensure_ascii=False, indent=4)


def get_link_author2paper():
    """
    从dblp_v14.json中提取author和paper的关系，包括：
        author -> paper.md
    :return:
    """
    dblp_file_path = 'data'
    dblp_file_list = os.listdir(dblp_file_path)

    author_id2paper_id = defaultdict(list)

    for file in tqdm(dblp_file_list):
        with open(f'{dblp_file_path}/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for paper in data:
            paper_id = paper['id']
            authors = paper['authors']
            year = paper['year']
            for author in authors:
                author_id = author['id']
                author_id2paper_id[author_id].append({'paper_id': paper_id, 'year': year})

    # save
    with open('graph/link/author_id2paper_id.json', 'w', encoding='utf-8') as f:
        json.dump(author_id2paper_id, f, ensure_ascii=False, indent=4)


def get_link_paper2venue_fos():
    """
    从dblp_v14.json中提取paper和venue, fos的关系，包括：
        paper.md -> venue, fos
    :return:
    """
    dblp_file_path = 'data'
    dblp_file_list = os.listdir(dblp_file_path)

    venue2paper_id = defaultdict(list)
    fos2paper_id = defaultdict(list)

    # load venue_name2index
    with open('graph/node/venue_name2index.json', 'r', encoding='utf-8') as f:
        venue_name2index = json.load(f)
    # load fos_name2index
    with open('graph/node/fos_name2index.json', 'r', encoding='utf-8') as f:
        fos_name2index = json.load(f)

    for file in tqdm(dblp_file_list):
        with open(f'{dblp_file_path}/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for paper in data:
            paper_id = paper['id']

            # add
            try:
                venue = paper['venue']['raw']
                venue2paper_id[venue_name2index[venue]].append(paper_id)
            except KeyError:
                pass

            try:
                fos_list = paper['fos']
                for fos in fos_list:
                    fos_name = fos['name']
                    fos_w = fos['w']
                    fos2paper_id[fos_name2index[fos_name]].append({'paper_id': paper_id, 'w': fos_w})
            except KeyError:
                pass

    # save
    with open('graph/link/venue2paper_id.json', 'w', encoding='utf-8') as f:
        json.dump(venue2paper_id, f, ensure_ascii=False, indent=4)
    with open('graph/link/fos2paper_id.json', 'w', encoding='utf-8') as f:
        json.dump(fos2paper_id, f, ensure_ascii=False, indent=4)


def get_link_author2org():
    """
    从dblp_v14.json中提取author和org的关系，包括：
        author -> org
    :return:
    """
    dblp_file_path = 'data'
    dblp_file_list = os.listdir(dblp_file_path)

    author_id2org_name = defaultdict(dict)

    # load org_name2index
    with open('graph/node/org_name2index.json', 'r', encoding='utf-8') as f:
        org_name2index = json.load(f)

    for file in tqdm(dblp_file_list):
        with open(f'{dblp_file_path}/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for paper in data:
            authors = paper['authors']
            year = paper['year']
            for author in authors:
                author_id = author['id']
                org_name = author['org']
                if org_name != '':
                    if org_name not in author_id2org_name[author_id]:
                        author_id2org_name[author_id][org_name2index[org_name]] = [year]
                    else:
                        author_id2org_name[author_id][org_name2index[org_name]].append(year)

    # save
    with open('graph/link/author_id2org_name.json', 'w', encoding='utf-8') as f:
        json.dump(author_id2org_name, f, ensure_ascii=False, indent=4)


def get_link_paper2paper():
    """
    从dblp_v14.json中提取paper和paper的关系，包括：
        paper.md -> paper.md
    :return:
    """
    dblp_file_path = 'data'
    dblp_file_list = os.listdir(dblp_file_path)

    paper_id2reference = dict()

    for file in dblp_file_list:
        with open(f'{dblp_file_path}/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for paper in tqdm(data, desc=file):
            paper_id = paper['id']
            if 'references' in paper:
                references = paper['references']
                year = paper['year']
                paper_id2reference[paper_id] = {'year': year, 'references': references}

    # save
    logging.info('num of paper_id2reference: {}'.format(len(paper_id2reference)))
    with open('graph/link/paper_id2reference.json', 'w', encoding='utf-8') as f:
        json.dump(paper_id2reference, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # data_cut()
    # get_node_paper()
    # get_node_author()
    # get_node_venue_fos()
    # get_link_author2paper()
    # get_link_paper2venue_fos()
    # get_link_author2org()
    get_link_paper2paper()
