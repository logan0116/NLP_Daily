#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：Daily_NLP 
@File    ：4_inf_extract.py
@IDE     ：PyCharm 
@Author  ：Logan
@Date    ：2023/11/26 下午9:52 
"""
import json
import sqlite3
import time
# import fitz
import os


def get_info(cursor):
    """
    从数据库获取所有的未read的title和abstract
    :return:
    """
    # 从数据库获取所有的未read的title和abstract
    cursor.execute('SELECT id, title, abstract, pdf_path FROM papers  WHERE deal_status = TRUE')
    info_list = cursor.fetchall()
    id_list = [info[0] for info in info_list]
    title_list = [info[1] for info in info_list]
    abstract_list = [info[2] for info in info_list]
    pdf_path_list = [info[3] for info in info_list]

    return id_list, title_list, abstract_list, pdf_path_list


def get_script_save_path():
    """
    获取下载路径
    :return:
    """
    local_time = time.strftime("%Y-%m-%d", time.localtime())
    script_save_path = '../script/{}'.format(local_time)
    # mkdir
    if not os.path.exists(script_save_path):
        os.mkdir(script_save_path)
    return script_save_path


def save_title_abstract(title_list, abstract_list, script_save_path):
    """
    保存title和abstract
    :param title_list:
    :param abstract_list:
    :param script_save_path:
    :return:
    """
    title_abstract_list = []
    for title, abstract in zip(title_list, abstract_list):
        title_abstract_list.append({'title': title, 'abstract': abstract})

    with open(os.path.join(script_save_path, 'inputs.json'), 'w', encoding='utf-8') as f:
        json.dump(title_abstract_list, f, ensure_ascii=False, indent=4)


# def get_image_from_pdf(pdf_path_list, script_save_path):
#     """
#     从pdf中提取图片
#     :param pdf_path_list:
#     :param script_save_path:
#     :return:
#     """
#     for pdf_index, pdf_path in enumerate(pdf_path_list):
#         images_save_path = os.path.join(script_save_path, 'images_{}'.format(pdf_index + 1))
#         if not os.path.exists(images_save_path):
#             os.mkdir(images_save_path)
#         doc = fitz.open(pdf_path)
#         lenXREF = doc.xref_length()
#
#         image_index = 0
#         for xref in range(1, lenXREF):
#             if doc.xref_get_key(xref, "Subtype")[1] != "/Image":  # not an image
#                 continue
#
#             imgdict = doc.extract_image(xref)
#             imgdata = imgdict["image"]  # image data
#             imgext = imgdict["ext"]  # image extension
#
#             image_index += 1
#             imgname = os.path.join(images_save_path, 'image_{}.{}'.format(image_index, imgext))
#             ofile = open(imgname, "wb")
#             ofile.write(imgdata)
#             ofile.close()
#
#         print(f"Image saved at {images_save_path}")


def update_deal_read_status(cursor, id_list):
    """
    deal_status = FALSE
    if_read = TRUE
    :param cursor:
    :param id_list:
    :return:
    """
    for id_ in id_list:
        cursor.execute("UPDATE papers SET deal_status = FALSE, if_read = TRUE WHERE id = ?", (id_,))


def main():
    # database
    # 连接到 SQLite 数据库
    conn = sqlite3.connect('../mydatabase.db')
    # 创建一个 Cursor:
    cursor = conn.cursor()
    # 创建一个路径，用于存放提取的信息
    script_save_path = get_script_save_path()
    # 从数据库获取所有deal_status为TRUE的title和abstract和pdf_path
    id_list, title_list, abstract_list, pdf_path_list = get_info(cursor)
    # 保存title和abstract
    save_title_abstract(title_list, abstract_list, script_save_path)
    # # get image from pdf
    # get_image_from_pdf(pdf_path_list, script_save_path)
    # 更新数据库
    print('Start updating database...')
    update_deal_read_status(cursor, id_list)
    print('Done.')
    cursor.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
