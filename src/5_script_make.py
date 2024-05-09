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


def text_generation(each_prompt: list):
    """
    example

    curl https://api.openai.com/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -d '{
        "model": "No models available",
        "messages": [
          {
            "role": "system",
            "content": "You are a helpful assistant."
          },
          {
            "role": "user",
            "content": "Hello!"
          }
        ]
      }'

    :param each_prompt:
    :return:
    """
    model_engine = "gpt-3.5-turbo"
    openai.api_key = ""

    start_time = time.time()
    completions = openai.ChatCompletion.create(
        model=model_engine,
        messages=each_prompt
    )
    end_time = time.time()
    message = completions.choices[0].message.content
    print('time: ', end_time - start_time)
    print(message)
    if end_time - start_time < 20:
        time.sleep(20 - (end_time - start_time))
    return message


def text_generation_deepseek_v2(each_prompt: list):
    """
    example

    curl https://api.openai.com/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -d '{
        "model": "No models available",
        "messages": [
          {
            "role": "system",
            "content": "You are a helpful assistant."
          },
          {
            "role": "user",
            "content": "Hello!"
          }
        ]
      }'

    :param each_prompt:
    :return:
    """

    client = OpenAI(api_key="", base_url="https://api.deepseek.com/")
    start_time = time.time()
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=each_prompt
    )
    end_time = time.time()
    message = response.choices[0].message.content
    print('time: ', end_time - start_time)
    print(message)
    if end_time - start_time < 20:
        time.sleep(20 - (end_time - start_time))
    return message


def make_script():
    local_time = time.strftime("%Y-%m-%d", time.localtime())
    script_text_input_path = '../script/{}/inputs.json'.format(local_time)

    with open(script_text_input_path, 'r', encoding='utf-8') as f:
        paper_info_list = json.load(f)

    response_list = []

    for title_abstract in paper_info_list:
        each_prompt = [{"role": "system", "content": """ \
        我这里有一篇自然语言处理领域论文的标题和摘要。 \
        针对这篇篇论文，请用中文给出一段200字左右的精炼且吸引人的总结，突出其主要发现及其重要性。 \
        这些总结能够适合普通观众阅读，并能激发他们对这些主题的兴趣。 \
        另外请注意，这些总结应该是独立的，不应该包含任何关于论文的标题或摘要中没有提到的信息。 \
        同时不要用太长的句子，以免造成阅读困难，每一句话请尽量不要超过70个字。  
        """},
                       {"role": "user", "content": title_abstract['title'] + '\n' + title_abstract['abstract']},
                       {"role": "assistant", "content": ''}]
        message = text_generation_deepseek_v2(each_prompt)
        response_list.append(message)

    title_list = [title_abstract['title'] for title_abstract in paper_info_list]
    url_list = [title_abstract['pdf_url'] for title_abstract in paper_info_list]

    start = '嗨，欢迎来到今天的NLP资讯速递，让我们看看又有哪些最新的研究。\n\n'
    end = '以上是今天所有的内容，如果您对今天讨论的任何主题感兴趣，不妨深入阅读相关论文，以获取更全面的了解。祝你今天有个好心情~ '

    script_text_output_path = '../script/{}/outputs.txt'.format(local_time)
    with open(script_text_output_path, 'w', encoding='utf-8') as f:
        f.write(start)
        for index, (title, response) in enumerate(zip(title_list, response_list)):
            f.write('## '.format(index + 1) + title + '\n')
            f.write(response + '\n')
            f.write('Pdf Link: ' + url_list[index] + '\n\n')
        f.write(end + '\n')


if __name__ == '__main__':
    make_script()
