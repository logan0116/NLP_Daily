#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：Daily_NLP 
@File    ：1_paper_crawler.py
@IDE     ：PyCharm 
@Author  ：Logan
@Date    ：2023/11/26 下午3:38 
"""

import requests
from bs4 import BeautifulSoup
from texttable import Texttable
import sqlite3
import time


def print_table(table: list, header: list):
    """
    打印表格
    :param table:
    :return:
    """
    t = Texttable()
    t.add_row(header)
    for inf in table:
        t.add_row(inf)
    print(t.draw())


def get_author_info(soup):
    author_dict = {}  # author:link
    author_list = []

    # authors
    for item in soup.select('.list-authors'):
        author_list_temp = []
        for author in item.select('a'):
            author_link = author['href']
            author_name = author.string.strip()
            author_dict[author_name] = author_link
            author_list_temp.append(author_name)
        author_list.append(author_list_temp)

    return author_dict, author_list


def get_pdf_link(soup):
    # <a href="/abs/2311.12798" title="Abstract">arXiv:2311.12798</a>
    # <a href="/pdf/2311.12798" title="Download PDF">pdf</a>
    # <a href="/format/2311.12798" title="Other formats">other</a>
    pdf_link_list = []
    for item in soup.select('.list-identifier'):
        pdf_link = item.select('a')[1]['href']
        pdf_link_list.append(f'Link: https://arxiv.org{pdf_link}')
    return pdf_link_list


def get_title(soup):
    # <div class="list-title mathjax">
    # <span class="descriptor">Title:</span> Frequency Analysis with Multiple Kernels and Complete Dictionary
    # </div>

    title_list = []
    for item in soup.select('.list-title.mathjax'):
        title = item.text.strip()
        if 'Title:' in title:
            title = title.replace('Title:', '').strip()
        title_list.append(title)
    return title_list


def get_abstract(soup):
    abstract_list = []
    for item in soup.select('p.mathjax'):
        abstract = item.get_text(separator=' ', strip=True)
        abstract_list.append(abstract)
    return abstract_list


def main():
    # arXiv的NLP相关论文列表的URL（这里需要替换为实际的URL）
    url = 'https://arxiv.org/list/cs/new'

    # 发送请求
    response = requests.get(url)
    response.raise_for_status()  # 确保请求成功

    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取论文标题
    title_list = get_title(soup)

    # 获取论文作者
    author_dict, authors_list = get_author_info(soup)

    # 获取论文PDF链接
    pdf_link_list = get_pdf_link(soup)

    # 获取论文摘要
    abstract_list = get_abstract(soup)

    # 打印表格
    print_table(zip([i + 1 for i in range(len(title_list))], title_list, pdf_link_list),
                header=['Index', 'Title', 'PDF Link'])

    # 将数据插入数据库
    insert_data(title_list, abstract_list, pdf_link_list, authors_list, author_dict)


def insert_data(title_list, abstract_list, pdf_link_list, authors_list, author_dict):
    """
    将数据插入数据库
    :param title_list:
    :param abstract_list:
    :param pdf_link_list:
    :param authors_list:
    :param author_dict:
    :return:
    """
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    local_date = time.strftime("%Y-%m-%d", time.localtime())

    for title, abstract, pdf_link, authors in zip(title_list, abstract_list, pdf_link_list, authors_list):
        # 检查title是否已存在
        cursor.execute("SELECT id FROM papers WHERE title = ?", (title,))
        paper_record = cursor.fetchone()
        if paper_record:
            paper_id = paper_record[0]
        else:
            # 插入新的论文
            cursor.execute(
                "INSERT INTO papers (title, abstract, pdf_url, pdf_path, date, deal_status, if_read) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title, abstract, pdf_link, '', local_date, False, False))
            paper_id = cursor.lastrowid

        for author in authors:
            # 检查作者是否已存在
            cursor.execute("SELECT id FROM authors WHERE name = ?", (author,))
            author_record = cursor.fetchone()
            if author_record:
                author_id = author_record[0]
            else:
                # 插入新的作者
                cursor.execute("INSERT INTO authors (name, info_url) VALUES (?, ?)",
                               (author, author_dict[author]))
                author_id = cursor.lastrowid

            # 插入作者和论文的关联
            cursor.execute("INSERT INTO paper_author (author_id, paper_id) VALUES (?, ?)",
                           (author_id, paper_id))

    # 关闭 Cursor:
    cursor.close()

    # 提交事务:
    conn.commit()

    # 关闭 Connection:
    conn.close()


if __name__ == '__main__':
    main()
