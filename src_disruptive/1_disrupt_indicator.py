import json
from tqdm import tqdm
import json
from collections import defaultdict
from tqdm import tqdm


def get_neighbors(paper_id2reference, time_point):
    """
    将引用信息转换为neighbor
    :return:
    """
    # 读取引用信息
    node2neighbor_left = defaultdict(set)  # local2past
    node2neighbor_right = defaultdict(set)  # local2future

    for paper_id, reference_info in tqdm(paper_id2reference.items(), total=len(paper_id2reference)):
        paper_time = reference_info['year']
        if paper_time > time_point:
            continue
        reference_list = reference_info['references']
        for reference in reference_list:
            node2neighbor_left[paper_id].add(reference)
            node2neighbor_right[reference].add(paper_id)

    return node2neighbor_left, node2neighbor_right


def disrupt_single(node, node2neighbor_left, node2neighbor_right):
    """
    颠覆性指标
    :param node:
    :param node2neighbor_left:
    :param node2neighbor_right:
    :return:
    """

    if len(node2neighbor_left[node]) == 0 or len(node2neighbor_right[node]) == 0:
        return 0, len(node2neighbor_right[node])

    target_set_1 = node2neighbor_right[node]
    target_set_2 = set()
    for neighbor in node2neighbor_left[node]:
        target_set_2 = target_set_2 | node2neighbor_right[neighbor]

    # ni node in target_set_1 not in target_set_2
    ni = len(target_set_1 - target_set_2)
    # nj node in target_set_2 in target_set_1
    nj = len(target_set_1 & target_set_2)
    # nk node in target_set_2 not in target_set_1
    nk = len(target_set_2 - target_set_1)

    return (ni - nj) / (ni + nj + nk), len(node2neighbor_right[node])


def disrupt(node2neighbor_left, node2neighbor_right, time_point):
    """
    颠覆性指标
    只基于引用网络来做
    :param node2neighbor_left:
    :param node2neighbor_right:
    :return:
    """
    # node_set 并集
    node_set = list(set(node2neighbor_left.keys()) | set(node2neighbor_right.keys()))
    # disrupt
    node2disrupt = {}
    for node in tqdm(node_set, total=len(node_set), desc=str(time_point)):
        node2disrupt[node] = disrupt_single(node, node2neighbor_left, node2neighbor_right)

    return node2disrupt


def main(paper_id2reference, time_point):
    """
    :param time_point:
    :return:
    """
    # get neighbors
    node2neighbor_left, node2neighbor_right = get_neighbors(paper_id2reference, time_point)
    node2disrupt = disrupt(node2neighbor_left, node2neighbor_right, time_point)
    # save disrupt
    with open('graph/indicator/paper_id2disrupt_{}.json'.format(time_point), 'w') as f:
        json.dump(node2disrupt, f)


# if __name__ == '__main__':
#     with open('graph/link/paper_id2reference.json', 'r') as f:
#         paper_id2reference = json.load(f)
#
#     for time_point in range(2000, 2023):
#         main(paper_id2reference, time_point=time_point)

with open('graph/link/paper_id2reference.json', 'r') as f:
    paper_id2reference = json.load(f)
for time_point in range(2000, 2023):

    node2neighbor_left, node2neighbor_right = get_neighbors(paper_id2reference, time_point)
    with open('graph/indicator/paper_id2disrupt_{}.json'.format(time_point), 'r') as f:
        node2disrupt = json.load(f)
    node2disrupt_new = {}
    for node, disrupt in node2disrupt.items():
        if disrupt == 0:
            node2disrupt_new[node] = [0, len(node2neighbor_right[node])]
        else:
            node2disrupt_new[node] = disrupt

    # save
    with open('graph/indicator/paper_id2disrupt_{}.json'.format(time_point), 'w') as f:
        json.dump(node2disrupt_new, f)
