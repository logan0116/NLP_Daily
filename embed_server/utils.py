#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：fd_backend_alarm_match 
@File    ：utils.py
@IDE     ：PyCharm 
@Author  ：Logan
@Date    ：2023/11/29 下午4:15 
"""
import os
import torch
from tqdm import tqdm


def get_embed(sentences, model, tokenizer):
    """
    对句子进行表征
    :param sentences:
    :param model:
    :param tokenizer:
    :return:
    """
    # Tokenize sentences
    encoded_input = tokenizer(sentences,
                              padding=True,
                              truncation=True,
                              return_tensors='pt',
                              max_length=512)
    input_ids = encoded_input['input_ids']
    attention_mask = encoded_input['attention_mask']
    token_type_ids = encoded_input['token_type_ids']
    # Compute token embeddings

    batch_size = 16
    sentence_embeddings = []
    for i in tqdm(range(0, len(input_ids), batch_size)):
        with torch.no_grad():
            input_ids_temp = input_ids[i:i + batch_size].cuda()
            attention_mask_temp = attention_mask[i:i + batch_size].cuda()
            token_type_ids_temp = token_type_ids[i:i + batch_size].cuda()

            model_output = model(input_ids=input_ids_temp,
                                 attention_mask=attention_mask_temp,
                                 token_type_ids=token_type_ids_temp)

            # Perform pooling. In this case, cls pooling.
            model_output = model_output.pooler_output.cpu().numpy().tolist()
            # to list
            sentence_embeddings.extend(model_output)
    # to tensor
    sentence_embeddings = torch.tensor(sentence_embeddings)
    # normalize embeddings
    sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
    return sentence_embeddings


def get_top(source: torch.Tensor, target: torch.Tensor, top_k, top_threshold):
    """
    获取top的index
    :param source:
    :param target:
    :param top_k:
    :param top_threshold:
    :return:
    """
    # sim: [source_num, target_num]
    sim = torch.matmul(source, target.T)
    # mean sim 【target_num]
    sim = sim.mean(dim=0)
    # get index: [target_num]
    _, sim_index = torch.sort(sim, descending=True)
    # top_k_threshold
    sim = sim.cpu().numpy().tolist()
    sim_index = sim_index.cpu().numpy().tolist()
    top_k_threshold = len([i for i in sim if i > top_threshold])
    # index: [target_num]
    sim_index = sim_index[:min(top_k, top_k_threshold)]
    return sim_index, [sim[i] for i in sim_index]
