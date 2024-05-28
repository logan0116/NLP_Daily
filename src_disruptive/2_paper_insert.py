import json
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3


def get_disrupt_distribution(time_point):
    """
    获取颠覆性分布
    :param time_point:
    :return:
    """
    # get indicator
    with open('graph/indicator/paper_id2disrupt_{}.json'.format(time_point), 'r') as f:
        paper_id2disrupt = json.load(f)
    value_list = list(paper_id2disrupt.values())
    # draw
    sns.set(style="whitegrid")
    sns.histplot(value_list, bins=100, kde=True)
    plt.xlabel('disrupt')
    plt.ylabel('count')
    plt.title('disrupt distribution')
    plt.savefig('graph/indicator/disrupt_distribution_{}.png'.format(time_point))


def paper_screen(time_point):
    """
    paper_screen
    :return:
    """
    with open('graph/indicator/paper_id2disrupt_{}.json'.format(time_point), 'r') as f:
        paper_id2disrupt = json.load(f)
    value_list = list(paper_id2disrupt.values())
    value_list = [value[0] for value in value_list]
    # 3 sigma
    mean = sum(value_list) / len(value_list)
    std = (sum([(value - mean) ** 2 for value in value_list]) / len(value_list)) ** 0.5
    threshold = mean + 3 * std
    print('mean', mean)
    print('std', std)
    print('threshold', threshold)
    # screen
    paper_id2disrupt_screen = {}
    for paper_id, (disrupt, num_cited) in paper_id2disrupt.items():
        if disrupt > threshold:
            paper_id2disrupt_screen[paper_id] = (disrupt, num_cited)

    print('screen', len(paper_id2disrupt_screen))

    return paper_id2disrupt_screen


def get_paper_id2info(paper_id2disrupt_screen):
    """
    获取paper_id2info
    :return:
    """
    with open('graph/node/paper_id2info.json', 'r') as f:
        paper_id2info = json.load(f)

    paper_id2info_screen = {}
    for paper_id, (disrupt, num_cited) in paper_id2disrupt_screen.items():
        if paper_id in paper_id2info:
            paper_info = paper_id2info[paper_id]
            paper_info['disrupt'] = disrupt
            paper_info['num_cited'] = num_cited
            paper_id2info_screen[paper_id] = paper_info

    return paper_id2info_screen


def insert_data(paper_id2info_screen, time_point):
    """
    插入数据
        title
        year
        doi
        disrupt
    :param paper_id2info_screen:
    :param time_point:
    :return:
    """

    conn = sqlite3.connect('../dblp_cite_disrupt.db')
    cursor = conn.cursor()
    table_name = f'papers_{time_point}'
    for paper_id, paper_info in paper_id2info_screen.items():
        cursor.execute(
            """insert into {} (
            paper_id, 
            title, 
            year, 
            doi, 
            disrupt,
            num_cited,
            deal_status, 
            if_read) values (?, ?, ?, ?, ?, ?, ?, ?)""".format(table_name),
            (paper_id,
             paper_info['title'],
             paper_info['year'],
             paper_info['doi'],
             paper_info['disrupt'],
             paper_info['num_cited'],
             False,
             False)
        )
    conn.commit()
    conn.close()


def main(time_point):
    paper_id2disrupt_screen = paper_screen(time_point)
    paper_id2info_screen = get_paper_id2info(paper_id2disrupt_screen)
    # write2database
    insert_data(paper_id2info_screen, time_point)


if __name__ == '__main__':
    # get_disrupt_distribution(2022)
    for time_point in range(2000, 2023):
        main(time_point)
