#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：Daily_NLP 
@File    ：2_paper_screen.py
@IDE     ：PyCharm 
@Author  ：Logan
@Date    ：2023/11/26 下午5:36 
"""

import sqlite3
import torch
from transformers import AutoTokenizer, AutoModel
from collections import Counter


def load_title_abstract(cursor):
    """
    从数据库获取所有的未read的title和abstract
    :return:
    """

    # 从数据库获取所有的未read的title和abstract
    cursor.execute('SELECT title, abstract FROM papers WHERE if_read = FALSE')
    title_abstract_list = cursor.fetchall()

    return title_abstract_list


def get_embedding(sentences, model, tokenizer):
    # Tokenize sentences
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt', max_length=512)
    input_ids = encoded_input['input_ids'].cuda()
    attention_mask = encoded_input['attention_mask'].cuda()
    token_type_ids = encoded_input['token_type_ids'].cuda()
    # Compute token embeddings
    with torch.no_grad():
        model_output = model(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        # Perform pooling. In this case, cls pooling.
        sentence_embeddings = model_output.pooler_output
    # normalize embeddings
    sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
    return sentence_embeddings


def get_top_k(source: torch.Tensor, target: torch.Tensor, top_k: int = 5):
    # sim: [source_num, target_num]
    sim = torch.matmul(source, target.T)
    sim = sim.T
    # get index: [target_num, source_num]
    _, sim_index = torch.sort(sim, descending=True)
    sim_index = sim_index.cpu().numpy()
    # index: [target_num, top_k]
    sim_index = sim_index[:, :top_k]
    sim_index = sim_index.tolist()
    index_count = []
    for i in sim_index:
        index_count.extend(i)
    index_count = dict(Counter(index_count))
    print(index_count)
    index_count = sorted(index_count.items(), key=lambda x: x[1], reverse=True)
    index_list_top_k = [i[0] for i in index_count[:top_k]]
    return index_list_top_k


def update_deal_status(cursor, title_list_top_k):
    """
    更新deal_status状态
    :param cursor:
    :param title_list_top_k:
    :return:
    """
    for title in title_list_top_k:
        cursor.execute("UPDATE papers SET deal_status = TRUE WHERE title = ?", (title,))


def main():
    # database
    # 连接到 SQLite 数据库
    conn = sqlite3.connect('mydatabase.db')
    # 创建一个 Cursor:
    cursor = conn.cursor()

    # Load model from HuggingFace Hub
    print('Loading model...')
    tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-large-en-v1.5')
    model = AutoModel.from_pretrained('BAAI/bge-large-en-v1.5')
    model.cuda()
    model.eval()
    print('Model loaded.')

    target_sentences = [
        'Exploring the latest advancements in large language model fine-tuning, focusing on parameter-efficient methods and their effectiveness in various NLP tasks.',
        'Investigating the role of prompt engineering in enhancing the performance of large language models, including the development of hard and soft prompts for context-specific applications.',
        'Analyzing in-context learning strategies within large language models to improve understanding and application of complex language tasks.',
        'Exploring domain-specific knowledge graph construction techniques and their impact on information retrieval and data integration.',
        'Advancements in knowledge extraction and fusion for building comprehensive knowledge graphs, emphasizing on representation learning and data accuracy.',
        'Investigating the integration of large language models with knowledge graphs for enhanced natural language understanding and reasoning capabilities.'
    ]

    # 从数据库获取所有的未read的title和abstract
    title_abstract_list = load_title_abstract(cursor)
    # 获取source_embedding
    print('Getting source embedding...')
    source_sentence_embeddings = get_embedding([title + '.' + abstract for title, abstract in title_abstract_list],
                                               model, tokenizer)
    # 获取target_embedding
    print('Getting target embedding...')
    target_sentence_embeddings = get_embedding(target_sentences, model, tokenizer)
    # 获取top_k
    print('Getting top_k...')
    index_list_top_k = get_top_k(source_sentence_embeddings, target_sentence_embeddings, top_k=5)
    # 1.更新deal_status状态
    print('Updating deal_status...')
    title_list_top_k = [title_abstract_list[i][0] for i in index_list_top_k]
    update_deal_status(cursor, title_list_top_k)
    print('Done.')
    cursor.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
