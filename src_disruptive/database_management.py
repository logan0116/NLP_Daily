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
conn = sqlite3.connect('../dblp_cite_disrupt_2022_3_sigma.db')

# 创建一个 Cursor:
cursor = conn.cursor()

# 删除现有的表（如果存在）
cursor.execute('DROP TABLE IF EXISTS papers')

# 创建 总文献表
cursor.execute('''CREATE TABLE papers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_id TEXT NOT NULL,
                    title TEXT,
                    year INTEGER,
                    doi TEXT,
                    disrupt FLOAT,
                    deal_status BOOLEAN,
                    if_read BOOLEAN
                )''')

# 关闭 Cursor:
cursor.close()

# 提交事务:
conn.commit()

# 关闭 Connection:
conn.close()
