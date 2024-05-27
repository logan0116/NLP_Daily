import json
from collections import defaultdict
from tqdm import tqdm


def get_cite_info():
    """
    将引用信息转换为neighbor
    :return:
    """
    # 读取引用信息
    node2neighbor_left = defaultdict(set)  # local2past
    node2neighbor_right = defaultdict(set)  # local2future

    with open('graph/link/paper_id2reference.json', 'r') as f:
        paper_id2reference = json.load(f)

    for paper_id, reference_list in tqdm(paper_id2reference.items(), total=len(paper_id2reference)):
        for reference in reference_list:
            node2neighbor_left[paper_id].add(reference)
            node2neighbor_right[reference].add(paper_id)

    # 保存
    # set2list
    node2neighbor_left = {k: list(v) for k, v in node2neighbor_left.items()}
    node2neighbor_right = {k: list(v) for k, v in node2neighbor_right.items()}
    # save
    with open('graph/link/paper_id2neighbor_left.json', 'w') as f:
        json.dump(node2neighbor_left, f)
    with open('graph/link/paper_id2neighbor_right.json', 'w') as f:
        json.dump(node2neighbor_right, f)
    print('save successfully.')


if __name__ == '__main__':
    get_cite_info()
