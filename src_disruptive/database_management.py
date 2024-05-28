#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：Daily_NLP 
@File    ：database_management.py
@IDE     ：PyCharm 
@Author  ：Logan
@Date    ：2023/11/26 下午3:30 
"""

import sqlite3

# 连接到 SQLite 数据库
conn = sqlite3.connect('../dblp_cite_disrupt.db')

# 创建一个 Cursor:
cursor = conn.cursor()

# 删除现有的表（如果存在）
for time in range(2000, 2023):
    table_name = f'papers_{time}'
    cursor.execute('DROP TABLE IF EXISTS {}'.format(table_name))

for time in range(2000, 2023):
    # 创建 总文献表
    table_name = f'papers_{time}'
    cursor.execute('''CREATE TABLE {} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        paper_id TEXT NOT NULL,
                        title TEXT,
                        year INTEGER,
                        doi TEXT,
                        disrupt FLOAT,
                        num_cited INTEGER,
                        deal_status BOOLEAN,
                        if_read BOOLEAN
                    )'''.format(table_name))

# 关闭 Cursor:
cursor.close()

# 提交事务:
conn.commit()

# 关闭 Connection:
conn.close()
