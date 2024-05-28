#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：Daily_NLP 
@File    ：5_script_make.py
@IDE     ：PyCharm 
@Author  ：Logan
@Date    ：2023/11/27 上午12:10 
"""

from openai import OpenAI
import openai
import time
import json
from utils import text_generation


def load_prompt():
    # load prompt

    # 研究问题
    with open('prompt/system_prompt_research_question.txt', 'r', encoding='utf-8') as f:
        prompt_research_question = f.read()
    # 研究gap
    with open('prompt/system_prompt_research_gap.txt', 'r', encoding='utf-8') as f:
        prompt_research_gap = f.read()
    # 研究内容及方法
    with open('prompt/system_prompt_research_content.txt', 'r', encoding='utf-8') as f:
        prompt_research_content = f.read()
    # 介绍
    with open('prompt/system_prompt_introduce.txt', 'r', encoding='utf-8') as f:
        prompt_introduce = f.read()

    return {'research_question': prompt_research_question,
            'research_gap': prompt_research_gap,
            'research_content': prompt_research_content,
            'introduce': prompt_introduce}


def export_script(title_list, response_list, url_list, local_time):
    """
    输出脚本
    :param title_list:
    :param response_list:
    :param url_list:
    :param local_time:
    :return:
    """
    start = '嗨，欢迎来到今天的NLP资讯速递，让我们看看又有哪些最新的研究。\n\n'
    end = '以上是今天所有的内容，如果您对今天讨论的任何主题感兴趣，不妨深入阅读相关论文，以获取更全面的了解。祝你今天有个好心情~ '

    script_text_output_path = '../script/{}/outputs.txt'.format(local_time)
    with open(script_text_output_path, 'w', encoding='utf-8') as f:
        f.write(start)
        for index, (title, response, url) in enumerate(zip(title_list, response_list, url_list)):
            f.write('## '.format(index + 1) + title + '\n')
            # research question
            f.write('**研究问题**：' + response['research_question'] + '\n')
            # research gap
            f.write('**研究缺口**：' + response['research_gap'] + '\n')
            # research content
            f.write('**研究内容及方法**：' + response['research_content'] + '\n')
            # 介绍
            f.write(response['introduce'] + '\n')
            # pdf link
            f.write('Pdf Link: ' + url + '\n\n')
        f.write(end + '\n')


def make_prompt_research(prompt, title, abstract, context):
    each_prompt = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Title: {title}\nAbstract: {abstract}\nContext: {context}"},
        {"role": "assistant", "content": ''}
    ]
    return each_prompt


def make_prompt_introduce(prompt, title, abstract, context, research_question, research_gap, research_content):
    each_prompt = [
        {"role": "system", "content": prompt},
        {"role": "user",
         "content": f"Title: {title}\nAbstract: {abstract}\nContext: {context}\n\nResearch Question: {research_question}\nResearch Gap: {research_gap}\nResearch Content: {research_content}"},
        {"role": "assistant", "content": ''}
    ]
    return each_prompt


def make_script():
    local_time = time.strftime("%Y-%m-%d", time.localtime())
    script_text_input_path = '../script/{}/inputs.json'.format(local_time)

    with open(script_text_input_path, 'r', encoding='utf-8') as f:
        paper_info_list = json.load(f)
    response_list = []

    # load prompt
    prompt_dict = load_prompt()  # research question, research gap, research content, introduce

    for title_abstract in paper_info_list:
        # response
        response = {}
        for prompt, prompt_context in prompt_dict.items():
            title, abstract, context = title_abstract['title'], title_abstract['abstract'], title_abstract['context']
            if prompt in ['research_question', 'research_gap', 'research_content']:
                each_prompt = make_prompt_research(prompt_context, title, abstract, context)
            else:
                each_prompt = make_prompt_introduce(prompt_context, title, abstract, context,
                                                    response['research_question'], response['research_gap'],
                                                    response['research_content'])

            message = text_generation(each_prompt, mode='deepseek')
            response[prompt] = message.strip()
        response_list.append(response)

    title_list = [title_abstract['title'] for title_abstract in paper_info_list]
    url_list = [title_abstract['pdf_url'] for title_abstract in paper_info_list]

    export_script(title_list, response_list, url_list, local_time)
    print('Script has been generated successfully!')


if __name__ == '__main__':
    make_script()
