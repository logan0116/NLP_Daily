#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：fd_backend_alarm_match 
@File    ：main.py
@IDE     ：PyCharm 
@Author  ：Logan
@Date    ：2023/11/29 下午4:11 
"""
# fastapi
import uvicorn
from fastapi import FastAPI
# model
from transformers import AutoTokenizer, AutoModel
# base
import os
import numpy as np
import torch
import json
# local
from parser import parameter_parser
from model import GetTopReqItem, GetTopResItem
from utils import get_embed, get_top

TRANSFORMER_OFFLINE = 1

# 全局变量
args = parameter_parser()
print('load model...')
tokenizer = AutoTokenizer.from_pretrained(args.embed_model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(args.embed_model_path, trust_remote_code=True).half()
model.cuda()
model.eval()
print('load model successfully.')
app = FastAPI()


@app.post("/api/get_top")
async def get_top_index(search_info: GetTopReqItem):
    """
    request body:
        source: List[str]
        target: List[str]
        top_k: int = 5
        top_threshold: float = 0.75
    """

    s_list = search_info.source
    t_list = search_info.target
    top_k = search_info.top_k
    top_threshold = search_info.top_threshold

    source_emb = get_embed(s_list, model, tokenizer)
    target_emb = get_embed(t_list, model, tokenizer)

    try:
        # 获取top的index
        top_index, top_sim_score = get_top(source_emb, target_emb, top_k=top_k, top_threshold=top_threshold)
        print(top_index)
        print(top_sim_score)
        # 释放显存
        del source_emb, target_emb
        return GetTopResItem(code=200, msg='Success', data=top_index)
    except Exception as e:
        del source_emb, target_emb
        return GetTopResItem(code=500, msg=str(e), data=[])


if __name__ == '__main__':
    uvicorn.run(app=app,
                host='0.0.0.0',
                port=9001,
                workers=1)
